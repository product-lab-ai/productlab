# Upstream foundations

Source inspection on 2026-09-30 found substantial overlap with the original
concept. This prototype isolates the product context and experiment rules needed
to test the remaining claims. It does not claim to invent iterative development
or learning instructions from feedback.

| Project | Inspected revision | Useful foundation |
| --- | --- | --- |
| [Compound Engineering](https://github.com/EveryInc/compound-engineering-plugin) | `89408fddf8dff7703e512b14d0cfcdc9b97a5019` | Product workflows, prototypes, independent alternatives, optimization, retained lessons |
| [pi-autoproto](https://github.com/adiun/pi-autoproto) | `1cca0e0b396d8f983cbfdb7f5418c65f0a776601` | Browser-based prototype exploration with simulated personas |
| [PM Skills](https://github.com/phuryn/pm-skills) | `8607e3b077817f89bf4a9b623246219734ac3be0` | Discovery, assumptions, experiment planning |
| [PM Brain](https://github.com/phuryn/pm-brain) | `6dcc1a712f7b5246fbb0d34477e0c2c9df47e9df` | Product evidence, contradictions, hypotheses, durable decisions |
| [gstack](https://github.com/garrytan/gstack) | `96764e80a641e28141ec8297223768029f5bf483` | Product questioning, reviews, delivery, persistent learning |
| [GEPA](https://github.com/gepa-ai/gepa) | `3f160c295000dd31db3d438c3d17553c23cc5f81` | Learning and evaluating reusable instructions |

The initial engine is a small independent implementation using Python's standard
library. No upstream code has been vendored. These projects remain integration
candidates. A larger fork should follow evidence that we need to change upstream
behavior rather than compose its existing workflow.

## Specific findings used here

Compound Engineering can accept a sequence of small tolerated losses when each
step is compared with the current reference. Its existing fixed limits can stop
that case. Product Lab compares protected metrics with the original reference as
well. This is an engineering choice, not a claim that upstream lacks controls.

pi-autoproto estimates some variability from scores across changed versions.
Product Lab repeats the same candidate and task set for its observed bounds.
Those bounds still do not provide statistical confidence or prove human preference.

GEPA's gskill already tests learned coding instructions on reserved tasks.
The open question here is whether a broader product process can improve actual
user outcomes at comparable total cost.

## Gaia: reference for ideas

On 2026-10-07, the founder chose to treat Red Hat's Project Gaia as prior art
and a reference for ideas. It is not a Product Lab dependency or integration
candidate. Product Lab keeps its own experiment and evidence contracts.

The inspected local checkout was `/home/eparenti/agents/repos/gaia`, revision
`387e394`. This is the internal Red Hat project, not the unrelated public
assistant with the same name.

Ideas worth considering in an independent Product Lab design:

- Compare the structure of observations across studies while retaining their
  audience, task, conditions, and source evidence.
- Keep a proposed connection as a hypothesis until a fresh experiment tests it.
- Retain contradictions and limits on reuse alongside supporting observations.
- Revisit a lesson when its context changes or later evidence disagrees.

Gaia's `gaia/soma/modal_layer/cross_domain_binder.py:analyze_patterns` compares
explicitly structured patterns across domains. It keeps source references,
checks for shared evidence IDs, and returns candidates marked `hypothesis`.
This provides a useful design reference. Different evidence IDs alone do not
establish independent samples or transferable product meaning.

Its raw scanner and promotion path are not a validation model to adopt. A local
check passed 100 seeded Gaussian samples through `DetailScanner`, the batch
preparation helpers, and `Tolerogen`. With one metric and no outcomes, the path
returned `AUTO_PROMOTE`, a confidence score of 0.9, and a prediction about
different outcomes. The scanner split the same metric into high and low groups;
it did not measure an outcome relationship. Batch preparation can also derive
a missing effect size from confidence. These scores cannot support a Product
Lab lesson.

Any future discovery feature must show useful proposals beyond the existing
assistant and simple retrieval of earlier studies. New evidence must establish
their value and full cost. The current Workings trial still needs human feedback;
Gaia's design does not resolve that missing evidence.
