# Working on Product Lab

Read PRODUCT.md, PRODUCT.json, SPEC.md, and HANDOFF.md before changing direction.
Apply the repository's product context to its own development.

Preserve the user's intent: audience understanding, useful originality, rapid
experiments, coherent craft, and lessons that earn their place through evidence.
Security is a requirement. Do not trade it for a better product score.

Use plain English. Never use an em dash or doubled hyphens as punctuation.
Keep hypotheses, measured results, reported reviews, and human acceptance distinct.
Do not claim real user benefit from the bundled simulation.

Use `python3 -m unittest discover -s tests -v` for behavior checks. Use
`ruff check .` and `ruff format --check .` for Python changes. Tests should exercise
meaningful decisions, execution failures, evidence handling, or user commands.

Run evaluators only within their authorized scope. The prototype executes trusted
local code with the caller's permissions. It is not a sandbox.

Before editing an existing shared branch, inspect the remote state. Do not publish,
deploy, or change assistant-wide settings without authorization. The repository is
https://github.com/product-lab-ai/productlab, with `main` as its default branch.
