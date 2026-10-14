# Workings product review

The first Product Lab cycle under the broader plan selects interruption recovery.
The current product keeps historical practice evidence but loses the unfinished
step and program on reload. This is directly reproducible. Whether it makes
people abandon a lesson or learn less is still unknown.

## Product and evidence

Workings is a local teaching platform with AI and Ansible courses. Its cabinet
design, predictions, executable experiments, trace inspection, hints, and fresh
challenge form the current experience. The initial audience remains the proposed
pilot group: people who use assistants and read simple code but have not built an
agent loop. No learner interviews or pilot observations were collected here.

On 2026-10-07, `capture.py` copied and verified the actual 155 source files from
`feat/platform-foundation` at `f8508e0`, including local edits and new files.
The source checkout was preserved. Product Lab remains on `trial/workings`.
Its local `main` matched fetched `origin/main`, which was an ancestor of the active
branch. Workings' active branch matched its fetched remote branch before this work.

The local evidence is in `generated/workings-product-review-1/`:

- `source-manifest.json` identifies the exact working source.
- `baseline/` is a standalone build of that source.
- `observation-03/observations.json` records the completed browser inspection.
- `observation-01/` and `observation-02/` retain incomplete harness runs.
  One missed the coin screen after reload. The other assumed same-route navigation
  reset lesson state. These are observation-script faults, not product failures.

The browser visited both course entries, the sampling and Ansible lesson entries,
an invalid route, and all 11 steps of the tool-using agent lesson. It used supplied
repairs to reach the challenge. That proves an executable path, not comprehension.
The baseline passed its existing 210 tests. The review does not cover every lesson,
authoring workflow, browser, device, threat, or customer segment.

## Diagnosis

| Perspective | Finding and source | Consequence and uncertainty |
| --- | --- | --- |
| Customer value | The agent lesson connects a bounded program with visible events and matching code. `AgentLesson.tsx` and the completed journey show this. | A concrete learning activity exists. Demand and independent understanding remain untested. |
| Learning | The final challenge checks three cases. Hints and solution use remain recorded. The browser supplied correct operations to complete it. | Preserve help attribution. Completion alone cannot establish that someone can diagnose a new failure. |
| UX and reliability | Step 4 becomes step 1 after reload. An unrun `wrong-id` draft becomes the default `discard` program when the learner returns. Historical evidence survives. | Recovery needs separate records for current work and prior results. Frequency and customer impact need observation. |
| Evidence inspection | Editing clears the earlier trace. The prior comparison trial already implements two alternatives. | Keep that trial available. Do not duplicate it or declare a preferred teaching method without feedback. |
| Accessibility and craft | The inspected mobile repair screen had no horizontal page overflow and no axe violations. The cabinet, readable body text, code view, and control deck form a consistent design. | These checks cover one screen. Long content still needs scrolling; its effort is an author concern, not a measured learner problem. |
| Performance | The packaged baseline is about 1.34 MB. Lessons execute locally. No production timing study ran. | Do not propose a performance rewrite without a measured delay and target device. Eager lesson imports merit a later scaling check. |
| Security and privacy | Typed lesson parsing bounds programs and text; reviewed source bundles and digests constrain authoring acceptance. No external requests were observed in the inspected packaged journey. | Preserve those boundaries. This is source and journey inspection, not a security certification or dependency audit. Saved browser data needs validation before restoration. |
| Maintainability | Shared `LessonFlow`, program execution, evidence records, and teaching review already exist. `training/DESIGN.md` describes authoring review. | Extend shared state carefully. The authoring journey has not been timed or tested end to end in this cycle. |
| Differentiation | The lesson exposes deterministic causal steps and guided experiments. No required learner explanation is collected. | An experiment-selection exercise could test a distinct teaching mechanism. Its usefulness and novelty remain hypotheses; no market claim is made. |

Keep the existing `training/PILOT.md`. It already proposes learner tasks and
help tracking. Use it when arranging real observations with the founder.

## Opportunity shortlist

### 1. Return to unfinished work

The affected journey is editing an agent loop, leaving, and returning. The desired
outcome is to continue the same unfinished activity. The observation is direct.
One explanation is that both place and draft matter. A competing explanation is
that a step bookmark is sufficient and replaying the edit is useful practice.

Compare the current product, a step bookmark, and a bookmark with the actual draft.
This is a small local change. The main risk is restoring stale content or crediting
an old result. Require content and engine matching, validated operations, separate
historical evidence, and a fresh prediction and run. A failed requirement rejects
the candidate regardless of how much state it restores.

Select this first because the loss is demonstrated and the mechanisms are cheap
to distinguish. The automated test can establish recovery, not lower effort or
better learning. Human preference remains open.

### 2. Make pilot evidence usable

Workings saves help, attempts, cases, and completion locally, but has no participant
results export in the inspected UI. The pilot already needs those records. A small
export could reduce manual collection errors. The competing explanation is that a
facilitator's existing worksheet is enough for five participants.

First compare a synthetic participant's expected events with an exported record
and the existing worksheet. Include consent, clear scope, and no automatic upload.
Defer implementation until recovery is reviewed. This prepares measurement; it
does not itself establish learning benefit.

### 3. Ask the learner to choose a useful experiment

An ambitious extension would present two plausible causes and ask the learner to
choose a run that distinguishes them, inspect the evidence, and explain a repair.
This builds on the working simulation rather than adding decorative features.
The competing explanation is that clearer existing feedback is sufficient.

Begin with one manually authored fresh task and the existing player. Compare it
with a simpler explanation prompt before building a general generator. A learner
pilot must test independent diagnosis and help use. Defer because the suspected
gap and the proposed teaching benefit have not yet been observed with people.

## Recovery experiment

See [the experiment protocol](../recovery/README.md). Original Workings and the
earlier attempt-comparison study remain separate. New alternatives are built from
the verified source copy. No Gaia code, service, package, or dependency is used.

Product Lab's skill now includes this wider review and opportunity-selection
process in `references/product-review.md`. The local experiment engine supplies
its existing snapshots, declared metrics, required checks, and preserved results.
This is the first implementation slice of the plan. Autonomous selection and
useful transfer to another product are not established.
