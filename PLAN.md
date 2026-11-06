# Product Lab development plan

Product Lab takes a rough idea, an initial prototype, or an existing product
through a complete improvement cycle. It understands the product and its
customers, challenges its assumptions, develops useful alternatives, tests them,
and combines supported changes into a coherent product. Experience from each
cycle should improve later decisions.

The founder confirmed this direction on 2026-10-07 and selected Workings as the
first target. The phases below are the proposed execution sequence. The current
experiment engine supplies part of the process; this plan describes the broader
product we will develop around it.

## Decisions already made

- Support both a new prototype and an existing product. Begin with something
  people can operate, then work backward to the customer problem and assumptions.
- Develop all three capabilities together: choosing experiments, producing
  strong alternatives, and retaining useful experience between projects.
- Examine the whole product. Include customer value, UX, accessibility, craft,
  performance, reliability, security, maintainability, and useful new capabilities.
- Allow simplification, removal, and changes to the original premise alongside
  feature development. Existing structure is evidence to inspect, not a limit on
  the alternatives we can consider.
- Use Workings to develop and test Product Lab through actual product work.
- Treat Gaia as prior art and a reference for ideas only. Do not introduce it as
  a dependency or integration. See [UPSTREAM.md](UPSTREAM.md).
- Keep customer outcomes, product requirements, human judgment, and automated
  measurements distinct. A better metric alone does not establish a better product.

## The experience we are building

The builder brings a product or a brief and explains the intended audience and
constraints. Product Lab operates what exists, drafts its understanding, and
identifies the decisions that matter. For a new idea, it first builds the smallest
prototype needed to expose the uncertain behavior.

It then presents a few substantial opportunities. Each explains the customer
problem, supporting evidence, alternative mechanisms, tradeoffs, and a small test
that could change the decision. The assistant does the investigation, drafting,
implementation, and routine verification. The builder supplies product intent,
domain judgment, taste, and final acceptance.

The result of a cycle is an improved working product, an explanation of the
choices, the evidence and remaining limits, and scoped lessons available to later
work. A report without a useful product change is an intermediate result. A
decision to leave the product unchanged can also be valid when experiments do
not support the proposed changes.

## Current foundation

The repository already has product context, an assistant skill, a local experiment
engine, candidate snapshots, comparisons with original and current references,
requirement reviews, and one reserved lesson comparison per study. The implemented
contract is in [SPEC.md](SPEC.md).

The [Workings trial](trials/workings/README.md) compared the original repair
experience with retained attempts and guided comparison. It established access
to more comparison evidence in the tested browser tasks. Human preference,
reduced effort, and learning benefit remain unmeasured. The failed accessibility
reviews and corrected builds remain part of that record.

The next work broadens the diagnosis beyond that one mechanism. Missing feedback
on the existing trial does not prevent independent inspection of the product.
It does prevent claims about learner benefit or a preferred teaching method.

## Phase 1 Understand and diagnose Workings

Start from the live Workings checkout and its accepted product direction. Record
the branch, revision, local changes, dependencies, and relevant existing plans.
Preserve its uncommitted work. Before changing Workings, prepare an isolated copy
of the actual working state and verify its source manifest. Keep the earlier
trial as a separate historical baseline.

Workings is a general teaching platform with AI and Ansible subjects. Inspect
the full entry and course experience, then follow one complete tool-using agent
lesson in depth. Include a wrong attempt, feedback, a repair, an independent
challenge, and return after interruption. Check the existing teaching design and
learner pilot before proposing another process for them.

The initial learner group is a hypothesis drawn from the existing pilot: people
who use AI assistants and can read simple loops and conditions but have not built
an agent loop. Keep the broader platform audience open until there is evidence.

| Perspective | Investigation | Evidence to seek |
| --- | --- | --- |
| Customer value | What should the learner be able to do afterward, and why does it matter? | Stated goals, observed tasks, existing research, and current substitutes |
| Learning | Which decisions require understanding, and which can be completed by following cues? | Explanations, wrong attempts, help use, and performance on a fresh task |
| UX and accessibility | Where does the learner lose orientation, evidence, or control? | Operated journeys, keyboard access, small screens, and recovery behavior |
| Craft | Do content, controls, pacing, and the cabinet design support one clear experience? | Direct review of complete interactions, including error states |
| Performance | Where does delay interrupt the intended activity? | Repeatable measurements on a declared device and workload |
| Security and privacy | What data and code cross trust boundaries during import, authoring, and use? | Code paths, storage behavior, dependency checks, and focused misuse cases |
| Reliability | What happens when work is interrupted, storage fails, or content changes? | Recovery checks and preserved learner state |
| Maintainability | How difficult is it to create, verify, and revise another lesson? | The actual authoring journey and cost of a small change |
| Product differentiation | Where could a different mechanism solve the problem better? | Adjacent products, alternative teaching approaches, and customer evidence |

