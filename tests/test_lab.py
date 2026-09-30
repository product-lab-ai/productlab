import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/product-lab/scripts"))

from product_lab.context import read_contract, validate_product  # noqa: E402
from product_lab.demo import learn_policy, run_demo, write_policy  # noqa: E402
from product_lab.model import LabError, assess, summarize, validate_contract  # noqa: E402
from product_lab.quality import quality_status, record_review  # noqa: E402
from product_lab.runner import run_development, validate_lesson  # noqa: E402
from product_lab.storage import Lab  # noqa: E402

EXAMPLE = ROOT / "skills/product-lab/scripts/product_lab/assets/recovery"


def contract():
    return read_contract(EXAMPLE / "contract.json")


def bounds(completion, unsafe=0):
    return {
        name: {"mean": value, "low": value, "high": value}
        for name, value in (("completion", completion), ("unsafe_actions", unsafe))
    }


class DecisionTests(unittest.TestCase):
    def test_product_labs_own_context_meets_the_same_contract(self):
        validate_product(json.loads((ROOT / "PRODUCT.json").read_text()))

    def test_metrics_need_an_audience_and_journey_outcome(self):
        for field, value in (("outcome", "unknown"), ("dimension", "unknown")):
            spec = contract()
            spec["metrics"][0][field] = value
            with self.subTest(field=field), self.assertRaises(LabError):
                validate_contract(spec)

    def test_security_cannot_be_a_tradeoff_or_marked_inapplicable(self):
        product = contract()["product"]
        product["dimensions"][0]["id"] = "security"
        with self.assertRaisesRegex(LabError, "requirement"):
            validate_product(product)
        product = contract()["product"]
        product["essentials"][0]["applies"] = False
        with self.assertRaisesRegex(LabError, "always apply"):
            validate_product(product)

    def test_persona_assumptions_and_empathy_require_a_stated_basis(self):
        product = contract()["product"]
        product["personas"][0]["basis"] = "obvious"
        with self.assertRaisesRegex(LabError, "basis"):
            validate_product(product)
        product = contract()["product"]
        del product["personas"][0]["empathy"]["feels"]
        with self.assertRaises(LabError):
            validate_product(product)

    def test_gradual_loss_is_rejected_against_original(self):
        spec = contract()
        spec["metrics"] = [
            {
                "name": "speed",
                "direction": "maximize",
                "role": "primary",
                "min_gain": 0,
                "max_loss": 0,
            },
            {
                "name": "completion",
                "direction": "maximize",
                "role": "guardrail",
                "min_gain": 0,
                "max_loss": 0.02,
            },
        ]

        def result(speed, completion):
            return {
                name: {"mean": value, "low": value, "high": value}
                for name, value in (("speed", speed), ("completion", completion))
            }

        original = result(1, 0.95)
        current = original
        for speed, rate in [(1.1, 0.94), (1.2, 0.93)]:
            candidate = result(speed, rate)
            self.assertEqual(
                assess(candidate, {"original": original, "current": current}, spec)["status"],
                "accept",
            )
            current = candidate
        next_candidate = result(1.3, 0.92)
        self.assertEqual(assess(next_candidate, {"current": current}, spec)["status"], "accept")
        outcome = assess(next_candidate, {"original": original, "current": current}, spec)
        self.assertEqual(outcome["status"], "reject")
        self.assertTrue(any("original" in reason for reason in outcome["reasons"]))

    def test_uncertain_guardrail_is_not_preserved_by_default(self):
        candidate = bounds(1)
        candidate["unsafe_actions"]["high"] = 1
        result = assess(candidate, {"current": bounds(0.5)}, contract())
        self.assertEqual(result["status"], "inconclusive")

    def test_primary_gain_cannot_offset_a_known_guardrail_failure(self):
        self.assertEqual(
            assess(bounds(1, 1), {"current": bounds(0.2)}, contract())["status"], "reject"
        )

    def test_equal_results_do_not_establish_improvement(self):
        self.assertEqual(
            assess(bounds(1), {"current": bounds(1)}, contract())["status"], "inconclusive"
        )

    def test_minimize_direction_respects_loss_and_gain(self):
        spec = contract()
        spec["metrics"][0]["direction"] = "minimize"
        self.assertEqual(assess(bounds(0.5), {"current": bounds(1)}, spec)["status"], "accept")
        self.assertEqual(assess(bounds(1), {"current": bounds(0.5)}, spec)["status"], "reject")

    def test_task_id_and_content_leakage_are_rejected(self):
        for key in ("id", "input", "family"):
            with self.subTest(key=key):
                spec = contract()
                spec["tasks"][3][key] = copy.deepcopy(spec["tasks"][0][key])
                with self.assertRaises(LabError):
                    validate_contract(spec)

    def test_invalid_contracts_fail_with_actionable_errors(self):
        for change in (
            {"repeats": True},
            {"repeats": 1},
            {"tasks": []},
            {"evidence_kind": "human"},
            {"timeout_seconds": float("nan")},
            {"unknown": 1},
        ):
            with self.subTest(change=change), self.assertRaises(LabError):
                validate_contract({**contract(), **change})

    def test_missing_duplicate_and_nonfinite_observations_are_rejected(self):
        spec = contract()
        samples = [
            {
                "task_id": task["id"],
                "repeat": r,
                "output": {
                    "metrics": {"completion": 1, "unsafe_actions": 0},
                    "gates": {"no-force-restart": "pass"},
                },
            }
            for task in spec["tasks"]
            if task["split"] == "development"
            for r in range(spec["repeats"])
        ]
        self.assertEqual(summarize(samples, spec, "development")["completion"]["mean"], 1)
        for damaged in (samples[:-1], samples + samples[:1]):
            with self.assertRaises(LabError):
                summarize(damaged, spec, "development")
        samples[0]["output"]["metrics"]["completion"] = float("inf")
        with self.assertRaises(LabError):
            summarize(samples, spec, "development")

    def test_worst_case_guardrail_cannot_be_hidden_by_averaging(self):
        spec = contract()
        samples = [
            {
                "task_id": task["id"],
                "repeat": r,
                "output": {
                    "metrics": {"completion": 1, "unsafe_actions": int(task["id"] == "dev-1")},
                    "gates": {"no-force-restart": "pass"},
                },
            }
            for task in spec["tasks"]
            if task["split"] == "development"
            for r in range(spec["repeats"])
        ]
        self.assertEqual(summarize(samples, spec, "development")["unsafe_actions"]["mean"], 1)


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.lab = Lab.create(self.root / "study", contract(), EXAMPLE / "evaluator")

    def tearDown(self):
        self.lab.close()
        self.temp.cleanup()

    def baseline(self):
        self.lab.register("retry", EXAMPLE / "baseline", "Retry recovers failed jobs")
        return run_development(self.lab, "baseline", "retry")

    def learned(self):
        initial = self.baseline()
        directory = self.root / "learned"
        write_policy(directory, learn_policy(initial))
        self.lab.register("learned", directory, "Failure-specific remedies transfer")
        self.lab.lesson(
            "remedies", "learned", "Use observed remedies by failure type", ["baseline"]
        )
        return initial

    def test_snapshot_is_independent_of_working_source(self):
        source = self.root / "source"
        write_policy(source, {"default": ["retry"], "rules": {}})
        self.lab.register("retry", source, "Retry recovers jobs")
        (source / "policy.json").write_text("broken")
        run = run_development(self.lab, "baseline", "retry")
        self.assertEqual(run["decision"]["status"], "baseline")
        self.assertAlmostEqual(run["summary"]["completion"]["mean"], 1 / 3)

    def test_lesson_transfers_in_fixture_and_validation_cannot_be_reused(self):
        self.learned()
        run = validate_lesson(self.lab, "transfer", "remedies")
        self.assertEqual(run["lesson_verdict"], "supported")
        self.assertEqual(run["summary"]["completion"]["mean"], 1)
        self.assertEqual(self.lab.get("lesson", "remedies")["status"], "supported")
        with self.assertRaisesRegex(LabError, "consumed"):
            validate_lesson(self.lab, "repeat", "remedies")
        with self.assertRaisesRegex(LabError, "consumed"):
            run_development(self.lab, "adapt-after-test", "learned")
        self.assertEqual(self.lab.get("state", "main")["current"], "baseline")

    def test_unsafe_lesson_is_rejected_without_changing_accepted_candidate(self):
        self.baseline()
        directory = self.root / "unsafe"
        write_policy(directory, {"default": ["force_restart"], "rules": {}})
        self.lab.register("unsafe", directory, "Force restarting recovers jobs")
        self.lab.lesson("force", "unsafe", "Force restart", ["baseline"])
        run = validate_lesson(self.lab, "transfer", "force")
        self.assertEqual(run["lesson_verdict"], "rejected")
        self.assertEqual(self.lab.get("state", "main")["current"], "baseline")

    def test_accepted_development_run_updates_current_but_preserves_original(self):
        initial = self.baseline()
        directory = self.root / "learned"
        write_policy(directory, learn_policy(initial))
        self.lab.register("learned", directory, "The remedies improve recovery")
        run = run_development(self.lab, "improved", "learned")
        self.assertEqual(run["decision"]["status"], "accept")
        state = self.lab.get("state", "main")
        self.assertEqual((state["original"], state["current"]), ("baseline", "improved"))

    def test_snapshot_mutation_prevents_evaluation(self):
        self.baseline()
        (self.lab.root / "candidates/retry/policy.json").write_text("{}")
        with self.assertRaisesRegex(LabError, "snapshot changed"):
            run_development(self.lab, "mutated", "retry")

    def test_evaluator_mutation_prevents_evaluation(self):
        self.baseline()
        (self.lab.root / "evaluator/evaluate.py").write_text("print('{}')")
        with self.assertRaisesRegex(LabError, "snapshot changed"):
            run_development(self.lab, "mutated", "retry")

    def test_changed_raw_output_cannot_support_a_report_or_later_decision(self):
        run = self.baseline()
        sample = run["samples"]["retry"][0]
        (self.lab.root / sample["artifact"] / "stdout.txt").write_text("{}")
        with self.assertRaisesRegex(LabError, "evidence changed"):
            self.lab.report()
        with self.assertRaisesRegex(LabError, "evidence changed"):
            run_development(self.lab, "later", "retry")
        self.assertEqual(self.lab.get("state", "main")["current"], "baseline")

    def test_failures_remain_failed_and_do_not_become_a_baseline(self):
        directory = self.root / "broken"
        directory.mkdir()
        (directory / "policy.json").write_text("invalid-json")
        self.lab.register("broken", directory, "This candidate must not pass")
        with self.assertRaises(LabError):
            run_development(self.lab, "failure", "broken")
        self.assertEqual(self.lab.get("run", "failure")["status"], "failed")
        self.assertIsNone(self.lab.get("state", "main")["current"])
        self.assertTrue((self.lab.root / "runs/failure/broken/dev-1-0/stderr.txt").is_file())

    def test_failed_validation_still_consumes_reserved_tasks(self):
        self.baseline()
        directory = self.root / "broken"
        directory.mkdir()
        (directory / "policy.json").write_text("invalid-json")
        self.lab.register("broken", directory, "Malformed candidate")
        self.lab.lesson("bad", "broken", "Candidate lesson", ["baseline"])
        with self.assertRaises(LabError):
            validate_lesson(self.lab, "failure", "bad")
        self.assertTrue(self.lab.get("state", "main")["validation_used"])
        self.assertIsNone(self.lab.get("state", "main")["busy"])
        with self.assertRaisesRegex(LabError, "consumed"):
            validate_lesson(self.lab, "second", "bad")

    def test_lessons_require_completed_development_evidence(self):
        self.lab.register("retry", EXAMPLE / "baseline", "Retry is enough")
        with self.assertRaises(LabError):
            self.lab.lesson("unsupported", "retry", "General rule", ["missing"])

    def test_running_trial_blocks_another_and_recovery_preserves_consumption(self):
        self.baseline()
        self.lab.reserve("interrupted", "validation", {"candidate": "retry"})
        with self.assertRaisesRegex(LabError, "active"):
            run_development(self.lab, "second", "retry")
        self.lab.recover("interrupted")
        state = self.lab.get("state", "main")
        self.assertEqual(state["current"], "baseline")
        self.assertTrue(state["validation_used"])
        self.assertIsNone(state["busy"])

    def test_resume_uses_persisted_state(self):
        self.baseline()
        self.lab.close()
        self.lab = Lab(self.root / "study")
        self.assertEqual(self.lab.get("state", "main")["current"], "baseline")
        self.assertEqual(len(self.lab.report()["runs"]), 1)

    def test_metric_success_does_not_claim_craft_or_security_approval(self):
        self.learned()
        run = validate_lesson(self.lab, "transfer", "remedies")
        self.assertEqual(run["lesson_verdict"], "supported")
        quality = quality_status(self.lab, "learned")
        self.assertEqual(quality["status"], "reviews_pending")
        self.assertEqual(quality["areas"]["craft"], "pending")
        self.assertEqual(quality["areas"]["authorized-actions"], "pending")

    def test_reviews_are_attributed_and_bound_to_artifacts(self):
        self.baseline()
        evidence = self.root / "review.txt"
        evidence.write_text("Fixture review: judged one journey. Not an actual user study.\n")
        review = record_review(
            self.lab,
            "craft-review",
            "retry",
            "craft",
            "pass",
            "test-fixture",
            "A scoped fixture result",
            evidence,
        )
        self.assertEqual(quality_status(self.lab, "retry")["areas"]["craft"], "reported_pass")
        (self.lab.root / review["artifact"] / "evidence.txt").write_text("changed")
        with self.assertRaisesRegex(LabError, "Review evidence changed"):
            quality_status(self.lab, "retry")

    def test_reported_review_pass_cannot_hide_an_observed_required_failure(self):
        self.baseline()
        directory = self.root / "unsafe"
        write_policy(directory, {"default": ["force_restart"], "rules": {}})
        self.lab.register("unsafe", directory, "A proposed unsafe remedy")
        run_development(self.lab, "unsafe-run", "unsafe")
        evidence = self.root / "review.txt"
        evidence.write_text("A fixture review that contradicts the observed check.\n")
        record_review(
            self.lab,
            "incorrect-review",
            "unsafe",
            "safe-remedies",
            "pass",
            "fixture",
            "Reported pass",
            evidence,
        )
        quality = quality_status(self.lab, "unsafe")
        self.assertEqual(quality["status"], "requirements_failed")
        self.assertEqual(quality["areas"]["safe-remedies"], "fail")

    def test_symlink_candidate_is_rejected(self):
        directory = self.root / "linked"
        directory.mkdir()
        (directory / "policy.json").symlink_to(EXAMPLE / "baseline/policy.json")
        with self.assertRaisesRegex(LabError, "Unsupported snapshot"):
            self.lab.register("linked", directory, "Linked input")
        alias = self.root / "source-alias"
        alias.symlink_to(EXAMPLE / "baseline", target_is_directory=True)
        with self.assertRaisesRegex(LabError, "symlink"):
            self.lab.register("alias", alias, "Linked root")

    @unittest.skipUnless(os.name == "posix", "POSIX permission bits")
    def test_new_evidence_store_is_private_to_its_owner(self):
        self.assertEqual(self.lab.root.stat().st_mode & 0o077, 0)


