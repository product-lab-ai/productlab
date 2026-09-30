"""Execute trusted local evaluators and retain failed as well as completed trials."""

import hashlib
import json
import os
import signal
import subprocess
import sys
import time

from .model import LabError, assess, canonical, gate_decision, summarize, validate_output


def terminate(process):
    if os.name == "posix":
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    elif process.poll() is None:
        process.kill()
    process.wait()


def measure(lab, candidate_id, task, repeat, folder):
    candidate = lab.verify(candidate_id)
    folder.mkdir(parents=True)
    request = {
        "candidate_dir": str(lab.root / candidate["path"]),
        "task": task["input"],
        "task_id": task["id"],
        "repeat": repeat,
    }
    (folder / "input.json").write_text(canonical(request) + "\n")
    command = [sys.executable, "-B", str(lab.root / "evaluator/evaluate.py")]
    started = time.monotonic()
    with (folder / "stdout.txt").open("wb") as stdout, (folder / "stderr.txt").open("wb") as stderr:
        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=stdout,
            stderr=stderr,
            cwd=folder,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            start_new_session=os.name == "posix",
        )
        try:
            process.communicate(
                canonical(request).encode(), timeout=lab.contract["timeout_seconds"]
            )
        except subprocess.TimeoutExpired as exc:
            terminate(process)
            raise LabError(f"Evaluator timed out on {task['id']}. Raw output is retained") from exc
        except BaseException:
            terminate(process)
            raise
        finally:
            # Evaluators must finish their children within the trial.
            if os.name == "posix":
                terminate(process)
    lab.verify(candidate_id)
    if process.returncode != 0:
        raise LabError(f"Evaluator exited {process.returncode} on {task['id']}. See stderr.txt")
    output_path = folder / "stdout.txt"
    if output_path.stat().st_size > 1_000_000:
        raise LabError("Evaluator output exceeds 1 MB")
    try:
        output = validate_output(json.loads(output_path.read_text()), lab.contract)
    except (ValueError, UnicodeError) as exc:
        raise LabError(f"Invalid evaluator result on {task['id']}: {exc}") from exc
    return {
        "task_id": task["id"],
        "repeat": repeat,
        "output": output,
        "wall_seconds": time.monotonic() - started,
        "digests": {
            name: hashlib.sha256((folder / name).read_bytes()).hexdigest()
            for name in ("input.json", "stdout.txt", "stderr.txt")
        },
        "artifact": str(folder.relative_to(lab.root)),
    }


def collect(lab, run, candidates, split):
    results = {candidate: [] for candidate in candidates}
    # Save every completed observation so a later failure does not erase it.
    run["samples"] = results
    tasks = [t for t in lab.contract["tasks"] if t["split"] == split]
    for repeat in range(lab.contract["repeats"]):
        for index, task in enumerate(tasks):
            order = candidates if (repeat + index) % 2 == 0 else list(reversed(candidates))
            for candidate_id in order:
                folder = lab.root / "runs" / run["id"] / candidate_id / f"{task['id']}-{repeat}"
                sample = measure(lab, candidate_id, task, repeat, folder)
                results[candidate_id].append(sample)
                with lab.db:
                    lab.put("run", run["id"], run, replace=True)
    return results


def run_development(lab, run_id, candidate_id):
    candidate = lab.verify(candidate_id)
    state = lab.get("state", "main")
    for reference_id in {state["original"], state["current"]} - {None}:
        reference = lab.get("run", reference_id)
        lab.verify(reference["candidate"])
        lab.verify_evidence(reference)
    run = lab.reserve(
        run_id, "development", {"candidate": candidate_id, "candidate_digest": candidate["digest"]}
    )
    try:
        samples = collect(lab, run, [candidate_id], "development")[candidate_id]
        summary = summarize(samples, lab.contract, "development")
        if run["current"] is None:
            # A baseline must itself meet declared absolute limits.
            decision = assess(summary, {}, lab.contract)
        else:
            for reference_id in (run["original"], run["current"]):
                lab.verify_evidence(lab.get("run", reference_id))
            original = lab.get("run", run["original"])["summary"]
            current = lab.get("run", run["current"])["summary"]
            decision = assess(summary, {"original": original, "current": current}, lab.contract)
        decision = gate_decision(samples, lab.contract) or decision
        run.update(status="complete", summary=summary, decision=decision)
        lab.finish(run, promote=decision["status"] in ("baseline", "accept"))
    except BaseException as exc:
        run.update(status="failed", error=str(exc))
        lab.finish(run)
        raise
    return run


def validate_lesson(lab, run_id, lesson_id):
    lesson = lab.get("lesson", lesson_id)
    state = lab.get("state", "main")
    if state["current"] is None:
        raise LabError("Establish an accepted baseline first")
    control_id = lab.get("run", state["current"])["candidate"]
    original_id = lab.get("run", state["original"])["candidate"]
    candidate_id = lesson["candidate"]
    control = lab.verify(control_id)
    candidate = lab.verify(candidate_id)
    lab.verify(original_id)
    for reference_id in (state["original"], state["current"]):
        lab.verify_evidence(lab.get("run", reference_id))
    if control["digest"] == candidate["digest"]:
        raise LabError("Lesson candidate must differ from the current accepted candidate")
    run = lab.reserve(
        run_id,
        "validation",
        {
            "lesson": lesson_id,
            "control": control_id,
            "original_candidate": original_id,
            "candidate": candidate_id,
        },
    )
    try:
        candidates = list(dict.fromkeys([original_id, control_id, candidate_id]))
        results = collect(lab, run, candidates, "validation")
        control_summary = summarize(results[control_id], lab.contract, "validation")
        original_summary = summarize(results[original_id], lab.contract, "validation")
        candidate_summary = summarize(results[candidate_id], lab.contract, "validation")
        decision = assess(
            candidate_summary,
            {"current": control_summary, "original": original_summary},
            lab.contract,
        )
        decision = gate_decision(results[candidate_id], lab.contract) or decision
        verdict = {"accept": "supported", "reject": "rejected", "inconclusive": "inconclusive"}[
            decision["status"]
        ]
        run.update(
            status="complete",
            summary=candidate_summary,
            control_summary=control_summary,
            original_summary=original_summary,
            decision=decision,
            lesson_verdict=verdict,
            claim=f"{verdict} on reserved {lab.contract['evidence_kind']} tasks only",
        )
        lab.finish(run)
    except BaseException as exc:
        run.update(status="failed", error=str(exc))
        lab.finish(run)
        raise
    return run


def costs(report):
    samples = [
        sample
        for run in report["runs"]
        for group in run.get("samples", {}).values()
        for sample in group
    ]
    return {
        "completed_evaluations": len(samples),
        "wall_seconds": sum(s["wall_seconds"] for s in samples),
        "reported_cost": sum(s["output"].get("cost", 0) for s in samples),
        "cost_unknown_evaluations": sum("cost" not in s["output"] for s in samples),
        "scope": "Completed evaluator calls. Failed calls and authoring cost are not measured",
    }