Keep findings separate from explanations. For example, disappearing evidence is
an observation; a claim that it causes poor learning needs learner evidence.
Several review perspectives can inspect the same issue, but their agreement does
not make the underlying observations independent.

Output: a concise product map, an evidence-backed diagnosis, and unresolved
questions. Every finding names the affected journey, source, consequence, and
uncertainty. Record strengths worth preserving as well as problems.

Exit: all perspectives have been considered, unsupported claims are labeled,
and there are concrete decisions that an experiment could change. The diagnosis
must not reduce Workings to the existing comparison trial.

## Phase 2 Select worthwhile opportunities

Develop a small set of distinct opportunities from the diagnosis. Describe the
problem before proposing a feature. For each opportunity, record:

- The audience, journey, desired outcome, and supporting observation.
- The proposed explanation and a plausible competing explanation.
- The mechanism that could help, including a simpler alternative.
- Expected benefit, evidence strength, effort, risk, and cost of being wrong.
- Requirements that must remain satisfied and likely conflicts with other gains.
- The smallest experiment, what it could establish, and what would reject it.

Prioritize clear requirement failures and consequential customer problems.
Prefer inexpensive tests of uncertain explanations before large implementations.
Include an ambitious opportunity when the diagnosis supports a real problem it
could solve. Do not force every review to produce a novel feature.

For Workings, distinguish hypotheses such as missing earlier evidence, difficulty
locating a relevant difference, and difficulty explaining its cause. These imply
different mechanisms. They are examples to investigate, not a selected backlog.

Output: a shortlist of about three opportunities and a reasoned first choice.
State why other opportunities are deferred. Avoid a single score that hides
requirements or disagreement.

Exit: the first opportunity has a specific customer outcome, distinguishable
alternatives, an affordable test, and explicit decision criteria. Routine choices
within accepted product intent can proceed without another approval ceremony.
Ask the founder when a choice changes that intent or needs missing domain judgment.

## Phase 3 Build and compare alternatives

For the selected opportunity, build two or three materially different mechanisms
at the scope needed to test them. Retain the original product as the reference.
Avoid spending on variants that cannot distinguish the competing explanations.

Use Product Lab's existing engine for snapshots, declared measures, required
checks, and preserved results. Use the host assistant and the target repository's
tools for implementation and inspection. Extend the engine only where this real
workflow exposes a repeated missing capability.

Tie each measure to the intended outcome. Declare protected behavior and limits
before the run. Keep product requirements separate from optimization choices.
Record model use, failed attempts, evaluation time, and human effort where
available; unknown cost stays unknown.

Use the evidence suited to the claim:

- Code and browser checks establish the particular behavior they exercise.
- Performance comparisons use the same declared workload and environment.
- Security checks state the threat and boundary actually examined.
- Founder feedback establishes attributed product judgment.
- Claims about comprehension, effort, or learning require representative people
  performing relevant tasks.

Reuse Workings' existing learner pilot as a starting point. Define a comparison
protocol before collecting observations. Use equivalent fresh tasks and vary
presentation order where appropriate. Repeating the same task creates practice
effects. A small pilot supports revision decisions, not a population-wide rate.
Participant access is organized with the user; do not invent participants or
contact people without instructions.

Output: runnable alternatives, frozen experiment records, failed results, and a
comparison that identifies support, rejection, and uncertainty. Verify that the
builder can open and operate the delivered artifacts through their actual access
path.

Exit: the evidence can support the intended decision, or the trial is explicitly
inconclusive with a defined reason and next step. Unavailable human evidence does
not become a simulated pass. Continue unrelated engineering work where possible.

## Phase 4 Integrate and review the whole product

Choose, revise, combine, or reject the alternatives using the recorded evidence
and product judgment. Explain the tradeoffs and retain rejected designs with the
reasons they were rejected.

Integrate supported changes into an isolated candidate. Recheck the complete
journey and its affected neighboring journeys. Combining individually useful
features can create clutter, conflicts, extra latency, or inconsistent teaching.
Review the resulting content, interactions, performance, accessibility, security,
and recovery together.

Output: one coherent Workings candidate, a short before-and-after explanation,
applicable verification, known limits, and the owner's acceptance state.