class ExecutionTests(unittest.TestCase):
    def test_failed_or_unknown_gate_prevents_baseline_even_with_perfect_metrics(self):
        for verdict, expected in (("fail", "reject"), ("unknown", "inconclusive")):
            with self.subTest(verdict=verdict), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                evaluator = root / "evaluator"
                evaluator.mkdir()
                output = {
                    "metrics": {"completion": 1, "unsafe_actions": 0},
                    "gates": {"no-force-restart": verdict},
                }
                (evaluator / "evaluate.py").write_text(f"print({json.dumps(output)!r})\n")
                lab = Lab.create(root / "study", contract(), evaluator)
                try:
                    lab.register("retry", EXAMPLE / "baseline", "A metric gain cannot clear a gate")
                    run = run_development(lab, "trial", "retry")
                    self.assertEqual(run["decision"]["status"], expected)
                    self.assertIsNone(lab.get("state", "main")["current"])
                finally:
                    lab.close()

    def test_timeout_is_recorded_and_cannot_promote(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            evaluator = root / "evaluator"
            evaluator.mkdir()
            (evaluator / "evaluate.py").write_text("import time\ntime.sleep(10)\n")
            spec = contract()
            spec["timeout_seconds"] = 0.05
            lab = Lab.create(root / "study", spec, evaluator)
            try:
                lab.register("retry", EXAMPLE / "baseline", "Timeout is not success")
                with self.assertRaisesRegex(LabError, "timed out"):
                    run_development(lab, "timeout", "retry")
                self.assertEqual(lab.get("run", "timeout")["status"], "failed")
                self.assertIsNone(lab.get("state", "main")["current"])
            finally:
                lab.close()

    def test_public_cli_demo_and_report_work_from_another_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "demo"
            result = subprocess.run(
                [sys.executable, str(ROOT / "lab.py"), "demo", "--output", str(output)],
                cwd=directory,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            lab = Lab(output / "study")
            try:
                self.assertEqual(lab.get("lesson", "conditioned-remedies")["status"], "supported")
            finally:
                lab.close()
            report = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "lab.py"),
                    "report",
                    "--lab",
                    str(output / "study"),
                    "--json",
                ],
                cwd=directory,
                capture_output=True,
                text=True,
            )
            self.assertEqual(report.returncode, 0, report.stderr)
            self.assertEqual(json.loads(report.stdout)["state"]["current"], "baseline")

    def test_demo_does_not_overwrite_existing_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(LabError, "already exists"):
                run_demo(Path(directory))


if __name__ == "__main__":
    unittest.main()
