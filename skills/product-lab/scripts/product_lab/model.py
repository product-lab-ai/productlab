"""Validate contracts and make decisions from repeated observations."""

import hashlib
import json
import math
import re
from statistics import mean


class LabError(ValueError):
    """An input or an experiment cannot support the requested operation."""


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise LabError(f"{label} must be a finite number")
    if not math.isfinite(value):
        raise LabError(f"{label} must be a finite number")
    return value


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,79}", value):
        raise LabError("IDs must use 1 to 80 lowercase letters, digits, underscores, or hyphens")
    return value


def exact_keys(value, required, optional=()):
    if not isinstance(value, dict):
        raise LabError("Expected a JSON object")
    missing = set(required) - value.keys()
    extra = value.keys() - set(required) - set(optional)
    if missing or extra:
        raise LabError(f"Invalid fields. Missing: {sorted(missing)}. Unknown: {sorted(extra)}")


def validate_contract(contract):
    from .context import keyed, validate_product

    exact_keys(
        contract,
        (
            "question",
            "evidence_kind",
            "metrics",
            "tasks",
            "repeats",
            "timeout_seconds",
            "product",
            "journey",
            "gates",
        ),
    )
    product = validate_product(contract["product"])
    journeys = keyed(product["journeys"], "journeys")
    outcomes = keyed(product["outcomes"], "outcomes")
    dimensions = keyed(product["dimensions"], "dimensions")
    essentials = keyed(product["essentials"], "essentials")
    if contract["journey"] not in journeys:
        raise LabError("The experiment must select a defined product journey")
    if not isinstance(contract["gates"], list):
        raise LabError("gates must be a list")
    gate_ids = set()
    for gate in contract["gates"]:
        exact_keys(gate, ("id", "requirement"))
        identifier(gate["id"])
        if gate["id"] in gate_ids:
            raise LabError("Duplicate gate ID")
        gate_ids.add(gate["id"])
        if gate["requirement"] not in essentials or not essentials[gate["requirement"]]["applies"]:
            raise LabError("Each gate must refer to an applicable product requirement")
    if not isinstance(contract["question"], str) or not contract["question"].strip():
        raise LabError("A product question is required")
    if contract["evidence_kind"] not in ("simulation", "automated"):
        raise LabError("Executable trials support simulation or automated evidence")
    count = contract["repeats"]
    if isinstance(count, bool) or not isinstance(count, int) or not 2 <= count <= 100:
        raise LabError("repeats must be an integer from 2 to 100")
    if not 0 < number(contract["timeout_seconds"], "timeout_seconds") <= 300:
        raise LabError("timeout_seconds must be in (0, 300]")
    metrics = contract["metrics"]
    if not isinstance(metrics, list) or not metrics:
        raise LabError("At least one metric is required")
    names = set()
    for metric in metrics:
        exact_keys(
            metric,
            ("name", "direction", "role", "min_gain", "max_loss", "outcome", "dimension"),
            ("limit", "aggregation"),
        )
        if metric["outcome"] not in outcomes:
            raise LabError("Each metric must refer to a defined user outcome")
        if outcomes[metric["outcome"]]["journey"] != contract["journey"]:
            raise LabError("A metric's outcome must belong to this experiment's journey")
        if metric["dimension"] not in dimensions:
            raise LabError("Each metric must refer to a defined quality dimension")
        name = identifier(metric["name"])
        if name in names:
            raise LabError(f"Duplicate metric: {name}")
        names.add(name)
        if metric["direction"] not in ("maximize", "minimize"):
            raise LabError("Metric direction must be maximize or minimize")
        if metric["role"] not in ("primary", "guardrail"):
            raise LabError("Metric role must be primary or guardrail")
        if metric.get("aggregation", "mean") not in ("mean", "worst"):
            raise LabError("Metric aggregation must be mean or worst")
        for key in ("min_gain", "max_loss"):
            if number(metric[key], key) < 0:
                raise LabError(f"{key} cannot be negative")
        if "limit" in metric:
            number(metric["limit"], "limit")
    if sum(m["role"] == "primary" for m in metrics) != 1:
        raise LabError("Exactly one primary metric is required")
    if not isinstance(contract["tasks"], list) or not contract["tasks"]:
        raise LabError("Tasks must be a nonempty list")
    ids, inputs = set(), set()
    families = {"development": set(), "validation": set()}
    for task in contract["tasks"]:
        exact_keys(task, ("id", "family", "split", "input"))
        identifier(task["id"])
        identifier(task["family"])
        if task["split"] not in families:
            raise LabError("Task split must be development or validation")
        fingerprint = digest(task["input"])
        if task["id"] in ids or fingerprint in inputs:
            raise LabError("Task IDs and input digests must be unique across both splits")
        ids.add(task["id"])
        inputs.add(fingerprint)
        families[task["split"]].add(task["family"])
    if not all(families.values()) or families["development"] & families["validation"]:
        raise LabError("Development and validation require distinct nonempty task families")
    return contract


