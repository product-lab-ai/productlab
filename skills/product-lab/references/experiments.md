# Running a product experiment

Use `scripts/lab.py` relative to the loaded skill. Resolve its absolute path once.
The plugin repository also has a `lab.py` convenience entrypoint at its root.

## Product context

Create a product JSON file matching `scripts/product_lab/assets/recovery/product.json`. The assistant
writes this file from the brief and evidence; the user reviews its meaning.

Every persona has a `basis` of `hypothesis`, `research`, or `user_statement`, with
a `source` explaining it. Empathy entries inherit that declared basis. Mixed
evidence needs explicit labels in the entries. These are attributed records,
not verified research credentials.

Every journey refers to a persona. Each outcome refers to a journey. Dimensions
describe intent, priority, tradeoff, boundary, and review. The `essentials` list
addresses each required category. An inapplicable item requires a reason;
security always applies. `craft` records the intended character of the experience
and how to review it directly.

Inspect the product picture:

```bash
python3 /path/to/product-lab/scripts/lab.py brief --product product.json
```

## Freeze the experiment

Use `scripts/product_lab/assets/recovery/contract.json` as a complete format example. `product` can
be an inline object or a path relative to the contract. Initialization resolves
the file and stores its complete contents. Later edits do not change the study.

- `journey` chooses one journey for this study.
- Each metric names its `outcome` and `dimension` in the product context.
- Exactly one metric is `primary`. Others are protected `guardrail` metrics.
- `min_gain` is the improvement required for the primary. `max_loss` is an
  absolute cumulative loss allowance, separate from measurement variability.
- `limit` is an optional absolute minimum for maximization or maximum for minimization.
- `aggregation` is `mean` by default. Use `worst` when a failure must not be
  hidden by other successful tasks.
- `gates` name required executable checks and the applicable requirement they test.
  A failed gate rejects a candidate. An unknown gate prevents acceptance.
- Tasks need unique IDs, input contents, and separate family names across
  development and validation. Family names alone do not establish substantive novelty.
- `repeats` repeats the same candidate and task set. Observed ranges are not
  confidence intervals or guarantees about future users.

If intent or the evaluator changes, start a new study and remeasure references.
Do not silently carry measurements across changed definitions of better.

```bash
python3 /path/to/product-lab/scripts/lab.py init \
  --lab /path/to/new-study --contract contract.json --evaluator evaluator
python3 /path/to/product-lab/scripts/lab.py register \
  --lab /path/to/new-study --id baseline --candidate prototype \
  --hypothesis 'This approach supports the selected journey'
python3 /path/to/product-lab/scripts/lab.py run \
  --lab /path/to/new-study --id baseline-run --candidate baseline
```

Each candidate and evaluator is copied before execution. `.git`, `__pycache__`,
`.venv`, `node_modules`, and `.product-lab` are excluded. Snapshots have a 50 MB
limit and reject symlinks and special files. External dependencies and host
configuration are not captured. Use an evaluator appropriate to that boundary.

## Evaluator interface

An evaluator directory must contain `evaluate.py`. The engine runs it in a new
working directory for every observation. It receives one JSON object on stdin:

```json
{"candidate_dir":"/snapshot/path","task":{"input":"value"},"task_id":"case-1","repeat":0}
```

Return a JSON object on stdout. Log diagnostics to stderr:

```json
{"metrics":{"completion":1,"unsafe_actions":0},"gates":{"no-force-restart":"pass"},"feedback":{"reason":"Observed result"},"cost":0}
```

All metrics and gates must be present. Gate values are `pass`, `fail`, or `unknown`.
Metric values must be finite numbers. Omit `cost` when unknown. The engine reports
unknown cost separately; a missing cost is not evidence that a run was free.

The evaluator is trusted local executable code. It can use local tools but must
obey the user's resource and data boundaries. The engine does not provide isolation
against malicious code. Timeout handling terminates the process group on POSIX.
Raw stdout and stderr remain on disk for completed and failed attempts.

## Test a lesson

Build a candidate that applies the proposed lesson. Register it and describe its
development evidence before using validation. The comparison uses the current
experimental reference plus the original version on the reserved task set.
Use a candidate that differs from the current reference.

```bash
python3 /path/to/product-lab/scripts/lab.py register \
  --lab /path/to/new-study --id learned --candidate improved-prototype \
  --hypothesis 'The proposed lesson helps a new task family'
python3 /path/to/product-lab/scripts/lab.py lesson \
  --lab /path/to/new-study --id scoped-lesson --candidate learned \
  --statement 'Apply this lesson under the recorded conditions' --evidence baseline-run
python3 /path/to/product-lab/scripts/lab.py validate \
  --lab /path/to/new-study --id transfer --lesson scoped-lesson
```

Validation is consumed before execution, even if a process fails. The engine
prevents further adaptation within that study. It does not hide task files from
the host or detect reuse across separately created labs. Treat exposure and
cross-study reuse as experiment-design responsibilities.

## Review the whole product

Record an attributed review against `craft` or a requirement ID. The evidence
file should state what was inspected, what was found, and its limits.

```bash
python3 /path/to/product-lab/scripts/lab.py review \
  --lab /path/to/new-study --id craft-1 --candidate learned --area craft \
  --verdict unknown --reviewer 'assistant' --note 'Real user review is pending' \
  --evidence review-notes.txt
python3 /path/to/product-lab/scripts/lab.py report --lab /path/to/new-study
```

Reviewer identity is caller supplied. A recorded pass is a reported pass.
The engine does not authenticate a human or certify a requirement. Failed
executable checks remain visible even if a later review reports a pass.
All required reviews passing produces `ready_for_owner_review`, never release approval.

Use `report --json` for complete records. After an interrupted process has stopped,
`recover --lab /path/to/study --id run-id` marks it failed and clears the active
run. It preserves any consumed validation state.
