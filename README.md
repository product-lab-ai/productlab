# Product Lab

An assistant skill and local experiment engine for building products around
their audience, testing alternatives, and checking whether lessons help later work.

This is a runnable research prototype. It uses Python 3.11 or later and the
standard library. The bundled demo needs no model, GPU, network, or installation.

## Try it

From this repository:

```bash
python3 lab.py brief --product PRODUCT.json
python3 lab.py demo --output generated/first-demo
python3 lab.py report --lab generated/first-demo/study
```

Choose a new output directory on each demo run. Existing evidence is preserved.
The demo observes failed recovery attempts, derives two conditional remedies,
and tests them on reserved jobs. A separate control tests a harmful generalization.
The examples demonstrate the machinery. Their repeated error types and invented
workload families do not establish real-world product improvement.

## What exists

- Product context: personas, empathy maps, journeys, outcomes, quality tradeoffs,
  requirements, and craft intent. Each metric refers to that context.
- Candidate and evaluator snapshots, predeclared hypotheses, raw observations,
  durable records, and digest checks before using evidence.
- Comparison with original and current references, required checks, observed
  variability, and explicit uncertainty.
- Proposed lessons and one reserved validation comparison per study.
- Review records for product requirements and craft, separate from metric gains.
- A portable assistant skill and plugin manifests for Codex and Claude Code.

The assistant shapes and builds the actual product. The engine executes its
trusted local evaluators. It does not yet choose experiments autonomously,
calibrate simulated users against people, or integrate GEPA or browser automation.

## Use through an assistant

Ask an assistant to read and use
[`skills/product-lab/SKILL.md`](skills/product-lab/SKILL.md) for your idea.
The skill includes its own scripts, reference guide, and complete example.
It drafts product context from available information; it does not ask the user
to fill out JSON or a long questionnaire.

The root portable manifest follows the
[OpenAI plugin packaging documentation](https://developers.openai.com/plugins/build/plugins).
Host compatibility manifests are also included. No user settings were changed
and no plugin was globally installed. Host execution still needs a real usage
trial. To test with Claude Code from a chosen project directory:

```bash
claude --plugin-dir /absolute/path/to/product-lab
```

Then ask it to use Product Lab on a product idea. For Codex, the skill can be
referenced by its local path, or the package can be added to a local marketplace
using the documented host workflow.

## Build on it

- [Product intent and first journey](PRODUCT.md)
- [Machine-readable product context](PRODUCT.json)
- [Current implementation scope](SPEC.md)
- [Evaluator and command guide](skills/product-lab/references/experiments.md)
- [Upstream comparison and reuse choices](UPSTREAM.md)
- [Current handoff](HANDOFF.md)

Run the behavioral checks:

```bash
python3 -m unittest discover -s tests -v
ruff check .
ruff format --check .
```

Ruff is an optional development tool. It is not a runtime dependency.

## First product trial

The [experiment-review trial](trials/experiment-review/README.md) compares the
current report with two working browser presentations. It uses verified engine
results and collects feedback about understanding the result and choosing the
next action. Automated checks pass; human review is pending.

## Evidence boundary

Observed ranges describe these repeated runs; they are not statistical confidence
intervals. Validation data is reserved by the workflow, not hidden from the host.
Cross-study reuse and semantic duplication require review. A supported lesson
is scoped to its recorded study.

Evaluators run with the caller's permissions. Use trusted local code. This version
is not an execution sandbox. Digests detect ordinary changes; the local record
store is not an independent authority against a malicious process with the same
permissions. Model costs, authoring time, and failed-call costs are not fully
accounted for yet.

Metric gains and review records do not grant product acceptance. Real user value,
accessibility, security, and craft need evidence suited to the actual product.
