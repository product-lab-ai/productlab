"""Report required reviews separately from measured experiment improvement."""

import hashlib
from pathlib import Path

from .context import keyed
from .model import LabError, identifier
from .storage import now


def record_review(lab, review_id, candidate_id, area, verdict, reviewer, note, evidence):
    identifier(review_id)
    candidate = lab.verify(candidate_id)
    essentials = keyed(lab.contract["product"]["essentials"], "essentials")
    if area != "craft" and (area not in essentials or not essentials[area]["applies"]):
        raise LabError("Review area must be craft or an applicable requirement ID")
    if verdict not in ("pass", "fail", "unknown"):
        raise LabError("Review verdict must be pass, fail, or unknown")
    if not reviewer.strip() or not note.strip():
        raise LabError("A review needs an attributed reviewer and a reason")
    evidence = Path(evidence)
    if evidence.is_symlink() or not evidence.is_file() or evidence.stat().st_size > 1_000_000:
        raise LabError("Review evidence must be a regular file no larger than 1 MB")
    folder = lab.root / "reviews" / review_id
    if folder.exists():
        raise LabError("Review ID already has evidence")
    folder.mkdir(parents=True)
    data = evidence.read_bytes()
    (folder / "evidence.txt").write_bytes(data)
    record = {
        "id": review_id,
        "candidate": candidate_id,
        "candidate_digest": candidate["digest"],
        "area": area,
        "verdict": verdict,
        "reviewer": reviewer,
        "note": note,
        "created_at": now(),
        "artifact": str(folder.relative_to(lab.root)),
        "evidence_digest": hashlib.sha256(data).hexdigest(),
        "attribution": "Caller supplied. Reviewer identity is not authenticated",
    }
    with lab.db:
        lab.put("review", review_id, record)
    return record


def quality_status(lab, candidate_id):
    candidate = lab.verify(candidate_id)
    product = lab.contract["product"]
    areas = {
        item["id"]: "pending" if item["applies"] else "not_applicable"
        for item in product["essentials"]
    }
    areas["craft"] = "pending"
    # A failed required check remains visible even when a later review reports a pass.
    observed = {}
    for run in lab.all("run"):
        lab.verify_evidence(run)
        samples = run.get("samples", {}).get(candidate_id, [])
        for gate in lab.contract["gates"]:
            values = [sample["output"]["gates"][gate["id"]] for sample in samples]
            if "fail" in values:
                observed[gate["requirement"]] = "fail"
    for review in lab.all("review"):
        if review["candidate"] != candidate_id:
            continue
        if review["candidate_digest"] != candidate["digest"]:
            raise LabError("Review refers to a different candidate snapshot")
        path = lab.root / review["artifact"] / "evidence.txt"
        if (
            not path.is_file()
            or path.is_symlink()
            or hashlib.sha256(path.read_bytes()).hexdigest() != review["evidence_digest"]
        ):
            raise LabError("Review evidence changed")
        areas[review["area"]] = (
            "reported_pass" if review["verdict"] == "pass" else review["verdict"]
        )
    areas.update(observed)
    if "fail" in areas.values():
        status = "requirements_failed"
    elif any(value in ("pending", "unknown") for value in areas.values()):
        status = "reviews_pending"
    else:
        status = "ready_for_owner_review"
    return {
        "candidate": candidate_id,
        "status": status,
        "areas": areas,
        "claim": "Review records describe their stated scope. They do not certify the product",
    }
