# Product Lab handoff

Date: 2026-09-30. The development repository is
[product-lab-ai/productlab](https://github.com/product-lab-ai/productlab), with
`main` as its default branch. The repository is private. No plugin has been
installed into assistant-wide settings.

## Current result

The first prototype contains a portable assistant skill, product context, an
experiment engine, a command line interface, behavioral tests, and a runnable
simulation. Read PRODUCT.md and PRODUCT.json before changing direction.

The active branch is `trial/workings`. The founder chose to improve an existing
product, Workings, rather than continue the assistant-proposed Lab Guide brief.
Read [the Workings trial](trials/workings/README.md) for the audience, alternatives,
evidence, commands, and remaining human review. Lab Guide is preserved on local
branch `trial/lab-guide` at `4e06a36` and is not the selected direction.

The Workings source checkout is
`/home/eparenti/agents/repos/side-projects/workings`. It had existing local changes.
Those were copied and verified in the isolated checkout
`/home/eparenti/agents/repos/side-projects/workings-productlab-trial`, on branch
`trial/productlab-learning-loop`. Commit `197b10d` records the inherited baseline.
Commit `6a6f685` adds the actual comparison feature and its local trial notes.
The source checkout is not edited or stashed. Preserve that distinction when
reviewing the trial's changes.

The trial improves access to evidence during an agent repair. Current Workings
clears the earlier program and trace on edit. Two alternatives retain them: an
inspectable previous attempt and a guided comparison of changed values and events.
The existing lesson content, engine, and grading rules are preserved. A new run
and prediction remain required after an edit.

The initial candidates exposed a keyboard access failure in their scrollable
retained traces. Revised builds fix that and add a direct comparison button.
The study preserves the failed requirement reviews. The revised browser review
passed 35 checks. Workings' 215 tests and its existing browser sweep of both agent
lessons passed. The final interaction revision passed the targeted browser checks
and a production build. Product Lab's 34 tests passed.

Open `generated/workings-trial-1/index.html` directly from the shared host folder.
The review links use `baseline`, `history-revised`, and `compare-revised`.
The full iteration is recorded in `revised-results.json` and the study directory.
All 30 declared repair runs completed. The engine's metric reference remains
`history`, which later failed its requirement review. The review links use the
corrected builds; metric reference selection is not product acceptance.
The automated metric counts four available comparison facts. It does not measure
learning, preference, or reduced effort. Founder feedback and learner results are
pending. Reserved reuse checks remain unused. Trial changes are local only.

The earlier branch `trial/experiment-review` compares the existing
report with two browser presentations. Read
[the trial brief](trials/experiment-review/README.md) for its audience, hypotheses,
task, criteria, and commands. The implementation is isolated under `trials/`.
The engine and installed plugin behavior are unchanged.

The latest prepared trial is `generated/review-trial-2/`. Each of the three views
passed source-fact checks on three cases with two repetitions. Both alternatives
received an inconclusive improvement result. There is no automated UX winner.
The revised page passed 32 browser checks, and the core suite passed 34 tests.
The local preview serves only `generated/review-trial-2/review/` on loopback port
8765 inside the development container. The user reported that this URL did not
work from their browser. The project folder is shared with the host at the same
path, so the corrected access path is the folder's `index.html` opened directly
in the host browser. The desktop opener accepted that request; visible host
access still needs confirmation. The trial brief records this first-use failure.

Human review is pending. Do not interpret the browser check responses as user
feedback. Reserved engineering validation is unused. Participant exports include
the reviewed report and candidate digests. Preserve those bindings when recording
later reviews. No trial changes have been pushed to GitHub.

The user explicitly added these requirements during implementation:

- Start with the audience, their problems, personas, empathy maps, and journeys.
- Connect measurements to that context so better has a defined meaning.
- Name the functional and non-functional quality choices and their tradeoffs.
- Treat security as a requirement, with other applicable requirements separate
  from optimization choices.
- Develop coherent, beautiful, distinctive work for the intended audience.
- Apply the same product context to Product Lab's own development.

The engine now requires metrics to refer to outcomes in the selected journey.
It records product requirements and craft intent. Required executable checks
cannot be offset by metric gains. Product reviews remain separate from the
experimental reference selected by the engine.

## Verified behavior

The source demo at `generated/verified-demo/` derives two conditional remedies
from development feedback. Completion in its reserved simulation cases changes
from one of three to three of three. A separate unsafe generalization is rejected.
The report leaves requirements and craft reviews pending.

The same demo ran from a built wheel in an isolated Python process. This checks
that the package includes its runtime code and example assets. The current wheel
is built under `generated/current-dist/`.

| Check | State |
| --- | --- |
| Behavioral suite | 34 tests passed on the final source |
| Ruff checks and formatting | Passed |
| Skill creator validator | Passed |
| Strict Claude plugin manifest validation | Passed |
| Source demo and report | Passed |
| Built package demo | Passed |
| Direct skill-guided development of an existing product | Workings trial run locally |
| Installed plugin discovery and invocation in each supported host | Not run |
| Real user benefit or general lesson transfer | Not established |

The Claude validator accepts the plugin root. Passing a skill-only directory to
that command reports a missing plugin manifest; use the skill creator validator
for the skill itself. An initial package probe from `/tmp` hit an unrelated
`copy.py` shadowing Python's library. The isolated package probe passed.

## Scope and remaining work

This engine runs trusted local evaluator code with the caller's permissions.
It is not a sandbox. It rejects changed snapshots, validates output, limits
trial time, retains evidence, and creates private evidence directories on POSIX.
Those checks do not establish production security or protect against a malicious
process with the same permissions.

The demo is deliberately small. Workload family labels differ across its splits,
but error types repeat. It demonstrates conditional rule reuse within that
fixture. It does not prove better product judgment, artistic quality, or broad
generalization. Personas and empathy maps remain labeled hypotheses.

Validation is consumed once per lab, including failed attempts. Files are not
hidden from the host. Cross-lab reuse and semantic overlap require experiment
review. Recorded reviewer identities are attributed, not authenticated.

Current cost totals include completed evaluator calls only. Full model, failed
attempt, human, and learning costs still need accounting before comparisons of
economic value.

Whole capabilities still deferred: autonomous experiment choice, GEPA integration,
real user study collection, evaluator calibration, and final product synthesis.
Browser evaluation exists in the local trials, not as a general engine adapter.
UPSTREAM.md records the projects to build on.

## Next useful trial

Collect the founder's response to the Workings alternatives. Use it to choose or
revise the comparison mechanism, then test a fresh learner task. Preserve the
existing study and source bindings. Do not call the gain in available browser
evidence a gain in understanding or learning speed.
