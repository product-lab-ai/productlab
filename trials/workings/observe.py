"""Record browser observations of a frozen Workings build, without judging learning."""

import argparse
import hashlib
import json
import shutil
import sys
import traceback
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "evaluator"))
from evaluate import LABELS, SOLUTION, enter_task, repair, run_program  # noqa: E402


def observe(trial, output):
    output.mkdir(parents=True, exist_ok=False)
    shutil.copy2(__file__, output / "observer.py")
    baseline = trial / "baseline"
    result = {
        "status": "running",
        "basis": "automated browser observation and author review",
        "scope": "Local packaged build. No learner observations or production timing claims.",
        "artifact_sha256": hashlib.sha256((baseline / "index.html").read_bytes()).hexdigest(),
        "observer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "observations": {},
        "page_errors": [],
        "external_requests": [],
    }
    observations = result["observations"]
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(args=["--no-sandbox"])
            try:
                page = browser.new_page(
                    viewport={"width": 1440, "height": 1100}, reduced_motion="reduce"
                )
                page.set_default_timeout(15000)
                page.on("pageerror", lambda e: result["page_errors"].append(str(e)))
                page.on(
                    "request",
                    lambda r: (
                        result["external_requests"].append(r.url)
                        if r.url.startswith(("https:", "http:"))
                        else None
                    ),
                )
                page.goto((baseline / "index.html").as_uri())
                page.get_by_role("button", name="Insert coin", exact=False).click()
                observations["catalog"] = page.locator("main").inner_text()
                page.screenshot(path=str(output / "catalog.png"))
                pages = []
                for route in [
                    "#/courses/ai",
                    "#/courses/ansible",
                    "#/courses/ai/lessons/sampling-dials",
                    "#/courses/ansible/lessons/desired-state",
                    "#/missing-course",
                ]:
                    page.goto((baseline / "index.html").as_uri() + route)
                    page.locator("main").wait_for()
                    pages.append({"route": route, "text": page.locator("main").inner_text()[:1600]})
                observations["entry_routes"] = pages
                task = {
                    "lesson": "tool-using-agent",
                    "beat": "return-the-result",
                    "changes": {"observation": "append"},
                    "before_setting": "Discard the result",
                }
                observations["repair"] = repair(page, baseline, task)
                page.set_viewport_size({"width": 1440, "height": 1100})
                page.screenshot(path=str(output / "repair-desktop.png"))
                page.get_by_role("button", name="Show hint 1 of 3", exact=True).click()
                page.get_by_label("After the tool returns", exact=True).select_option("wrong-id")
                before = {
                    "step": page.locator(".lesson-progress").inner_text(),
                    "program": page.get_by_label(
                        "After the tool returns", exact=True
                    ).input_value(),
                    "evidence": page.evaluate(
                        "Object.fromEntries(Object.entries(localStorage)"
                        ".filter(([key]) => key.startsWith('workings-agent-evidence:')))"
                    ),
                }
                observations["reload"] = {"before": before}
                page.reload()
                coin = page.get_by_role("button", name="Insert coin", exact=False)
                observations["reload"]["coin_gate"] = coin.is_visible()
                if coin.is_visible():
                    coin.click()
                page.locator(".lesson-progress").wait_for()
                after = {
                    "step": page.locator(".lesson-progress").inner_text(),
                    "evidence": page.evaluate(
                        "Object.fromEntries(Object.entries(localStorage)"
                        ".filter(([key]) => key.startsWith('workings-agent-evidence:')))"
                    ),
                }
                observations["reload"].update(
                    after=after,
                    same_step=before["step"] == after["step"],
                    saved_evidence_retained=before["evidence"] == after["evidence"],
                )
                page.screenshot(path=str(output / "after-reload.png"))
                enter_task(page, baseline, task)
                observations["program_after_return"] = page.get_by_label(
                    "After the tool returns", exact=True
                ).input_value()
                page.set_viewport_size({"width": 390, "height": 844})
                page.screenshot(path=str(output / "repair-mobile.png"))
                observations["mobile_overflow"] = page.evaluate(
                    "document.documentElement.scrollWidth > innerWidth"
                )
                observations["mobile_viewport"] = page.evaluate(
                    "({width:innerWidth,height:innerHeight,screen:document.querySelector('.wish-screen-content').getBoundingClientRect().toJSON()})"
                )
                axe = (trial / "source/node_modules/axe-core/axe.min.js").read_text()
                page.evaluate(axe)
                observations["repair_accessibility"] = page.evaluate(
                    "async () => (await axe.run()).violations.map(v => "
                    "({id:v.id,impact:v.impact,targets:v.nodes.map(n=>n.target)}))"
                )
                page.set_viewport_size({"width": 1440, "height": 1100})
                lesson = json.loads((baseline / "tool-using-agent.json").read_text())
                page.close()
                page = browser.new_page(
                    viewport={"width": 1440, "height": 1100}, reduced_motion="reduce"
                )
                page.on("pageerror", lambda e: result["page_errors"].append(str(e)))
                page.goto(
                    (baseline / "index.html").as_uri() + "#/courses/ai/lessons/tool-using-agent"
                )
                page.get_by_role("button", name="Insert coin", exact=False).click()
                observations["journey_steps"] = []
                for beat in lesson["beats"]:
                    observations["journey_steps"].append(
                        {
                            "beat": beat["id"],
                            "visible_step": page.locator(".lesson-progress").inner_text(),
                        }
                    )
                    if beat["kind"] == "play":
                        for key in beat["editable"]:
                            page.get_by_label(LABELS[key], exact=True).select_option(
                                str(SOLUTION[key])
                            )
                        run_program(page)
                        if beat["mode"] == "challenge":
                            observations["challenge"] = {
                                "verdict": page.locator(".agent-verdict").inner_text(),
                                "case_buttons": page.locator(".agent-cases").inner_text(),
                                "help": page.locator(".agent-help").inner_text(),
                            }
                            page.screenshot(path=str(output / "challenge.png"))
                    if beat["kind"] != "free-play":
                        page.get_by_role("button", name="Continue", exact=True).click()
                observations["completion"] = page.evaluate(
                    "localStorage.getItem('workings-course-progress-v1')"
                )
                observations["export_controls"] = page.get_by_role("button").all_text_contents()
                page.screenshot(path=str(output / "free-play.png"))
                blocked = browser.new_context(
                    viewport={"width": 1440, "height": 1100}, reduced_motion="reduce"
                )
                blocked.add_init_script(
                    "Object.defineProperty(window, 'localStorage', "
                    "{get(){throw new DOMException('blocked','SecurityError')}})"
                )
                blocked_page = blocked.new_page()
                blocked_page.goto(
                    (baseline / "index.html").as_uri() + "#/courses/ai/lessons/tool-using-agent"
                )
                blocked_page.get_by_role("button", name="Insert coin", exact=False).click()
                blocked_page.locator(".lesson-progress").wait_for()
                observations["storage_blocked"] = {
                    "step": blocked_page.locator(".lesson-progress").inner_text(),
                    "notices": blocked_page.get_by_role("status").all_text_contents(),
                }
                blocked.close()
                result["status"] = "complete"
            finally:
                browser.close()
    except Exception:
        result.update(status="incomplete", error=traceback.format_exc())
        raise
    finally:
        (output / "observations.json").write_text(json.dumps(result, indent=2) + "\n")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trial", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = observe(args.trial.resolve(), args.output.resolve())
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
