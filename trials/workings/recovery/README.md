# Workings interruption recovery experiment

The first run is complete. Read [RESULTS.md](RESULTS.md) and open
`generated/workings-product-review-1/index.html` for the runnable local review.

Question: does restoring the current step also recover the unfinished activity,
or does Workings need a separate draft record?

The first comparison covers the two existing AI agent lessons. General course
recovery, free-play drafts, multiple tabs, cross-device accounts, and the earlier
attempt-comparison feature are outside this prototype.

## Alternatives and declared decision

- Baseline: the captured current Workings product.
- Bookmark: save the current agent lesson step and restore it after re-entry.
- Draft: also save the actual editable program, including edits not yet run.

Use the existing cabinet design and Back navigation. Save locally with the course
and lesson identity. Match the full lesson content and engine version. Validate
program operations, numeric bounds, and locked fields. Reset the prediction,
execution state, and current verdict. Preserve historical help and run evidence.
Storage failure must leave an operable lesson and an honest notice.

The primary measure is the fraction of two facts restored: current step and current
draft. Score the draft only when the correct step is restored. Both development
tasks contain a nondefault edit. They exercise observation handling and answer
termination. Repeat twice and use the worst task result. This is a functional
comparison, not a measurement of learning, preference, speed, or customer impact.

Required browser gates preserve past evidence, require a fresh prediction and run,
allow a fresh correct repair, show no page errors, and make no external requests.
Separately check malformed and stale records, course separation, blocked storage,
mobile layout, keyboard access, and accessibility on the new states. A failed
requirement prevents acceptance regardless of the metric.

Proceed with draft recovery as a review candidate only if it restores both facts
and passes the declared checks. A bookmark may still be preferred by learners if
reconstructing a draft helps practice or if the added persistence is unwelcome.
Ask about that in the existing learner pilot. Do not turn this automated result
into a teaching recommendation.

## Evidence and reproduction

The contract is saved in `contract.json` before scoring. The evaluator snapshots
include `journey.py`, copied from the existing trial's browser navigation helpers.
No retry replaces a scored run. Product Lab retains its own raw calls and snapshots.
Browser screenshots sit beside raw calls as review aids; the engine hashes its
input, stdout, and stderr, not those screenshots.

The reserved task covers the retry lesson. It remains unused in this development
comparison. Its content is inspectable and has appeared in earlier Workings work.
It is not a blind or semantically novel test of learning or general reuse.

The generated directory holds the original source manifest, immutable baseline,
isolated `candidate-source`, standalone builds, and `recovery-study`:

```sh
python3 trials/workings/capture.py --source /path/to/workings --output generated/new-review
```

Copy the captured source into a separate candidate directory, provide its existing
dependencies, then apply `candidate.patch` from that directory. The patch targets
the recorded baseline, including its local edits. Do not apply it to a different
Workings state without review. Build to new output folders:

```sh
node trials/workings/build.mjs generated/new-review/source generated/new-review/baseline baseline
node trials/workings/build.mjs generated/new-review/candidate-source generated/new-review/bookmark bookmark
node trials/workings/build.mjs generated/new-review/candidate-source generated/new-review/draft draft
python3 trials/workings/recovery/prepare.py --artifacts generated/new-review
```

The captured dependency lock and installed node_modules were used. Installed
dependencies were shared through a symlink, not copied or independently archived.
This is a local prototype, not a hermetic build or release.
