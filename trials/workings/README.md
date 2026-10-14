# Workings product trial

The broader 2026-10-07 cycle is in the
[product review](product-review/README.md) and [recovery experiment](recovery/README.md).
This document preserves the earlier attempt-comparison trial.

The founder chose an existing product for the broader Product Lab trial on
2026-09-30. Workings is the product under test. The earlier Lab Guide experiment
is parked on its own local branch.

## Audience and purpose

Use Workings' accepted audience: people who use AI assistants and can read simple
loops and objects, but have not built an agent loop. Keep its existing teaching
sequence: predict, change, run, inspect evidence, repeat, and transfer.

The selected journey is repairing the tool-using agent, then explaining what
changed in the run. The lesson already asks learners to compare results. Its
current player clears the previous trace when they edit a block. That behavior
is visible in the source and must be checked in the browser before calling it
an observed product problem.

The empathy hypothesis is that remembering an earlier trace adds effort while
the learner is already reasoning about unfamiliar code. No learner has confirmed
this yet. The founder is a domain reviewer, not a substitute for a new learner.

## Alternatives

- Current Workings: inspect one run at a time and remember or recreate the earlier run.
- Retained attempt: keep the previous program and trace available beside the new work.
- Guided comparison: show the changed blocks, observed outcomes, and first differing
  event for the same case, with access to both complete traces.

The first alternative favors learner-directed inspection. The second reduces
the work of locating a difference but could reveal too much or add screen clutter.
Neither can reveal an unrun result or suggest a repair in the independent challenge.

## What better means

The learner can explain what changed, point to the observed evidence, and apply
that understanding to another task. Human measures are explanation quality,
outside hints, wrong turns, effort, and fresh-task performance. They remain pending.

The automated measure is narrower: which facts needed for a before-and-after
explanation are available and correct in the actual browser. It cannot measure
understanding or declare the better teaching method. Existing completion checks,
prediction gates, help records, and simulation boundaries remain requirements.

Keep security, privacy, evidence integrity, correct assessment, accessibility,
recovery, and truthful claims as requirements. Balance clarity, learner control,
screen space, performance, maintainability, and novelty within those requirements.
Use the existing cabinet design and theme tokens. Put evidence next to the decision
it supports. Do not add a new visual identity or modify accepted lesson content.

## Source boundary

The original Workings checkout has local changes. The trial uses an isolated
worktree containing a verified copy of that exact working state. Its snapshot
commit is `197b10d`. Those inherited changes are the baseline, not improvements
produced by Product Lab. The original checkout is not edited or stashed.

The preparation record includes source hashes, the inherited patch, candidate
builds, evaluator output, and browser evidence. Local files can be opened from
the folder shared with the host. No hosted preview or external publication is
required. Production builds use the same source as the preview artifact.

## Trial decisions

The engineering comparison, author review, founder review, and learner trial are
separate. Keep unsuccessful runs. Revise when a check exposes a fault. Any lesson
about improved learning remains a hypothesis until fresh learner work tests it.
Unknown model and human costs remain unknown.

## Observations and revision

The baseline browser run confirmed that an edit removes the earlier trace and
program state. Both alternatives retain those facts. The metric checks four
specific facts: earlier events, the earlier edited setting, current events, and
the current edited setting. Current Workings exposes two of four after a repair;
both alternatives expose all four in the tested tasks. This measures available
evidence, not how well a learner uses it.

The first candidate review found a serious accessibility issue: the retained
trace could scroll but could not receive keyboard focus. Both candidates were
revised. They now provide keyboard access to that trace and a button beside the
current trace that moves to the comparison. Unrelated retry controls are omitted
from the first tool lesson's retained program. The original candidate builds and
failed reviews remain in the study.

The revised browser review passed 35 checks. It covered retained evidence,
prediction and completion rules, reset and interrupted runs, keyboard access,
both themes, narrow layouts, and automated accessibility checks. Direct screen
inspection covered the same files. No person using assistive technology has
reviewed them yet.

The full engine study completed 30 repair runs: three tasks, two repetitions,
and five frozen builds. The two revised alternatives tie on available evidence.
The engine's `current` field still names the first measured gain, `history`.
That build later failed its accessibility review and is not a product choice.
The review links use the corrected builds. Read the requirement reviews alongside
the metric decisions; neither field grants product acceptance.

Workings' 215 tests passed after the comparison logic was added. Its existing
browser sweep passed both complete agent lessons. The final focus and navigation
revision then passed the targeted browser checks and a production build. Product
Lab's 34 tests also passed. These checks do not establish learner understanding.

## Run and inspect

The current artifacts are under `generated/workings-trial-1/`. Open `index.html`
in the host browser through the shared folder. The three links open complete
Workings builds. They include the existing course content and require no server.

The original application is in `baseline/`. The review links use
`history-revised/` and `compare-revised/`. The first alternatives remain in
`history/` and `compare/` as evidence of the iteration.

To reproduce a build with the installed Workings development dependencies:

```bash
node trials/workings/build.mjs /path/to/workings-checkout /new/artifacts/baseline baseline
node trials/workings/build.mjs /path/to/revised-workings /new/artifacts/history history
node trials/workings/build.mjs /path/to/revised-workings /new/artifacts/compare compare
python3 trials/workings/prepare.py --artifacts /new/artifacts
```

The baseline must use the frozen source snapshot. Building the revised source
with the name `baseline` does not restore old behavior. Choose new output folders;
the builder preserves existing ones. The evaluator needs Python Playwright and
its Chromium browser. The development dependencies are local tools, not new
Product Lab runtime dependencies.

The revision workflow retains the first browser findings and uses these commands:

```bash
python3 trials/workings/verify_browser.py \
  --trial generated/workings-trial-1 \
  --workings /path/to/revised-workings
python3 trials/workings/revise.py --artifacts generated/workings-trial-1
```

The current run already contains those records. Reusing its identifiers is not
supported. `study/` contains the frozen candidates, raw evaluator outputs, and
reviews. `revised-results.json` and `revised-results.txt` show the whole iteration.
`baseline-source.json` identifies the inherited Workings files and commit.

## What to decide next

The engineering results do not distinguish the two revised alternatives. The
author's provisional preference is the guided comparison: it puts changed values
and the first differing event together. Its risk is extra guidance and screen
space. The retained-attempt version offers more self-directed inspection.

The founder should try the complete repair and describe what helped or confused
them. Record that as domain feedback against the chosen artifact. For learning
claims, use representative learners and equivalent fresh tasks, vary the order
of the alternatives, and retain help use and explanations. Repeating the same
task in each version adds practice and cannot isolate a learning benefit.

A scoped software-design lesson is proposed in the engine. Reserved reuse checks
are unused. No preferred teaching method, general learning gain, or product
acceptance has been established. Nothing has been pushed, merged, or published.
