"""Review the revised Workings comparison using the delivered local files."""

import argparse
import hashlib
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "evaluator"))
from evaluate import repair  # noqa: E402


def verify(trial, workings):
    axe = (workings / "node_modules/axe-core/axe.min.js").read_text()
    output = trial / "revised-browser"
    output.mkdir(exist_ok=False)
    checks, errors, external = [], [], []

    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    task = {
        "lesson": "tool-using-agent",
        "beat": "return-the-result",
        "changes": {"observation": "append"},
        "before_setting": "Discard the result",
    }
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            for candidate in ("history-revised", "compare-revised"):
                folder = trial / candidate
                screenshots = output / candidate
                screenshots.mkdir()
                page = browser.new_page(
                    viewport={"width": 1440, "height": 1100}, reduced_motion="reduce"
                )
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.on(
                    "request",
                    lambda req: (
                        external.append(req.url)
                        if req.url.startswith(("http:", "https:"))
                        else None
                    ),
                )
                evidence = repair(page, folder, task)
                check(
                    f"{candidate}: earlier facts match the actual original run",
                    all(evidence["facts"].values()),
                )
                check(
                    f"{candidate}: earlier attempt survives an edit", evidence["preserved_on_edit"]
                )
                page.evaluate(axe)
                region = page.get_by_role("region", name="Attempt comparison", exact=True)
                previous = region.locator("details").first
                if previous.get_attribute("open") is not None:
                    previous.locator("summary").click()
                page.get_by_role(
                    "button", name="Compare with the previous attempt", exact=True
                ).click()
                check(
                    f"{candidate}: comparison button moves keyboard focus",
                    region.evaluate("node => node === document.activeElement"),
                )
                page.keyboard.press("Tab")
                page.keyboard.press("Enter")
                page.keyboard.press("Tab")
                check(
                    f"{candidate}: retained trace is reachable by keyboard",
                    previous.locator(".agent-attempt-trace").evaluate(
                        "node => node === document.activeElement"
                    ),
                )
                for width, name in [(390, "narrow"), (1440, "desktop")]:
                    page.set_viewport_size(
                        {"width": width, "height": 844 if width == 390 else 1100}
                    )
                    for theme in ("dark", "light"):
                        if (
                            candidate.startswith("compare")
                            and previous.get_attribute("open") is not None
                        ):
                            previous.locator("summary").click()
                        page.get_by_role(
                            "button", name="Compare with the previous attempt", exact=True
                        ).click()
                        issues = page.evaluate(
                            "async () => (await axe.run()).violations"
                            ".filter(v => ['serious', 'critical'].includes(v.impact))"
                            ".map(v => ({id:v.id, nodes:v.nodes.map(n=>n.target)}))"
                        )
                        check(
                            f"{candidate}: {name} {theme} has no serious accessibility findings",
                            not issues,
                        )
                        check(
                            f"{candidate}: {name} {theme} has no page overflow",
                            page.evaluate("document.documentElement.scrollWidth <= innerWidth"),
                        )
                        page.screenshot(path=str(screenshots / f"{name}-{theme}.png"))
                        page.get_by_role("switch").click()
                if candidate.startswith("compare"):
                    rows = region.locator("tbody tr").all_inner_texts()
                    check(
                        "Guided comparison shows the result transition",
                        any(
                            "Call limit reached" in row and "Answer returned" in row for row in rows
                        ),
                    )
                    check(
                        "Guided comparison identifies the first observed difference",
                        region.get_by_role(
                            "heading", name="First difference: event 3", exact=True
                        ).is_visible(),
                    )
                    check(
                        "Guided comparison excludes unrelated retry controls",
                        "Retry limit" not in region.inner_text(),
                    )
                page.get_by_role("button", name="Reset agent run", exact=True).click()
                check(f"{candidate}: reset clears earlier comparison", region.count() == 0)
                page.get_by_role("radio").first.check()
                page.get_by_role("button", name="Step agent", exact=True).click()
                page.get_by_role("button", name="Stop", exact=True).click()
                page.get_by_label("After the tool returns", exact=True).select_option("wrong-id")
                check(
                    f"{candidate}: interrupted run cannot become comparison evidence",
                    region.count() == 0,
                )
                check(
                    f"{candidate}: interrupted and edited work cannot complete the task",
                    page.get_by_role("button", name="Continue", exact=True).is_disabled(),
                )
                evidence["artifact_sha256"] = hashlib.sha256(
                    (folder / "index.html").read_bytes()
                ).hexdigest()
                (screenshots / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")
                page.close()
            check("No page exceptions", not errors)
            check("No external browser requests", not external)
        finally:
            browser.close()
    result = {
        "status": "passed",
        "checks": checks,
        "scope": "Browser operation and automated accessibility. "
        "No learner feedback or assistive-technology user trial.",
    }
    (output / "results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(f"{len(checks)} checks passed. Evidence: {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trial", required=True, type=Path)
    parser.add_argument("--workings", required=True, type=Path)
    args = parser.parse_args()
    verify(args.trial.resolve(), args.workings.resolve())
