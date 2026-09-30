"""Exercise the local review journey and record browser evidence."""

import argparse
import copy
import hashlib
import json
from pathlib import Path

from playwright.sync_api import sync_playwright


def verify(trial):
    review = trial / "review/index.html"
    manifest = json.loads((trial / "manifest.json").read_text())
    output = trial / "browser-checks"
    output.mkdir(exist_ok=True)
    checks, errors, external = [], [], []

    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page(viewport={"width": 1440, "height": 1100})
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on(
                "request",
                lambda req: (
                    external.append(req.url) if req.url.startswith(("https:", "http:")) else None
                ),
            )
            page.goto(review.as_uri() + "?view=a")
            page.locator("#report h2").wait_for()
            contrast = page.evaluate("""() => {
              const style = getComputedStyle(document.documentElement);
              const canvas = document.createElement('canvas');
              canvas.width = canvas.height = 1;
              const context = canvas.getContext('2d');
              function luminance(token) {
                context.fillStyle = style.getPropertyValue(token).trim();
                context.fillRect(0, 0, 1, 1);
                const values = [...context.getImageData(0, 0, 1, 1).data].slice(0, 3)
                  .map(value => value / 255)
                  .map(value => value <= 0.04045
                    ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4);
                return values[0] * 0.2126 + values[1] * 0.7152 + values[2] * 0.0722;
              }
              function ratio(a, b) {
                const values = [luminance(a), luminance(b)].sort((a, b) => a - b);
                return (values[1] + 0.05) / (values[0] + 0.05);
              }
              return {
                body: ratio('--ink', '--bg'), muted: ratio('--muted', '--bg'),
                button: ratio('--bg', '--brand'), selected: ratio('--ink', '--tint'),
                error: ratio('--error', '--surface'), detail: ratio('--muted', '--surface')
              };
            }""")
            check("Body text contrast at least 7", contrast["body"] >= 7)
            check("Secondary and colored text contrast at least 4.5", min(contrast.values()) >= 4.5)
            check("Simulation scope visible", "simulation" in page.locator("#report").inner_text())
            cells = page.locator("table").first.locator("tbody tr").first.locator("td")
            check("Candidate measured value", cells.nth(0).inner_text().startswith("1\n"))
            check("Current reference value", cells.nth(1).inner_text().startswith("0.3333\n"))
            check("Original reference value", cells.nth(2).inner_text().startswith("0.3333\n"))
            page.screenshot(path=str(output / "prototype-a-desktop.png"), full_page=True)
            page.keyboard.press("Tab")
            check(
                "Skip link available by keyboard",
                page.locator(".skip").evaluate("e => e === document.activeElement"),
            )
            page.keyboard.press("Enter")
            check(
                "Skip link reaches report",
                page.locator("#report").evaluate("e => e === document.activeElement"),
            )

            page.locator("#finding").fill("AUTOMATED CHECK: support is limited to this simulation.")
            page.locator("#next-step").fill("AUTOMATED CHECK: review the actual product task.")
            page.locator("#ease").select_option("3")
            page.get_by_role("button", name="Record this judgment").click()
            check(
                "Judgment can be recorded",
                "1 judgment recorded" in page.locator("#response-count").inner_text(),
            )
            page.get_by_role("button", name="Prototype B", exact=True).click()
            check("Views keep separate answers", page.locator("#finding").input_value() == "")
            page.screenshot(path=str(output / "prototype-b-desktop.png"), full_page=True)
            page.get_by_role("button", name="Prototype A", exact=True).click()
            check(
                "Earlier answer preserved",
                page.locator("#finding").input_value().startswith("AUTOMATED CHECK"),
            )
            page.reload()
            check(
                "Answer survives reload",
                page.locator("#finding").input_value().startswith("AUTOMATED CHECK"),
            )
            page.locator("#finding").fill("AUTOMATED CHECK: edited draft.")
            check(
                "Edited answers require recording again",
                "0 judgments recorded" in page.locator("#response-count").inner_text(),
            )
            page.get_by_role("button", name="Record this judgment").click()

            page.locator("#case").select_option("case-2")
            check("Cases keep separate answers", page.locator("#finding").input_value() == "")
            check(
                "Required failure stays visible",
                "no-force-restart" in page.locator("#report").inner_text(),
            )
            check(
                "Rejected result stays rejected",
                "Lesson rejected" in page.locator("#report").inner_text(),
            )
            page.locator("#case").select_option("case-3")
            text = page.locator("#report").inner_text()
            check("Failed attempt is visible", "Trial failed" in text)
            check(
                "Failed validation needs fresh cases",
                "fresh cases" in text and "Validation consumed: True" in text,
            )
            check("Missing measurements stay missing", "No complete measurements" in text)

            page.get_by_role("button", name="Current report", exact=True).click()
            check(
                "Baseline wording unchanged",
                page.locator(".original").inner_text() == manifest["cases"][2]["original_text"],
            )
            page.get_by_role("button", name="Prototype B", exact=True).click()
            page.set_viewport_size({"width": 390, "height": 844})
            check(
                "Narrow viewport has no page overflow",
                page.evaluate("document.documentElement.scrollWidth <= innerWidth"),
            )
            page.screenshot(path=str(output / "prototype-b-mobile.png"), full_page=True)

            with page.expect_download() as download:
                page.get_by_role("button", name="Download feedback", exact=True).click()
            saved = output / "automated-feedback.json"
            download.value.save_as(saved)
            responses = json.loads(saved.read_text())
            check(
                "Feedback identifies reviewed candidate",
                responses["answers"]["a:case-1"]["candidate_digest"] == manifest["candidates"]["a"],
            )
            check(
                "Feedback identifies reviewed report",
                responses["answers"]["a:case-1"]["report_digest"] == manifest["cases"][0]["digest"],
            )
            check("Feedback retains recorded state", responses["answers"]["a:case-1"]["recorded"])

            page.get_by_text("Inspect the source report", exact=True).click()
            with page.expect_download() as download:
                page.get_by_role("button", name="Download source JSON", exact=True).click()
            source = output / "downloaded-source.json"
            download.value.save_as(source)
            check(
                "Downloaded source matches prepared report",
                json.loads(source.read_text()) == manifest["cases"][2]["report"],
            )

            hostile = copy.deepcopy(manifest)
            marker = (
                '<img src="https://invalid.example/probe" onerror="window.reportExecuted=true">'
            )
            hostile["cases"][0]["report"]["contract"]["contract"]["question"] = marker
            hostile["id"] = "hostile-test"
            probe = browser.new_page()
            probe.on(
                "request",
                lambda req: external.append(req.url) if req.url.startswith("https:") else None,
            )
            probe.add_init_script("window.__TRIAL_OVERRIDE__ = " + json.dumps(hostile) + ";")
            probe.goto(review.as_uri() + "?view=a")
            check(
                "Report markup is shown as text", probe.locator("#report h2").inner_text() == marker
            )
            check(
                "Report markup cannot execute",
                probe.evaluate(
                    "window.reportExecuted !== true && "
                    "document.querySelectorAll('#report img').length === 0"
                ),
            )
            probe.close()

            denied = browser.new_page()
            denied.add_init_script(
                "Storage.prototype.setItem = () => { throw new Error('storage disabled'); };"
            )
            denied.goto(review.as_uri() + "?view=a")
            check(
                "Storage failure has a recovery path",
                "download your feedback" in denied.locator("#feedback-status").inner_text(),
            )
            denied.close()
            corrupt = browser.new_page()
            corrupt.goto(review.as_uri() + "?view=a")
            key = f"productlab-review:{manifest['id']}"
            corrupt.evaluate("key => localStorage.setItem(key, 'broken saved JSON')", key)
            corrupt.reload()
            check(
                "Unreadable saved data is preserved",
                corrupt.evaluate("key => localStorage.getItem(key)", key) == "broken saved JSON",
            )
            check(
                "Unreadable saved data has a download path",
                "download your feedback" in corrupt.locator("#feedback-status").inner_text(),
            )
            corrupt.close()
            check("No page errors", not errors)
            check("No external requests", not external)
        finally:
            browser.close()
    result = {
        "status": "passed",
        "checks": checks,
        "candidate_digests": manifest["candidates"],
        "text_contrast_ratios": contrast,
        "review_script_sha256": hashlib.sha256((trial / "review/app.js").read_bytes()).hexdigest(),
        "scope": "Automated browser checks. These responses are test data, not user research.",
    }
    (output / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f"{len(checks)} browser checks passed. Evidence: {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trial", type=Path, required=True)
    verify(parser.parse_args().trial.resolve())
