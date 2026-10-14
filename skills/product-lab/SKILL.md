---
name: product-lab
description: Develop or improve a product from a brief, prototype, or existing implementation through product investigation, distinct alternatives, experiments, synthesis, and tested lessons. Use when deciding which product changes would help its users and carrying them through to a working result.
---

Help the user build a useful, coherent, distinctive product for a defined audience.
Work backward from the actual experience to the customer problem, then develop
and test useful improvements across the product. Choosing experiments, producing
strong alternatives, and retaining experience are parts of the same workflow.
The user owns product intent, taste, and acceptance. Supply product judgment,
working alternatives, and evidence. Do the drafting and technical translation.

## Ground the product

Read the existing product context and live implementation first. Preserve accepted
choices. For a new idea, draft the audience, problem, current substitute, desired
outcomes, and smallest complete journey before choosing metrics or architecture.
Use the user's statements as evidence. Label inferred personas, empathy maps, and
market claims as hypotheses. Never invent interviews or user quotations.

When starting from an existing product, or once an initial prototype can be
operated, use [references/product-review.md](references/product-review.md).
Inspect complete journeys, including failed attempts and interruption, before
limiting the work to a feature. Preserve strengths, accepted product choices,
local changes, and earlier evidence. Work on an isolated candidate when needed.

Build a compact product context with:

- Personas defined by situation, needs, and access constraints.
- Empathy maps: what the person says, thinks, does, and feels, with a stated basis.
- Journeys covering the trigger, actions, pain, needs, and important failure states.
- Outcomes that explain what the audience should be able to do or experience.
- Functional and non-functional quality dimensions with priorities, allowed
  tradeoffs, minimum expectations, and a review method.
- Requirements for security, privacy, data integrity, core correctness,
  accessibility, recovery, honesty, and applicable safety.
- Craft intent: intended meaning, audience effect, distinctive character,
  things to avoid, and prompts for reviewing the whole experience.

An initial context is a revisable hypothesis. Fill it from available evidence and
show useful options. Ask only for decisions that materially change the product.
Do not turn the context into a questionnaire or treat completed fields as research.

Read [references/experiments.md](references/experiments.md) when making the context
executable or running the engine. The example in `scripts/product_lab/assets/recovery/` is a simulation,
not a recommended product direction or evidence about actual operators.

## Shape and build

Choose the problem before the feature. Connect each opportunity to an observed
issue or an explicitly labeled hypothesis about the audience. Consider competing
explanations and specify what would change the decision. Rank a short list by
customer consequence, evidence, cost, and risk. Explain the selection; do not
hide conflicting requirements inside one score.

Explore materially different ways to solve the audience's problem. Explain each
mechanism, its experience, likely benefit, cost, and hardest assumption. Bring a
clear recommendation and a reason someone might reject it.

Use prototypes that expose the uncertain part of the journey. A visual question
needs suitable visual finish. An interaction question needs working interaction.
A feasibility question needs the real technical behavior. Select the next
experiment for the decision it could change and its full cost.

For interfaces, develop information hierarchy, content, layout, type, interaction,
and complete states around the audience and intended meaning. Use suitable design
tools available in the host. Review the result by operating it in its actual
medium. Generic visual polish is insufficient evidence of product fit.

## Judge the work

Tie every metric to a defined user outcome and journey. Separate:

- Requirements a candidate must satisfy. Other gains cannot compensate for a failed check.
- Quality dimensions where a deliberate tradeoff is possible within agreed limits.
- Direct judgments of clarity, coherence, beauty, and distinctive character.

Run executable checks where they fit. Retain uncertainty when evidence is missing.
Use representative people for claims about their needs and experience. Simulated
personas can suggest issues and experiments; they cannot establish real demand.

Engine acceptance changes an experimental reference only. Security and other
product requirements still need evidence appropriate to the real product. Craft
needs direct review. Record who reviewed what and the exact candidate. Do not
attribute a model's opinion to a human or call review records certification.

## Learn and synthesize

Capture a proposed lesson with its conditions, evidence, counterexamples, and
intended use. A useful explanation is a candidate lesson. Test whether applying
it improves fresh work against the current method, including its cost.

Retain decisions and failed alternatives as the work proceeds. Keep the owner's
preferences separate from observations about customers. Before reusing a lesson,
explain the shared problem and the differences that might invalidate it. Simple
retrieval of earlier decisions is a useful reference for evaluating more complex
learning methods. Agreement among reviews of the same evidence is not replication.

The bundled engine reserves a separate task split for one final comparison.
Freeze the lesson before that comparison. Once those results are exposed,
further adaptation needs fresh validation tasks. Do not call repeated use of
the same data independent confirmation.

Before a final build, revisit the complete product context and accumulated
evidence. Explain the selected mechanism and discarded alternatives. Build a
coherent whole and evaluate that whole again. Reusing individually successful
parts does not establish a successful combination.

## Execution scope

Run `scripts/lab.py` with Python 3.11 or later. The engine has no external runtime
dependencies and no model API calls. It runs trusted local evaluator code with
the caller's permissions. It is not a sandbox. Inspect an unfamiliar evaluator
before executing it, and stay within the user's existing action authorization.

Plugin use does not authorize external publishing, contacting users, production
changes, or additional paid services. Keep existing approvals and user limits.
Do not install or enable other plugins just because this skill mentions a capability.
