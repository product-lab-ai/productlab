# Review and improve an existing product

Use this workflow when the user brings an existing product or an initial
prototype. The output is a useful product change with reasons and evidence.
Investigation documents support that work; they are not the final product.

## Establish the actual starting point

Read the accepted product direction, repository instructions, current work,
handoff, and relevant experiments. Verify the branch and remote state before
editing. Preserve local changes. Use an isolated copy or worktree when a trial
needs a separate candidate, including uncommitted source in its baseline.

Record the source revision and a manifest of the files actually used. A commit
alone does not identify a dirty checkout. Keep generated artifacts separate from
source, and identify build dependencies that the snapshot does not capture.
Do not overwrite an earlier trial or label inherited changes as your improvement.

For a new product, build the smallest prototype that exposes the uncertain
behavior, then apply the same review. Do not mistake the first implementation's
structure for a customer requirement.

## Reconstruct the product from use

Operate the product through its main entry, a complete task, a failed attempt,
recovery, and return after interruption. Read the implementation to explain what
you observe. Review source-only claims separately from browser observations.
Use the actual delivery path, and check that the user's access path works.

Draft the audience, intended outcome, current substitute, important journeys,
strengths, and unresolved assumptions. Reuse existing research and product
context. Do not turn an absent interview into an invented persona finding.

Consider these perspectives at a depth suited to the product:

| Perspective | Decision it informs |
| --- | --- |
| Customer value | Whether the product solves an important task for the intended audience |
| UX and accessibility | Whether people can understand, operate, and recover within the journey |
| Craft | Whether content, controls, pacing, and visual choices form a coherent experience |
| Performance and reliability | Whether the product responds and preserves work under its intended conditions |
| Security and privacy | Whether the relevant code, data, identity, and storage boundaries are sound |
| Maintainability and cost | Whether a useful change can be built, checked, and sustained at acceptable cost |
| Differentiation | Whether a different mechanism could solve a real problem better than existing substitutes |
| Domain outcomes | Whether the product achieves its specific purpose, such as learning or accurate decisions |

Retain conflicts. Faster task completion might hide weaker understanding. More
guidance might reduce user agency. Adding a feature can make the complete product
harder to use. The owner chooses intended tradeoffs within product requirements.

## Keep observations separate from explanations

For each consequential finding, record the journey, exact source or artifact,
what happened, why it could matter, and what remains uncertain. Label its basis
as observed behavior, code inspection, attributed feedback, or hypothesis.

A failure to preserve a draft can be observed directly. The number of customers
affected cannot be inferred from that observation alone. Two reviews citing the
same trace remain one underlying observation. Statistical scores need an outcome,
a meaningful comparison, and evidence suited to the stated claim.

Preserve unsuccessful runs and capture failures. Correct the harness when needed
and use a new output location; do not replace failed evidence with a successful
retry. Keep development investigations separate from reserved validation.

## Select opportunities before solutions

Prepare a short list that reflects the whole review. Each opportunity needs:

- An audience problem and supporting evidence, or an explicit hypothesis.
- Competing explanations and materially different mechanisms worth comparing.
- A simpler alternative, including leaving the product unchanged where sensible.
- Expected benefit, effort, uncertainty, and risks to required behavior.
- A small experiment, its decision criteria, and a result that would reject it.

Give a recommendation and explain why it comes first. Do not impose a universal
score or a fixed number of proposals. Fix a clear requirement failure when the
evidence warrants it. Test an uncertain customer explanation before committing
to a large feature. Check adjacent work before claiming novelty.

## Carry one opportunity through the complete loop

Build the alternatives, freeze their sources and measures, and use
[experiments.md](experiments.md) to run the existing engine where it fits.
Assess the product through its actual decisions. Keep security, accessibility,
correctness, and other requirements separate from metric gains.

Obtain human evidence for claims about preference, effort, or learning. Prepare
the task and a neutral way to record observations; do not contact participants
without instructions. Continue unrelated engineering work while such evidence
is pending. Mark the dependent conclusion unresolved.

Integrate the selected change, then inspect the whole journey again. Record the
owner's acceptance separately from the experiment's reference selection. Explain
rejected alternatives and known limits. A local candidate does not imply release.

## Reuse the experience carefully

Capture lessons with conditions, evidence, exceptions, and their originating
decision. Owner preferences are inputs to product direction, not customer study
results. Before applying a lesson elsewhere, state the shared problem, important
differences, proposed action, and fresh test.

Begin with readable records and retrieval. Add schemas, commands, or discovery
machinery only when a real workflow needs them. Compare learning against ordinary
assistant work and simple retrieval, including the cost of collecting and
checking lessons. Repeatedly exposed tasks cannot establish fresh confirmation.
