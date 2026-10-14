"""Check recovery controls, failure states, and accessibility in delivered builds."""

import argparse
import hashlib
import json
import sys
import traceback
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "evaluator"))
from evaluate import reenter  # noqa: E402
from journey import enter_task  # noqa: E402


def verify(trial, output):
    output.mkdir(parents=True, exist_ok=False)
    results = {"status": "running", "checks": [], "artifacts": {}, "errors": []}

    def check(name, value):
        results["checks"].append({"name": name, "passed": bool(value)})
        assert value, name

    task = {"lesson": "tool-using-agent", "beat": "return-the-result"}
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(args=["--no-sandbox"])
            try:
                for candidate in ["bookmark", "draft"]:
                    folder = trial / candidate
                    results["artifacts"][candidate] = hashlib.sha256(
                        (folder / "index.html").read_bytes()
                    ).hexdigest()
                    page = browser.new_page(
                        viewport={"width": 1440, "height": 1100}, reduced_motion="reduce"
                    )
                    page.on("pageerror", lambda error: results["errors"].append(str(error)))
                    enter_task(page, folder, task)
                    program = page.get_by_label("After the tool returns", exact=True)
                    program.select_option("wrong-id")
                    reenter(page)
                    check(
                        candidate + ": restores step",
                        "Step 4 " in page.locator(".lesson-progress").inner_text(),
                    )
                    expected = "wrong-id" if candidate == "draft" else "discard"
                    check(candidate + ": expected program", program.input_value() == expected)
                    program.focus()
                    page.keyboard.press("ArrowDown" if expected == "discard" else "ArrowUp")
                    check(candidate + ": keyboard edit", program.input_value() != expected)
                    check(
                        candidate + ": new prediction",
                        page.get_by_role("button", name="Run agent", exact=True).is_disabled(),
                    )
                    page.screenshot(path=str(output / f"{candidate}-desktop.png"))
                    page.set_viewport_size({"width": 390, "height": 844})
                    page.locator("main").focus()
                    for _ in range(40):
                        page.keyboard.press("Tab")
                        if program.evaluate("n => n === document.activeElement"):
                            break
                    check(
                        candidate + ": keyboard reaches mobile edit",
                        program.evaluate("n => n === document.activeElement"),
                    )
                    page.screenshot(path=str(output / f"{candidate}-mobile.png"))
                    check(
                        candidate + ": mobile overflow",
                        page.evaluate("document.documentElement.scrollWidth <= innerWidth"),
                    )
                    check(
                        candidate + ": control within mobile screen",
                        program.evaluate(
                            "n => { const r=n.getBoundingClientRect(); "
                            "const s=document.querySelector('.wish-screen-content')"
                            ".getBoundingClientRect(); return r.top>=s.top && r.bottom<=s.bottom; }"
                        ),
                    )
                    page.screenshot(path=str(output / f"{candidate}-mobile.png"))
                    page.evaluate((trial / "source/node_modules/axe-core/axe.min.js").read_text())
                    violations = page.evaluate("async () => (await axe.run()).violations")
                    results[candidate + "_axe"] = violations
                    check(candidate + ": axe inspected state", not violations)
                    page.close()

                    blocked = browser.new_context(reduced_motion="reduce")
                    blocked.add_init_script(
                        "Object.defineProperty(window, 'localStorage', "
                        "{get(){throw new DOMException('blocked','SecurityError')}})"
                    )
                    page = blocked.new_page()
                    page.on("pageerror", lambda error: results["errors"].append(str(error)))
                    enter_task(page, folder, task)
                    check(
                        candidate + ": unavailable storage notice",
                        page.get_by_text(
                            "Your place cannot be saved in this browser. "
                            "You can keep working here.",
                            exact=True,
                        ).is_visible(),
                    )
                    if candidate == "draft":
                        check(
                            candidate + ": unavailable draft notice",
                            page.get_by_text(
                                "Your draft cannot be saved in this browser. "
                                "You can keep working here.",
                                exact=True,
                            ).is_visible(),
                        )
                    check(
                        candidate + ": editable without storage",
                        page.get_by_label("After the tool returns", exact=True).is_enabled(),
                    )
                    blocked.close()
                check("No page errors in inspected journeys", not results["errors"])
                results["status"] = "complete"
            finally:
                browser.close()
    except Exception:
        results.update(status="incomplete", error=traceback.format_exc())
        raise
    finally:
        (output / "verification.json").write_text(json.dumps(results, indent=2) + "\n")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.artifacts.resolve(), args.output.resolve()), indent=2))
