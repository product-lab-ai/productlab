"""Prepare a local comparison from verified Product Lab engine results."""

import argparse
import hashlib
import json
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "skills/product-lab/scripts"))

from product_lab.cli import report_text  # noqa: E402
from product_lab.context import read_contract  # noqa: E402
from product_lab.demo import run_demo  # noqa: E402
from product_lab.model import LabError, canonical, digest  # noqa: E402
from product_lab.quality import quality_status  # noqa: E402
from product_lab.runner import costs, run_development, validate_lesson  # noqa: E402
from product_lab.storage import Lab, tree_digest  # noqa: E402

EXAMPLE = ROOT / "skills/product-lab/scripts/product_lab/assets/recovery"
VIEWS = {"current": "Current report", "a": "Prototype A", "b": "Prototype B"}


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def export_report(lab):
    report = lab.report()
    report["costs"] = costs(report)
    report["quality"] = [quality_status(lab, c["id"]) for c in report["candidates"]]
    return report


def case_from_lab(path, case_id, label):
    lab = Lab(path)
    try:
        report = export_report(lab)
    finally:
        lab.close()
    return {
        "id": case_id,
        "label": label,
        "report": report,
        "digest": digest(report),
        "original_text": report_text(report),
    }


def source_cases(output):
    print("Running source experiments, including a deliberate failed attempt.", flush=True)
    run_demo(output / "source-demo")
    spec = read_contract(EXAMPLE / "contract.json")
    failed = Lab.create(output / "source-failed", spec, EXAMPLE / "evaluator")
    try:
        failed.register("retry", EXAMPLE / "baseline", "Retry is the starting policy")
        run_development(failed, "baseline", "retry")
        broken = output / "malformed-policy"
        broken.mkdir()
        (broken / "policy.json").write_text("This is deliberately invalid JSON.\n")
        failed.register("broken", broken, "Exercise a real evaluator failure")
        failed.lesson("failure-case", "broken", "Probe failure reporting", ["baseline"])
        try:
            validate_lesson(failed, "transfer", "failure-case")
        except LabError:
            if failed.get("run", "transfer")["status"] != "failed":
                raise
        else:
            raise LabError("The failure probe unexpectedly completed")
    finally:
        failed.close()
    empty = Lab.create(output / "source-empty", spec, EXAMPLE / "evaluator")
    empty.close()
    return [
        case_from_lab(output / "source-demo/study", "case-1", "Case 1: remedy experiment"),
        case_from_lab(
            output / "source-demo/negative-control", "case-2", "Case 2: alternative remedy"
        ),
        case_from_lab(output / "source-failed", "case-3", "Case 3: failed comparison"),
    ], case_from_lab(output / "source-empty", "reserved-empty", "Unstarted study")


def trial_product():
    product = json.loads((ROOT / "PRODUCT.json").read_text())
    product["name"] = "Product Lab experiment review"
    product["purpose"] = (
        "Help a builder explain an experiment result and choose the next useful action."
    )
    product["journeys"].append(
        {
            "id": "understand-result",
            "persona": "builder",
            "trigger": "An experiment finishes or fails and needs a product decision.",
            "steps": [
                {
                    "id": "read",
                    "action": "Read the result and its scope",
                    "pain": "Measurements can hide missing product evidence",
                    "need": "A faithful result with uncertainty visible",
                },
                {
                    "id": "decide",
                    "action": "Explain what to try next and why",
                    "pain": "A successful simulation may be mistaken for product approval",
                    "need": "A next action consistent with the evidence",
                },
            ],
        }
    )
    product["outcomes"].append(
        {
            "id": "faithful-review",
            "journey": "understand-result",
            "description": "The builder can inspect the result without missing or altered facts.",
        }
    )
    return product


