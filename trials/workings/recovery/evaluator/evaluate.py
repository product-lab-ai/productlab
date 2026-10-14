"""Measure restored unfinished state, without claiming learner benefit."""

import json
import sys
import traceback
from pathlib import Path

from journey import LABELS, SOLUTION, enter_task, run_program
from playwright.sync_api import sync_playwright


def reenter(page):
    page.reload()
    coin = page.get_by_role("button", name="Insert coin", exact=False)
    if coin.is_visible():
        coin.click()
    page.locator(".lesson-progress").wait_for()


def evidence(page):
    return page.evaluate(
        "Object.fromEntries(Object.entries(localStorage)"
        ".filter(([key]) => key.startsWith('workings-agent-evidence:')))"
    )


def observe(page, folder, task):
    beat = enter_task(page, folder, task)
    run_program(page)
    page.get_by_role("button", name="Show hint 1 of 3", exact=True).click()
    for key, value in task["draft"].items():
        page.get_by_label(LABELS[key], exact=True).select_option(str(value))
    before = {
        "step": page.locator(".lesson-progress").inner_text(),
        "draft": {
            key: page.get_by_label(LABELS[key], exact=True).input_value() for key in task["draft"]
        },
        "evidence": evidence(page),
    }
    reenter(page)
    same_step = page.locator(".lesson-progress").inner_text() == before["step"]
    same_draft = same_step and all(
        page.get_by_label(LABELS[key], exact=True).input_value() == str(value)
        for key, value in task["draft"].items()
    )
    checks = {"historical_evidence_kept": evidence(page) == before["evidence"]}
    if same_step:
        checks.update(
            prediction_required=page.get_by_role(
                "button", name="Run agent", exact=True
            ).is_disabled(),
            fresh_run_required=page.get_by_role(
                "button", name="Continue", exact=True
            ).is_disabled(),
            no_current_verdict=page.locator(".agent-verdict strong").count() == 0,
            no_restored_prediction=page.locator('input[type="radio"]:checked').count() == 0,
        )
    page.screenshot(path="recovered.png")
    after = {
        "step": page.locator(".lesson-progress").inner_text(),
        "same_step": same_step,
        "same_draft": same_draft,
        "checks": checks,
    }
    if not same_step:
        enter_task(page, folder, task)
    for key in beat["editable"]:
        page.get_by_label(LABELS[key], exact=True).select_option(str(SOLUTION[key]))
    run_program(page)
    checks["fresh_repair_operates"] = page.get_by_role(
        "button", name="Continue", exact=True
    ).is_enabled()
    return {"before": before, "after": after, "checks": checks}


def run():
    request = json.load(sys.stdin)
    errors, external, failures = [], [], []
    result = {"after": {"same_step": False, "same_draft": False}, "checks": {}}
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox"])
        try:
            page = browser.new_page(
                viewport={"width": 1440, "height": 1100}, reduced_motion="reduce"
            )
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on(
                "request",
                lambda req: (
                    external.append(req.url) if req.url.startswith(("https:", "http:")) else None
                ),
            )
            result = observe(page, Path(request["candidate_dir"]), request["task"])
        except Exception:
            failures.append(traceback.format_exc())
        finally:
            browser.close()
    passed = (
        not failures and not errors and bool(result["checks"]) and all(result["checks"].values())
    )
    print(
        json.dumps(
            {
                "metrics": {
                    "recovered_state": sum(
                        int(result["after"][key]) for key in ["same_step", "same_draft"]
                    )
                    / 2
                },
                "gates": {
                    "valid-recovery": "pass" if passed else "fail",
                    "private-browser": "pass" if not external else "fail",
                },
                "feedback": {
                    **result,
                    "failures": failures,
                    "page_errors": errors,
                    "external_requests": external,
                    "scope": "Step and draft recovery only. No learner outcome measured.",
                },
            }
        )
    )


if __name__ == "__main__":
    run()
