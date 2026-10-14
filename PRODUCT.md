# Product Lab

Product Lab helps a builder and their assistant improve a product as a whole.
It can start from a loose idea, an initial prototype, or an existing product.
It operates what exists, works backward to the customer problem and assumptions,
develops useful alternatives, tests them, and produces a coherent better version.
Retained experience should improve later product decisions.

The founder confirmed this direction on 2026-10-07 and selected Workings as the
first target. [PLAN.md](PLAN.md) defines the development sequence and next work.
The product context lives in [PRODUCT.json](PRODUCT.json). View it with
`python3 lab.py brief --product PRODUCT.json`.

The founder has asked for rapid prototyping, retained experience, better
experiments, audience understanding, and exceptional craft. Those requests are
direct evidence of intent. The broader personas and empathy maps are initial
hypotheses. We have not conducted user research.

## Who and what

The primary user is a product builder working with a coding assistant. Their
problem is deciding what deserves to be built and whether each iteration serves
the intended audience. Code generation alone does not answer that question.

A product owner or domain expert is a supporting user. They need to operate the
experience, judge its fit, and see their feedback survive later changes.

The complete journey is: inspect the product, understand its customers, challenge
its assumptions, select opportunities, compare mechanisms, operate prototypes,
judge results, synthesize a coherent experience, and test lessons on later work.
The initial engine implements the experiment and evidence portion. The assistant
skill carries product reasoning around it. The broader workflow and final
product synthesis are the next development work.

Review customer value, UX, accessibility, craft, performance, reliability,
security, maintainability, and useful new capabilities. Consider simplification
and changes to the product premise alongside new features. The process must help
choose experiments, produce strong alternatives, and carry useful experience
forward together.

## What better means

Each experiment traces a metric to a user outcome, journey, and persona. A
measurement without that connection cannot initialize a study.

Quality has several dimensions. Their priorities follow the audience and the
task. We record an intent, allowed tradeoff, lower limit, and review method for
each. We do not combine them into one universal product score.

| Dimension | Product Lab's intent | Review |
| --- | --- | --- |
| Functionality | Complete the selected user journey | Have someone attempt the task |
| UX | Make decisions understandable with little setup | Observe where the builder hesitates |
| Craft | Clear meaning, coherent behavior, and finish suited to the medium | Review the complete experience |
| Performance | Shorten time to a useful decision | Include setup, waiting, and interpretation |
| Maintainability | Keep rules understandable and tools replaceable | Change an evaluator and diagnose a failure |
| Innovation | Find a useful, distinctive mechanism | Compare substantially different approaches |
| Cost | Reduce total effort, including learning | Account for human time and failed experiments |
| Portability | Fit the builder's existing assistant and tools | Exercise the whole journey in each host |

## Requirements that cannot buy a better score

- **Security:** authorized access, appropriate isolation, protected secrets, and
  sound dependency handling. Security always applies.
- **Privacy:** suitable collection, disclosure, retention, and data boundaries.
- **Data integrity:** preserve user work and trustworthy experiment records.
- **Core correctness:** promised behavior works; incomplete evidence stays incomplete.
- **Accessibility:** the core journey works with relevant access needs and tools.
- **Reliability and recovery:** meet the promised operating conditions, retain
  work after failure, and provide a safe recovery path.
- **Honesty and user control:** communicate actual state, uncertainty, consequences,
  and the user's available choices.
- **Safety:** address credible harms in the product's intended use.

These categories need concrete requirements and evidence for each product.
Availability targets vary by use, for example. Once promised, they become a
minimum that other gains cannot excuse. Applicable legal, contractual, and
license obligations also belong in a real product's requirements.

A requirement outside the product's scope needs an explicit reason. Recording a
reason does not certify that it is correct. Passing a metric does not clear any
unreviewed requirement. The engine can retain an experimental candidate while
its product reviews remain pending. It never grants release approval.

## Craft is part of the product

The assistant should develop a point of view: intended meaning, audience effect,
information hierarchy, interaction rhythm, language, and distinctive character.
Explore genuinely different mechanisms. Explain how each serves the person and
their task. The user owns product intent and taste.

Review the actual medium. A command line workflow needs clear output and useful
failure messages. An interface needs direct interaction, content, visual
hierarchy, motion when helpful, and complete states. A screenshot cannot prove
a journey. A rubric cannot establish beauty by itself.

The final synthesis needs another complete review. Combining successful parts
does not establish that the whole is coherent.

## First trial and counterargument

The first executable example learns remedies from a tiny simulated recovery
task. It checks reuse and rejection mechanics. Its repeated error types and
invented personas do not establish real-world transfer or product value.

The first field trial should compare the strongest existing workflow, Product
Lab with learning disabled, and Product Lab with retained lessons. Use new briefs,
representative users, the same resources, and reviews that hide the producing
system. Include the full cost of collecting and validating lessons.

The main risk is that Product Lab creates more records without better decisions.
The test is whether users reach useful, well-crafted outcomes with less total
work, while the requirements remain satisfied.