def validate_output(output, contract):
    exact_keys(output, ("metrics", "gates"), ("feedback", "cost"))
    expected_gates = {gate["id"] for gate in contract["gates"]}
    if not isinstance(output["gates"], dict) or set(output["gates"]) != expected_gates:
        raise LabError("Evaluator must return every declared gate")
    if any(value not in ("pass", "fail", "unknown") for value in output["gates"].values()):
        raise LabError("Gate status must be pass, fail, or unknown")
    expected = {m["name"] for m in contract["metrics"]}
    if not isinstance(output["metrics"], dict) or set(output["metrics"]) != expected:
        raise LabError("Evaluator must return every declared metric, with no extra metrics")
    for name, value in output["metrics"].items():
        number(value, name)
    if "cost" in output and number(output["cost"], "cost") < 0:
        raise LabError("Evaluator cost cannot be negative")
    canonical(output)
    return output


def gate_decision(samples, contract):
    failures, unknowns = [], []
    for gate in contract["gates"]:
        statuses = [sample["output"]["gates"][gate["id"]] for sample in samples]
        if "fail" in statuses:
            failures.append(f"Required check failed: {gate['id']}")
        elif not statuses or "unknown" in statuses:
            unknowns.append(f"Required check is unresolved: {gate['id']}")
    if failures or unknowns:
        return {
            "status": "reject" if failures else "inconclusive",
            "reasons": failures or unknowns,
            "comparisons": [],
        }
    return None


def summarize(samples, contract, split):
    tasks = [t for t in contract["tasks"] if t["split"] == split]
    expected = {(t["id"], r) for t in tasks for r in range(contract["repeats"])}
    keys = [(s["task_id"], s["repeat"]) for s in samples]
    if len(keys) != len(set(keys)) or set(keys) != expected:
        raise LabError("Missing or duplicate task repetitions")
    for sample in samples:
        validate_output(sample["output"], contract)
    result = {}
    for metric in contract["metrics"]:
        name = metric["name"]
        aggregate = mean
        if metric.get("aggregation") == "worst":
            aggregate = min if metric["direction"] == "maximize" else max
        rounds = [
            aggregate(s["output"]["metrics"][name] for s in samples if s["repeat"] == r)
            for r in range(contract["repeats"])
        ]
        result[name] = {"mean": mean(rounds), "low": min(rounds), "high": max(rounds)}
    return result


def assess(candidate, references, contract):
    """Require observed bounds to satisfy limits against every protected reference."""
    failures, unknowns, details = [], [], []
    improvement = False
    epsilon = 1e-12
    for metric in contract["metrics"]:
        name = metric["name"]
        sign = 1 if metric["direction"] == "maximize" else -1
        cand = candidate[name]
        c_low, c_high = sorted((sign * cand["low"], sign * cand["high"]))
        if "limit" in metric:
            floor = sign * metric["limit"]
            if c_high < floor - epsilon:
                failures.append(f"{name} violates its absolute limit")
            elif c_low < floor - epsilon:
                unknowns.append(f"{name} may violate its absolute limit")
        for reference_name, reference in references.items():
            ref = reference[name]
            r_low, r_high = sorted((sign * ref["low"], sign * ref["high"]))
            low, high = c_low - r_high, c_high - r_low
            details.append({"metric": name, "reference": reference_name, "gain_range": [low, high]})
            if high < -metric["max_loss"] - epsilon:
                failures.append(f"{name} loses too much against {reference_name}")
            elif low < -metric["max_loss"] - epsilon:
                unknowns.append(f"{name} preservation is uncertain against {reference_name}")
            if metric["role"] == "primary" and reference_name == "current":
                improvement = low > metric["min_gain"] + epsilon
    if failures:
        status = "reject"
    elif unknowns:
        status = "inconclusive"
    elif not references:
        status = "baseline"
    elif not improvement:
        status = "inconclusive"
    else:
        status = "accept"
    return {
        "status": status,
        "reasons": (["Starting measurements recorded"] if status == "baseline" else failures)
        or unknowns
        or (
            ["Primary gain exceeds the threshold and observed loss limits hold"]
            if improvement
            else ["Primary improvement is not established"]
        ),
        "comparisons": details,
    }
