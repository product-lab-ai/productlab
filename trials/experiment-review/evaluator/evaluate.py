"""Check visible source facts and local browser behavior, not human understanding."""

import json
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright


def normalize(value):
    return re.sub(r"[_-]", " ", value.casefold())


def run():
    request = json.load(sys.stdin)
    case = request["task"]
    report = case["report"]
    source = report["contract"]["contract"]
    expected = {
        "question": source["question"],
        "evidence_kind": f"Evidence: {source['evidence_kind']}",
        "validation_state": f"Validation consumed: {report['state']['validation_used']}",
        "claim_boundary": "Human product value is untested",
    }
    latest = report["runs"][-1] if report["runs"] else None
    if latest:
        expected["run_id"] = latest["id"]
        expected["run_status"] = latest.get(
            "lesson_verdict", latest.get("decision", {}).get("status", latest["status"])
        )
        for name, summary in latest.get("summary", {}).items():
            expected[f"metric:{name}"] = name
            expected[f"value:{name}"] = f"{summary['mean']:.4g}"
        if latest.get("error"):
            expected["failure"] = latest["error"]
        quality = next(
            (q for q in report["quality"] if q["candidate"] == latest["candidate"]), None
        )
        if quality:
            expected["review_status"] = quality["status"]
            for area, value in quality["areas"].items():
                expected[f"requirement:{area}"] = area
                expected[f"review:{area}"] = value
    browser_errors, external = [], []
    override = {
        "id": "engineering-check",
        "prepared_at": "Automated fixture",
        "cases": [case],
        "candidates": {"current": "fixture", "a": "fixture", "b": "fixture"},
    }
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page(viewport={"width": 1360, "height": 1000})
            page.on("pageerror", lambda error: browser_errors.append(str(error)))
            page.on(
                "request",
                lambda req: (
                    external.append(req.url) if req.url.startswith(("http:", "https:")) else None
                ),
            )
            page.add_init_script("window.__TRIAL_OVERRIDE__ = " + json.dumps(override) + ";")
            page.goto((Path(request["candidate_dir"]) / "index.html").as_uri())
            page.locator("#report").wait_for()
            # Disclosed requirement details must be reachable. Raw JSON does not count.
            details = page.locator("details[data-requirements]")
            if details.count():
                details.locator("summary").click()
            visible = normalize(page.locator("#report").inner_text())
            checks = {name: normalize(value) in visible for name, value in expected.items()}
            page.set_viewport_size({"width": 390, "height": 844})
            no_overflow = page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
            usable = no_overflow and not browser_errors and page.locator("#finding").is_visible()
        finally:
            browser.close()
    result = {
        "metrics": {"fact_coverage": sum(checks.values()) / len(checks)},
        "gates": {
            "facts-present": "pass" if all(checks.values()) else "fail",
            "no-external-requests": "pass" if not external else "fail",
            "page-operates": "pass" if usable else "fail",
        },
        "feedback": {
            "checks": checks,
            "browser_errors": browser_errors,
            "external_requests": external,
            "scope": "Visible source facts and basic rendering only. No human judgment measured.",
        },
    }
    print(json.dumps(result))


if __name__ == "__main__":
    run()
