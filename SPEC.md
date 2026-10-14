# Product Lab: first executable slice

This specification describes the current experiment engine. The broader product
improvement workflow and its next implementation steps are in [PLAN.md](PLAN.md).
Workings is the first target for that development.

The user wants an assistant that starts with a loose product brief, builds and
tests alternatives, retains useful experience, and makes better decisions on
later work. This prototype supplies the experiment engine and an assistant skill.
The host assistant supplies product reasoning and implementation.

The first user is a developer using an assistant to explore a product. Their
current substitute is a coding workflow, ad hoc evaluations, and saved notes.
The central unresolved claim is that retained lessons improve later outcomes
enough to pay for the experiments that produced them.

## First journey

1. Define the audience, personas, empathy map, journey, desired outcomes, quality
   tradeoffs, requirements, and craft intent. Label hypotheses and their sources.
2. Freeze a question, metrics, loss limits, evaluator, and task splits. Every
   metric must refer to an outcome in the selected journey and a quality dimension.
3. Register a candidate and its hypothesis before running it.
4. Execute the evaluator on a snapshot of the candidate. Keep raw results.
5. Compare with both the starting version and the current experimental reference.
6. Propose a scoped lesson using completed development runs.
7. Freeze that lesson and its implementation. Compare it with the current
   accepted version on the reserved validation tasks exactly once.
8. Report support, rejection, or uncertainty with the observed cost and scope.
   Show pending product requirements and craft reviews separately.

The demo is a small simulated job recovery product. Its lesson is derived from
development failures. It tests the resulting policy on reserved workload
families. Its scores establish behavior in that simulation only.

## Rules for this prototype

- A metric improvement must exceed its declared minimum gain.
- Required executable checks cannot be offset by metric gains. Unknown checks
  prevent experimental acceptance. Broader product requirements and craft need
  attributed reviews whose evidence is bound to the candidate.
- Every protected metric is checked against the original and current versions.
- Loss tolerance and measurement noise are separate fields.
- Repeated measurements concern the same candidate and task. Ranges are
  conservative observed bounds, not statistical confidence intervals.
- An overlapping range produces uncertainty unless the full range satisfies
  the declared loss limit. Lack of a detected loss does not prove safety.
- The contract, evaluator, candidates, and lesson are bound to file digests.
- Failed runs and missing metrics cannot become successful decisions.
- Development and validation have distinct task IDs, input digests, and families.
- Validation is consumed before execution, including on failure. Retrying the
  same exposed tasks cannot supply fresh validation evidence.
- A supported lesson is scoped to the recorded experiment. Human product
  acceptance and general transfer remain separate claims.
- Local evaluators are trusted executable code. This version is not a sandbox.

The user requires audience grounding, explicit quality choices, and security as
a requirement. Other mechanisms are implementation choices for the first trial.

## Success and limits

This slice succeeds when a fresh checkout runs the full journey, detects gradual
regression, preserves incomplete evidence as incomplete, and rejects reuse of
validation data. It must show both a useful learned policy and a rejected policy.

The larger product succeeds only if real user outcomes improve at comparable
total cost. The first field comparison should use the strongest existing workflow,
this engine with learning disabled, and this engine with learned guidance.
Learning and evaluation costs count in that comparison.

The strongest counterargument is that the engine adds records and evaluation
cost without improving decisions. If learned guidance does not help on fresh
work, its claimed benefit remains unsupported.

Deferred whole capabilities: automatic experiment selection, human study
collection, evaluator calibration against people, GEPA integration, browser
automation, model calls, and automatic final-product synthesis. Existing upstream
tools remain candidates for those parts.
