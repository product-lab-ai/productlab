"""Retain the failed requirement reviews and evaluate the corrected Workings builds."""

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "skills/product-lab/scripts"))
from product_lab.cli import report_text  # noqa: E402
from product_lab.quality import quality_status, record_review  # noqa: E402
from product_lab.runner import costs, run_development  # noqa: E402
from product_lab.storage import Lab  # noqa: E402


def revise(output):
    browser = json.loads((output / "revised-browser/results.json").read_text())
    if browser["status"] != "passed":
        raise ValueError("The revised browser checks must pass before recording this review")
    lab = Lab(output / "study")
    try:
        for candidate in ("history", "compare"):
            record_review(
                lab,
                f"{candidate}-keyboard-failure",
                candidate,
                "accessible-workflow",
                "fail",
                "Codex using an automated browser check",
                "The retained trace scrolls but cannot receive keyboard focus.",
                output / f"{candidate}-browser/results.json",
            )
        for candidate in ("history-revised", "compare-revised"):
            lab.register(
                candidate,
                output / candidate,
                "Retain the observed evidence while making its trace keyboard accessible "
                "and its comparison reachable from the current work",
            )
            print(f"Evaluating {candidate} through the frozen repair checks.", flush=True)
            run = run_development(lab, candidate, candidate)
            print(f"  {run['decision']['status']}: {run['summary']}", flush=True)
            evidence = json.loads(
                (output / "revised-browser" / candidate / "evidence.json").read_text()
            )
            expected = hashlib.sha256((output / candidate / "index.html").read_bytes()).hexdigest()
            if evidence["artifact_sha256"] != expected:
                raise ValueError("Browser evidence refers to a different candidate build")
            review = {
                "artifact_sha256": expected,
                "checks": [name for name in browser["checks"] if name.startswith(candidate)],
                "scope": "Keyboard navigation, narrow layouts, both themes, and axe checks. "
                "No assistive-technology user trial or learner feedback.",
            }
            path = output / "revised-browser" / candidate / "access-review.json"
            path.write_text(json.dumps(review, indent=2) + "\n")
            record_review(
                lab,
                f"{candidate}-access",
                candidate,
                "accessible-workflow",
                "pass",
                "Codex using browser automation and direct screen inspection",
                review["scope"],
                path,
            )
        lab.lesson(
            "retain-observed-attempt",
            "compare-revised",
            "In these deterministic agent repairs, retaining a completed attempt for the same "
            "case preserves evidence lost during an edit. Partial runs and changed scenarios "
            "cannot supply that comparison. Several changed blocks show a combined effect. "
            "This is a proposed software-design lesson, not evidence of improved learning.",
            ["baseline", "history-revised", "compare-revised"],
        )
        report = lab.report()
        report["costs"] = costs(report)
        report["quality"] = [
            quality_status(lab, candidate["id"]) for candidate in report["candidates"]
        ]
        (output / "revised-results.json").write_text(json.dumps(report, indent=2) + "\n")
        (output / "revised-results.txt").write_text(report_text(report) + "\n")
        shutil.copyfile(HERE / "review.html", output / "index.html")
    finally:
        lab.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", required=True, type=Path)
    revise(parser.parse_args().artifacts.resolve())
