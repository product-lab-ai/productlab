"""Connect product judgment to people, journeys, and intended outcomes."""

import json
from pathlib import Path

from .model import LabError, exact_keys, identifier

ESSENTIALS = {
    "security",
    "privacy",
    "data_integrity",
    "correctness",
    "accessibility",
    "recovery",
    "honesty",
    "safety",
}


def text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise LabError(f"{label} needs a nonempty explanation")


def strings(value, label, *, allow_empty=False):
    if not isinstance(value, list) or (not value and not allow_empty):
        raise LabError(f"{label} must be a list of explanations")
    for item in value:
        text(item, label)


def keyed(items, label):
    if not isinstance(items, list) or not items:
        raise LabError(f"{label} must be a nonempty list")
    result = {}
    for item in items:
        if not isinstance(item, dict) or "id" not in item:
            raise LabError(f"Every {label} entry needs an ID")
        key = identifier(item["id"])
        if key in result:
            raise LabError(f"Duplicate {label} ID: {key}")
        result[key] = item
    return result


def validate_product(product):
    exact_keys(
        product,
        (
            "name",
            "purpose",
            "personas",
            "journeys",
            "outcomes",
            "dimensions",
            "essentials",
            "craft",
            "non_goals",
        ),
    )
    text(product["name"], "Product name")
    text(product["purpose"], "Product purpose")
    personas = keyed(product["personas"], "personas")
    for persona in personas.values():
        exact_keys(persona, ("id", "name", "context", "needs", "basis", "source", "empathy"))
        for field in ("name", "context", "source"):
            text(persona[field], f"Persona {field}")
        if persona["basis"] not in ("hypothesis", "research", "user_statement"):
            raise LabError(
                "Persona basis must distinguish hypotheses, research, and user statements"
            )
        strings(persona["needs"], "Persona needs")
        exact_keys(persona["empathy"], ("says", "thinks", "does", "feels"))
        for field, entries in persona["empathy"].items():
            strings(entries, f"Empathy {field}")
    journeys = keyed(product["journeys"], "journeys")
    for journey in journeys.values():
        exact_keys(journey, ("id", "persona", "trigger", "steps"))
        if journey["persona"] not in personas:
            raise LabError("Every journey must refer to a defined persona")
        text(journey["trigger"], "Journey trigger")
        for step in keyed(journey["steps"], "steps").values():
            exact_keys(step, ("id", "action", "pain", "need"))
            for field in ("action", "pain", "need"):
                text(step[field], f"Journey step {field}")
    outcomes = keyed(product["outcomes"], "outcomes")
    for outcome in outcomes.values():
        exact_keys(outcome, ("id", "journey", "description"))
        if outcome["journey"] not in journeys:
            raise LabError("Every outcome must refer to a defined journey")
        text(outcome["description"], "Desired outcome")
    for dimension in keyed(product["dimensions"], "dimensions").values():
        exact_keys(dimension, ("id", "intent", "priority", "tradeoff", "boundary", "review"))
        if dimension["id"] in ESSENTIALS:
            raise LabError(f"{dimension['id']} is a requirement, not a tradeoff dimension")
        if dimension["priority"] not in ("primary", "supporting"):
            raise LabError("Dimension priority must be primary or supporting")
        for field in ("intent", "tradeoff", "boundary", "review"):
            text(dimension[field], f"Quality dimension {field}")
    categories = set()
    for essential in keyed(product["essentials"], "essentials").values():
        exact_keys(
            essential, ("id", "category", "requirement", "verification", "applies", "reason")
        )
        if essential["category"] not in ESSENTIALS:
            raise LabError(f"Unknown essential category: {essential['category']}")
        categories.add(essential["category"])
        if not isinstance(essential["applies"], bool):
            raise LabError("Requirement applicability must be true or false")
        if essential["category"] == "security" and not essential["applies"]:
            raise LabError("Security requirements always apply")
        for field in ("requirement", "verification", "reason"):
            text(essential[field], f"Essential {field}")
    if categories != ESSENTIALS:
        raise LabError(
            f"Address each essential category. Missing: {sorted(ESSENTIALS - categories)}"
        )
    exact_keys(
        product["craft"],
        ("intent", "audience_effect", "distinctive_character", "anti_goals", "review_prompts"),
    )
    for field in ("intent", "audience_effect", "distinctive_character"):
        text(product["craft"][field], f"Craft {field}")
    strings(product["craft"]["anti_goals"], "Craft anti-goals")
    strings(product["craft"]["review_prompts"], "Craft review prompts")
    strings(product["non_goals"], "Non-goals", allow_empty=True)
    return product


def read_contract(path):
    path = Path(path)
    contract = json.loads(path.read_text())
    if isinstance(contract, dict) and isinstance(contract.get("product"), str):
        contract["product"] = json.loads((path.parent / contract["product"]).read_text())
    return contract


def product_text(product):
    validate_product(product)
    lines = [product["name"], product["purpose"], ""]
    for persona in product["personas"]:
        lines.extend(
            [
                f"For: {persona['name']} ({persona['basis']})",
                persona["context"],
                f"Needs: {'; '.join(persona['needs'])}",
                f"Basis: {persona['source']}",
            ]
        )
    for journey in product["journeys"]:
        lines.extend(
            [
                "",
                f"Journey: {journey['id']} for {journey['persona']}",
                f"Starts when: {journey['trigger']}",
            ]
        )
        for step in journey["steps"]:
            lines.append(f"  {step['action']}. Need: {step['need']}")
    lines.extend(["", "Desired outcomes:"])
    lines.extend(f"  {outcome['id']}: {outcome['description']}" for outcome in product["outcomes"])
    lines.extend(["", "Quality choices:"])
    for dimension in product["dimensions"]:
        lines.extend(
            [
                f"  {dimension['id']} ({dimension['priority']}): {dimension['intent']}",
                f"    Tradeoff: {dimension['tradeoff']}",
                f"    Limit: {dimension['boundary']}",
            ]
        )
    lines.extend(
        [
            "",
            f"Intended experience: {product['craft']['intent']}",
            f"Distinctive character: {product['craft']['distinctive_character']}",
            "",
            "Requirements:",
        ]
    )
    for essential in product["essentials"]:
        status = "required" if essential["applies"] else "not applicable"
        lines.append(f"  {essential['id']} ({status}): {essential['requirement']}")
    return "\n".join(lines)
