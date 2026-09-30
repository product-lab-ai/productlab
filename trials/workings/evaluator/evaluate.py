"""Check evidence available during a real Workings repair, without judging learning."""

import json
import sys
import traceback
from pathlib import Path

from playwright.sync_api import sync_playwright

LABELS = {
    "dispatch": "When the model requests a tool",
    "observation": "After the tool returns",
    "finish": "When the model returns an answer",
    "maxTurns": "Maximum model calls",
    "onError": "When a tool returns an error",
    "retries": "Maximum retries after errors",
}
SOLUTION = {
    "dispatch": "execute",
    "observation": "append",
    "finish": "return",
    "maxTurns": 8,
    "onError": "stop",
    "retries": 0,
}


def run_program(page):
    page.get_by_role("radio").first.check()
    page.get_by_role("button", name="Run agent", exact=True).click()
    page.locator(".agent-verdict strong").wait_for(timeout=15000)


def enter_task(page, folder, task):
    lesson = json.loads((folder / f"{task['lesson']}.json").read_text())
    page.goto((folder / "index.html").as_uri() + f"#/courses/ai/lessons/{lesson['id']}")
    coin = page.get_by_role("button", name="Insert coin", exact=False)
    if coin.is_visible():
        coin.click()
    page.get_by_role("heading", name=lesson["title"], exact=True).wait_for()
    for beat in lesson["beats"]:
        if beat["id"] == task["beat"]:
            return beat
        if beat["kind"] == "play":
            for key in beat["editable"]:
                page.get_by_label(LABELS[key], exact=True).select_option(str(SOLUTION[key]))
            run_program(page)
        page.get_by_role("button", name="Continue", exact=True).click()
    raise AssertionError("The requested task does not exist in this lesson")


def repair(page, folder, task, screenshots=None):
    enter_task(page, folder, task)
    run_program(page)
    original_events = page.locator(".agent-trace li p").all_inner_texts()
    original_outcome = page.locator(".agent-verdict").inner_text()
    if screenshots:
        page.screenshot(path=str(screenshots / "before-edit.png"))
    for key, value in task["changes"].items():
        page.get_by_label(LABELS[key], exact=True).select_option(str(value))
    assert page.get_by_role("button", name="Run agent", exact=True).is_disabled(), (
        "An edit must require a new prediction"
    )
    assert page.get_by_role("button", name="Continue", exact=True).is_disabled(), (
        "Earlier evidence cannot complete the edited task"
    )
    assert page.locator(".agent-verdict strong").count() == 0, "An old verdict remained current"
    comparison = page.get_by_role("region", name="Attempt comparison", exact=True)
    preserved_on_edit = comparison.count() == 1
    if screenshots:
        page.screenshot(path=str(screenshots / "after-edit.png"))
    run_program(page)
    assert page.get_by_role("button", name="Continue", exact=True).is_enabled(), (
        "The correct repair did not pass the existing grader"
    )
    current_events = page.locator(".agent-trace li p").all_inner_texts()
    facts = {
        "earlier_event_evidence": False,
        "earlier_changed_setting": False,
        "current_event_evidence": bool(current_events) and current_events != original_events,
        "current_changed_setting": all(
            page.get_by_label(LABELS[key], exact=True).input_value() == str(value)
            for key, value in task["changes"].items()
        ),
    }
    if comparison.count():
        previous = comparison.locator("details").first
        if previous.get_attribute("open") is None:
            previous.locator("summary").click()
        retained_events = previous.locator(".agent-attempt-trace li p").all_inner_texts()
        facts["earlier_event_evidence"] = retained_events == original_events
        facts["earlier_changed_setting"] = (
            task["before_setting"] in previous.locator("dl").inner_text()
        )
        assert facts["earlier_event_evidence"], (
            "Retained events differ from the earlier observed run"
        )
        assert facts["earlier_changed_setting"], (
            "Retained program does not match the earlier setting"
        )
        if screenshots:
            page.locator("main").evaluate("node => { node.scrollTop = node.scrollHeight; }")
            page.screenshot(path=str(screenshots / "comparison.png"))
    page.set_viewport_size({"width": 390, "height": 844})
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), (
        "The narrow page overflows"
    )
    if screenshots:
        page.screenshot(path=str(screenshots / "mobile.png"))
    return {
        "facts": facts,
        "preserved_on_edit": preserved_on_edit,
        "original_outcome": original_outcome,
        "original_events": original_events,
        "current_events": current_events,
    }


def run():
    request = json.load(sys.stdin)
    errors, external, failures = [], [], []
    observations = {"facts": {}}
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page(
                viewport={"width": 1440, "height": 1100}, reduced_motion="reduce"
            )
            page.set_default_timeout(7000)
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on(
                "request",
                lambda req: (
                    external.append(req.url) if req.url.startswith(("http:", "https:")) else None
                ),
            )
            try:
                observations = repair(page, Path(request["candidate_dir"]), request["task"])
            except Exception:
                failures.append(traceback.format_exc())
        finally:
            browser.close()
    facts = observations["facts"]
    print(
        json.dumps(
            {
                "metrics": {"comparison_evidence": sum(facts.values()) / 4},
                "gates": {
                    "repair-operates": "pass" if not failures and not errors else "fail",
                    "private-browser": "pass" if not external else "fail",
                },
                "feedback": {
                    **observations,
                    "failures": failures,
                    "browser_errors": errors,
                    "external_requests": external,
                    "scope": "Availability and consistency of observed evidence. "
                    "No learner understanding or preference measured.",
                },
            }
        )
    )


if __name__ == "__main__":
    run()
