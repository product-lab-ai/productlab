"""Command line interface for local product experiments."""

import argparse
import json
import sqlite3
import sys
from pathlib import Path

from .context import product_text, read_contract
from .model import LabError
from .quality import quality_status, record_review
from .runner import costs, run_development, validate_lesson
from .storage import Lab


def read_json(path):
    return json.loads(Path(path).read_text())


def report_text(report):
    contract = report["contract"]["contract"]
    product = contract["product"]
    journey = next(item for item in product["journeys"] if item["id"] == contract["journey"])
    persona = next(item for item in product["personas"] if item["id"] == journey["persona"])
    lines = [
        f"Question: {report['contract']['contract']['question']}",
        f"Evidence: {report['contract']['contract']['evidence_kind']}",
        f"Experimental reference: {report['state']['current'] or 'none'}",
        f"Product: {product['name']}",
        f"Audience: {persona['name']} ({persona['basis']})",
        f"Journey: {report['contract']['contract']['journey']}",
        f"Validation consumed: {report['state']['validation_used']}",
        f"Intended experience: {product['craft']['intent']}",
        "",
    ]
    for run in report["runs"]:
        verdict = run.get("lesson_verdict", run.get("decision", {}).get("status", run["status"]))
        lines.append(f"{run['id']}: {verdict}")
        for reason in run.get("decision", {}).get("reasons", []):
            lines.append(f"  {reason}")
        if run.get("error"):
            lines.append(f"  {run['error']}")
        for name, value in run.get("summary", {}).items():
            lines.append(f"  {name}: {value['mean']:.4g} [{value['low']:.4g}, {value['high']:.4g}]")
    expense = costs(report)
    for quality in report.get("quality", []):
        lines.extend(["", f"Product review for {quality['candidate']}: {quality['status']}"])
        lines.extend(f"  {area}: {status}" for area, status in quality["areas"].items())
    lines.extend(
        [
            "",
            f"Completed evaluator calls: {expense['completed_evaluations']}",
            f"Evaluator wall time: {expense['wall_seconds']:.3f} seconds",
            f"Calls without reported cost: {expense['cost_unknown_evaluations']}",
            "Ranges are observed bounds, not confidence intervals.",
            "Lesson support applies only to this study. Human product value is untested.",
        ]
    )
    return "\n".join(lines)


def parser():
    result = argparse.ArgumentParser(description="Run product experiments and test scoped lessons.")
    commands = result.add_subparsers(dest="command", required=True)
    brief = commands.add_parser(
        "brief", help="Show the product audience, journey, and quality intent"
    )
    brief.add_argument("--product", required=True)
    init = commands.add_parser("init", help="Freeze a contract and evaluator in a new lab")
    init.add_argument("--lab", required=True)
    init.add_argument("--contract", required=True)
    init.add_argument("--evaluator", required=True)
    register = commands.add_parser("register", help="Snapshot a candidate and its hypothesis")
    register.add_argument("--lab", required=True)
    register.add_argument("--id", required=True)
    register.add_argument("--candidate", required=True)
    register.add_argument("--hypothesis", required=True)
    run = commands.add_parser("run", help="Measure a candidate on development tasks")
    run.add_argument("--lab", required=True)
    run.add_argument("--id", required=True)
    run.add_argument("--candidate", required=True)
    lesson = commands.add_parser("lesson", help="Freeze a lesson before using validation tasks")
    lesson.add_argument("--lab", required=True)
    lesson.add_argument("--id", required=True)
    lesson.add_argument("--candidate", required=True)
    lesson.add_argument("--statement", required=True)
    lesson.add_argument(
        "--evidence", action="append", required=True, help="Completed development run ID"
    )
    validate = commands.add_parser("validate", help="Use the reserved tasks once to test a lesson")
    validate.add_argument("--lab", required=True)
    validate.add_argument("--id", required=True)
    validate.add_argument("--lesson", required=True)
    report = commands.add_parser("report", help="Show completed and incomplete evidence")
    report.add_argument("--lab", required=True)
    report.add_argument("--json", action="store_true")
    recover = commands.add_parser(
        "recover", help="Mark an active run interrupted after its process stops"
    )
    recover.add_argument("--lab", required=True)
    recover.add_argument("--id", required=True)
    review = commands.add_parser(
        "review", help="Attach an attributed review to a candidate snapshot"
    )
    for name in ("lab", "id", "candidate", "area", "reviewer", "note", "evidence"):
        review.add_argument(f"--{name}", required=True)
    review.add_argument("--verdict", required=True, choices=("pass", "fail", "unknown"))
    demo = commands.add_parser("demo", help="Run a local simulation with no model or network calls")
    demo.add_argument(
        "--output", required=True, help="New directory for evidence and generated policies"
    )
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    lab = None
    try:
        if args.command == "brief":
            print(product_text(read_json(args.product)))
            return 0
        if args.command == "demo":
            from .demo import run_demo

            print(run_demo(Path(args.output)))
            return 0
        if args.command == "init":
            lab = Lab.create(args.lab, read_contract(args.contract), args.evaluator)
            output = {"lab": str(lab.root), "contract": lab.get("contract", "main")["digest"]}
        else:
            lab = Lab(args.lab)
            if args.command == "register":
                output = lab.register(args.id, args.candidate, args.hypothesis)
            elif args.command == "run":
                output = run_development(lab, args.id, args.candidate)
            elif args.command == "lesson":
                output = lab.lesson(args.id, args.candidate, args.statement, args.evidence)
            elif args.command == "validate":
                output = validate_lesson(lab, args.id, args.lesson)
            elif args.command == "recover":
                output = lab.recover(args.id)
            elif args.command == "review":
                output = record_review(
                    lab,
                    args.id,
                    args.candidate,
                    args.area,
                    args.verdict,
                    args.reviewer,
                    args.note,
                    args.evidence,
                )
            else:
                output = lab.report()
                output["costs"] = costs(output)
                output["quality"] = [quality_status(lab, c["id"]) for c in output["candidates"]]
                if not args.json:
                    print(report_text(output))
                    return 0
        print(json.dumps(output, indent=2, allow_nan=False))
        return 0
    except (LabError, OSError, sqlite3.Error, json.JSONDecodeError) as exc:
        print(f"Product Lab: {exc}", file=sys.stderr)
        return 2
    finally:
        if lab is not None:
            lab.close()
