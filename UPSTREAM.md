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