Exit: the candidate meets the declared requirements and supports the intended
customer outcome to the stated level of evidence. The owner decides product
acceptance. Publishing and deployment follow their own existing authorization.

## Phase 5 Test whether retained experience helps

Capture proposed lessons throughout the cycle, including unsuccessful changes.
Each lesson keeps its originating decision, conditions, source evidence,
counterexamples, uncertainty, and the action it suggests. Store founder preferences
separately from claims about customers.

Before another Workings opportunity or another product, retrieve relevant lessons
and explain why they might apply. State the differences that could invalidate
the analogy. Freeze the proposed use before fresh validation. Already exposed
tasks cannot count as new confirmation, even when copied into a new study.

Compare the current assistant workflow, simple retrieval of earlier decisions,
and the proposed learning method under comparable resources. Begin with explicit
records and simple retrieval. Build more elaborate discovery only if it finds
useful opportunities that those references miss.

Output: a record of whether retained experience changed the decision, improved
fresh work, caused harm, or added cost without benefit. Keep lessons scoped to
the evidence and revisit them when conditions change.

Exit: any claim of useful learning includes fresh outcomes and full cost limits.
Unproven lessons remain proposals. A failed transfer is evidence to retain.

## Product Lab implementation sequence

Develop the reusable workflow through Workings. Avoid building a general platform
before one complete improvement cycle works.

| Slice | Change in Product Lab | Proof required |
| --- | --- | --- |
| Product inspection | Extend the assistant workflow for importing a product, mapping journeys, and reviewing it from several perspectives | One Workings diagnosis grounded in actual behavior and sources |
| Opportunity selection | Keep findings, alternative explanations, opportunities, and selection reasons together | The chosen experiment follows from a customer problem and could change the decision |
| Experiment delivery | Reuse the engine and add only missing support for the selected trial | The builder operates alternatives and can inspect complete results and costs |
| Synthesis | Record the decision and review the integrated product | One coherent candidate passes the applicable whole-journey checks |
| Reuse | Retrieve scoped lessons, preserve contradictions, and test proposed transfer | A fresh comparison measures benefit and harm against simpler methods |

Use the existing product, candidate, run, review, and lesson records wherever
they fit. Initially keep diagnosis and opportunity reasoning in readable
repository documents that reference source artifacts. Add machine-readable
records when an actual command or comparison needs them. Do not create a second
evidence store or infer support from prose confidence.

The first workflow extension belongs in `skills/product-lab/SKILL.md` and its
reference guide. Changes to evidence semantics belong in the engine and require
behavior tests. Specific Workings code remains in the isolated Workings checkout.

## How we judge Product Lab itself

Judge the complete cycle by whether it finds consequential problems, develops
useful alternatives, produces a coherent improvement, and makes later work better
at an acceptable total cost. Review how well the builder understands the choices
and can redirect the process.

Compare with the strongest available ordinary assistant workflow. Where retained
learning is the claim, also compare with learning disabled and simple retrieval.
Keep task scope, resources, and assessment comparable. Do not tune the evaluation
on the same cases later presented as fresh evidence.

Document volume, proposal count, code volume, and automated passes are not measures
of customer benefit. If a cycle only produces more records, investigate or remove
the work that did not improve a decision.

## First implementation status

The 2026-10-07 cycle produced the
[Workings diagnosis and shortlist](trials/workings/product-review/README.md),
extended the assistant skill, and built the selected
[interruption recovery experiment](trials/workings/recovery/README.md).
The isolated original, bookmark, and draft builds completed 12 declared browser
evaluations. Draft recovery retained both the unfinished step and program while
requiring a fresh prediction and run. This is functional evidence. The workflow
is assistant-guided; autonomous selection and useful transfer remain unproven.

The original Workings checkout and earlier trial are preserved. The local review
entry is `generated/workings-product-review-1/index.html`. The broader plan remains
active, with product acceptance and fresh reuse evidence still to collect.

## Immediate work

1. Review draft recovery in the delivered Workings build. Record founder judgment
   separately from automated evidence and any learner observations.
2. Use the existing learner pilot to examine interruption, effort, and explanation
   when participants are available. Do not invent feedback or contact people
   without instructions.
3. Decide whether pilot evidence export is needed for that study or whether the
   existing worksheet is enough. Keep the more ambitious experiment-selection
   exercise as an explicit hypothesis.
4. Apply the proposed recovery lesson to fresh work and compare it with ordinary
   assistant work and simple retrieval. Existing exposed Workings tasks cannot
   establish general transfer.

The earlier retained-attempt comparison remains available for founder feedback.
It has not been combined with recovery because no preferred comparison mechanism
has been established with the user or learners.