def contract(product, cases, reserved):
    tasks = [
        {
            "id": case["id"],
            "family": "completed-or-failed-report",
            "split": "development",
            "input": case,
        }
        for case in cases
    ]
    tasks.append(
        {
            "id": reserved["id"],
            "family": "unstarted-report",
            "split": "validation",
            "input": reserved,
        }
    )
    return {
        "product": product,
        "journey": "understand-result",
        "question": "Do these report presentations retain required facts and local behavior?",
        "evidence_kind": "automated",
        "repeats": 2,
        "timeout_seconds": 45,
        "metrics": [
            {
                "name": "fact_coverage",
                "direction": "maximize",
                "role": "primary",
                "min_gain": 0,
                "max_loss": 0,
                "limit": 1,
                "aggregation": "worst",
                "outcome": "faithful-review",
                "dimension": "functionality",
            }
        ],
        "gates": [
            {"id": "facts-present", "requirement": "valid-decisions"},
            {"id": "no-external-requests", "requirement": "private-evidence"},
            {"id": "page-operates", "requirement": "accessible-workflow"},
        ],
        "tasks": tasks,
    }


def make_web(target, data, variant=None):
    shutil.copytree(HERE / "web", target)
    (target / "data.js").write_text(
        "window.TRIAL_DATA = window.__TRIAL_OVERRIDE__ || " + canonical(data) + ";\n"
    )
    (target / "variant.js").write_text("window.TRIAL_VARIANT = " + json.dumps(variant) + ";\n")


def prepare(output, *, evaluate=True):
    if output.exists():
        raise LabError("Choose a new output directory. Existing trials and feedback are preserved")
    output.mkdir(parents=True, mode=0o700)
    started = time.monotonic()
    prepared_at = datetime.now(timezone.utc).isoformat()
    cases, reserved = source_cases(output)
    reports = output / "reports"
    reports.mkdir()
    for case in cases:
        write_json(reports / f"{case['id']}.json", case["report"])
        (reports / f"{case['id']}.txt").write_text(case["original_text"] + "\n")
    product = trial_product()
    spec = contract(product, cases, reserved)
    write_json(output / "product.json", product)
    write_json(output / "contract.json", spec)
    lab = Lab.create(output / "engineering-study", spec, HERE / "evaluator")
    try:
        identifiers = {}
        for variant, label in VIEWS.items():
            candidate = output / "prototypes" / variant
            make_web(candidate, {"cases": []}, variant)
            lab.register(
                variant,
                candidate,
                f"{label} can present the recorded result without changing required facts",
            )
            identifiers[variant] = tree_digest(candidate)
        write_json(output / "candidate-digests.json", identifiers)
        if evaluate:
            for variant, label in VIEWS.items():
                print(f"Checking {label} through Product Lab's engine.", flush=True)
                run = run_development(lab, f"check-{variant}", variant)
                print(f"  {run['decision']['status']}: {run['summary']}", flush=True)
        engineering = export_report(lab)
        write_json(output / "engineering-results.json", engineering)
        (output / "engineering-results.txt").write_text(report_text(engineering) + "\n")
    finally:
        lab.close()
    manifest = {
        "id": hashlib.sha256((prepared_at + digest(identifiers)).encode()).hexdigest()[:12],
        "prepared_at": prepared_at,
        "candidates": identifiers,
        "cases": cases,
    }
    make_web(output / "review", manifest)
    shutil.copytree(reports, output / "review/reports")
    write_json(output / "manifest.json", manifest)
    write_json(
        output / "costs.json",
        {
            "preparation_command_seconds": time.monotonic() - started,
            "engineering_evaluators": engineering["costs"],
            "authoring_time": "Not measured by this command",
            "model_use": "Assistant used for design and implementation; charges unknown",
            "human_review": "Pending",
            "claim": "These records do not establish total cost or savings",
        },
    )
    print(f"Open {output / 'review/index.html'}", flush=True)
    print("Human review is pending. Reserved engineering validation remains unused.", flush=True)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="A new local output directory")
    parser.add_argument(
        "--skip-engineering-checks",
        action="store_true",
        help="Prepare views without browser checks",
    )
    args = parser.parse_args()
    try:
        prepare(args.output.resolve(), evaluate=not args.skip_engineering_checks)
    except (LabError, OSError) as exc:
        parser.exit(2, f"Trial preparation: {exc}\n")


if __name__ == "__main__":
    main()
