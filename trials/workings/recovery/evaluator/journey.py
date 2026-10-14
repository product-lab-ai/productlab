"""Navigation helpers frozen from the existing Workings trial."""

import json

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
