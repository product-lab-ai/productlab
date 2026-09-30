# Product Lab handoff

Date: 2026-09-30. The development repository is
[product-lab-ai/productlab](https://github.com/product-lab-ai/productlab), with
`main` as its default branch. The repository is private. No plugin has been
installed into assistant-wide settings.

## Current result

The first prototype contains a portable assistant skill, product context, an
experiment engine, a command line interface, behavioral tests, and a runnable
simulation. Read PRODUCT.md and PRODUCT.json before changing direction.

A local trial on branch `trial/experiment-review` now compares the existing
report with two browser presentations. Read
[the trial brief](trials/experiment-review/README.md) for its audience, hypotheses,
task, criteria, and commands. The implementation is isolated under `trials/`.
The engine and installed plugin behavior are unchanged.

The latest prepared trial is `generated/review-trial-2/`. Each of the three views
passed source-fact checks on three cases with two repetitions. Both alternatives
received an inconclusive improvement result. There is no automated UX winner.
The revised page passed 32 browser checks, and the core suite passed 34 tests.
The local preview serves only `generated/review-trial-2/review/` on loopback port
8765 when its server is running. Open the same folder's `index.html` directly
if the server has stopped.

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
| Live Codex or Claude product-development journey | Not run |
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
browser evaluation, real user study collection, evaluator calibration, and final
product synthesis. UPSTREAM.md records the projects to build on.

## Next useful trial

Use the skill on one real product brief through the first complete journey. Have
the builder review the audience and intended experience, operate distinct
prototypes, and judge whether Product Lab helped choose the next experiment.
Record the outcome and effort. Then compare with the strongest existing workflow
before expanding the engine or claiming a learning advantage.
