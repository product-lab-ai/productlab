"""Compare the frozen Workings builds through actual browser repairs."""

import argparse
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "skills/product-lab/scripts"))
from product_lab.cli import report_text  # noqa: E402
from product_lab.quality import quality_status  # noqa: E402
from product_lab.runner import costs, run_development  # noqa: E402
from product_lab.storage import Lab  # noqa: E402

TASKS = [
    {
        "id": "return-results",
        "family": "tool-observations",
        "split": "development",
        "input": {
            "lesson": "tool-using-agent",
            "beat": "return-the-result",
            "changes": {"observation": "append"},
            "before_setting": "Discard the result",
        },
    },
    {
        "id": "execute-requests",
        "family": "tool-dispatch",
        "split": "development",
        "input": {
            "lesson": "tool-using-agent",
            "beat": "execute-the-tool",
            "changes": {"dispatch": "execute"},
            "before_setting": "Stop",
        },
    },
    {
        "id": "return-answer",
        "family": "answer-termination",
        "split": "development",
        "input": {
            "lesson": "tool-using-agent",
            "beat": "return-the-answer",
            "changes": {"finish": "return"},
            "before_setting": "Call the model again",
        },
    },
    {
        "id": "reserved-tool-errors",
        "family": "tool-error-recovery",
        "split": "validation",
        "input": {
            "lesson": "retry-tools",
            "beat": "allow-one-retry",
            "changes": {"onError": "retry", "retries": 1},
            "before_setting": "Stop",
        },
    },
]


def prepare(output):
    product = json.loads((HERE / "PRODUCT.json").read_text())
    contract = {
        "product": product,
        "journey": "repair-and-explain",
        "question": "Does the repair journey retain correct evidence for comparing attempts?",
        "evidence_kind": "automated",
        "repeats": 2,
        "timeout_seconds": 90,
        "metrics": [
            {
                "name": "comparison_evidence",
                "direction": "maximize",
                "role": "primary",
                "min_gain": 0.1,
                "max_loss": 0,
                "limit": 0,
                "aggregation": "worst",
                "outcome": "explain-a-change",
                "dimension": "functionality",
            }
        ],
        "gates": [
            {"id": "repair-operates", "requirement": "valid-decisions"},
            {"id": "private-browser", "requirement": "private-evidence"},
        ],
        "tasks": TASKS,
    }
    (output / "contract.json").write_text(json.dumps(contract, indent=2) + "\n")
    started = time.monotonic()
    lab = Lab.create(output / "study", contract, HERE / "evaluator")
    try:
        for candidate, hypothesis in [
            ("baseline", "Current Workings supports comparison through its existing evidence"),
            (
                "history",
                "Retaining the earlier attempt makes the evidence for a comparison available",
            ),
            (
                "compare",
                "Showing observed differences makes the comparison easier to inspect; "
                "human effort is unmeasured",
            ),
        ]:
            lab.register(candidate, output / candidate, hypothesis)
            print(f"Running {candidate} through the existing repair journey.", flush=True)
            run = run_development(lab, candidate, candidate)
            print(f"  {run['decision']['status']}: {run['summary']}", flush=True)
        report = lab.report()
        report["costs"] = costs(report)
        report["quality"] = [
            quality_status(lab, candidate["id"]) for candidate in report["candidates"]
        ]
        (output / "results.json").write_text(json.dumps(report, indent=2) + "\n")
        (output / "results.txt").write_text(report_text(report) + "\n")
        (output / "costs.json").write_text(
            json.dumps(
                {
                    "evaluation_command_seconds": time.monotonic() - started,
                    "evaluator": report["costs"],
                    "authoring_and_model_cost": "Unknown",
                    "human_effort": "Not measured",
                    "learner_feedback": "Pending",
                },
                indent=2,
            )
            + "\n"
        )
    finally:
        lab.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", required=True, type=Path)
    prepare(parser.parse_args().artifacts.resolve())
