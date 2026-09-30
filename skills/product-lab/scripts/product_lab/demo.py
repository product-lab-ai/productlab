"""A small simulation showing evidence-driven policy updates and reserved trials."""

import json
import shutil
from collections import defaultdict
from pathlib import Path

from .context import read_contract
from .model import LabError
from .runner import run_development, validate_lesson
from .storage import Lab


def learn_policy(run):
    """Use unanimous observed remedies, ignoring task IDs and workload family."""
    remedies = defaultdict(set)
    for samples in run["samples"].values():
        for sample in samples:
            feedback = sample["output"].get("feedback", {})
            if not feedback.get("completed"):
                remedies[feedback["error"]].add(tuple(feedback["required_actions"]))
    return {
        "default": ["retry"],
        "rules": {
            error: list(next(iter(actions)))
            for error, actions in remedies.items()
            if len(actions) == 1
        },
    }


def write_policy(directory, policy):
    directory.mkdir()
    (directory / "policy.json").write_text(json.dumps(policy, indent=2) + "\n")


def run_demo(output):
    # The example ships with the skill, so copied skills retain a runnable demo.
    example = Path(__file__).resolve().parent / "assets/recovery"
    output = output.resolve()
    if output.exists():
        raise LabError("Demo output already exists. Choose a new directory")
    output.mkdir(parents=True)
    shutil.copytree(example, output / "inputs")
    contract = read_contract(example / "contract.json")
    learned_dir, wrong_dir = output / "learned-policy", output / "overgeneralized-policy"
    good_lab = Lab.create(output / "study", contract, example / "evaluator")
    try:
        good_lab.register(
            "retry", example / "baseline", "Retrying is enough to recover a failed job"
        )
        development = run_development(good_lab, "baseline", "retry")
        policy = learn_policy(development)
        write_policy(learned_dir, policy)
        good_lab.register(
            "learned",
            learned_dir,
            "Remedies observed during development also help new workload families",
        )
        good_lab.lesson(
            "conditioned-remedies",
            "learned",
            "Choose a remedy from the observed failure reason; retain retry as fallback",
            ["baseline"],
        )
        validation = validate_lesson(good_lab, "transfer", "conditioned-remedies")
        report = good_lab.report()
        (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    finally:
        good_lab.close()

    # A separate negative control demonstrates that recording a lesson is not support.
    write_policy(wrong_dir, {"default": ["force_restart"], "rules": {}})
    bad_lab = Lab.create(output / "negative-control", contract, example / "evaluator")
    try:
        bad_lab.register("retry", example / "baseline", "Retry is the control policy")
        run_development(bad_lab, "baseline", "retry")
        bad_lab.register("force", wrong_dir, "Force restarting recovers every kind of failure")
        bad_lab.lesson("force-everything", "force", "Always force restart", ["baseline"])
        negative = validate_lesson(bad_lab, "transfer", "force-everything")
    finally:
        bad_lab.close()
    if validation["lesson_verdict"] != "supported" or negative["lesson_verdict"] != "rejected":
        raise LabError("Demo did not produce its expected positive and negative controls")
    before = validation["control_summary"]["completion"]["mean"]
    after = validation["summary"]["completion"]["mean"]
    return "\n".join(
        [
            "Product Lab demo completed.",
            "Evidence: a deterministic simulation, with no model or network calls.",
            f"Learned rules from development feedback: {len(policy['rules'])}",
            f"Reserved-task completion: {before:.0%} -> {after:.0%}",
            f"Conditioned lesson: {validation['lesson_verdict']}",
            f"Overgeneralized lesson: {negative['lesson_verdict']}",
            f"Evidence directory: {output}",
            "These controls demonstrate the engine. They do not establish real product value.",
        ]
    )
