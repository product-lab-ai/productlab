# Experiment review trial

Status: working prototypes prepared. Prototype comparison is pending. The user
reported an access failure, recorded below.

## Run the trial

From the repository root:

```bash
python3 trials/experiment-review/prepare.py --output generated/my-review-trial
python3 trials/experiment-review/verify_browser.py --trial generated/my-review-trial
```

Open `generated/my-review-trial/review/index.html` in a browser. To serve it locally:

```bash
python3 -m http.server 8765 --bind 127.0.0.1 --directory generated/my-review-trial/review
```

When preparation runs inside a container, its loopback URL may not be reachable
from the reviewer's host browser. Open the generated `index.html` from a folder
shared with the host, or use an existing port mapping. Verify the reviewer's
access path before announcing that the trial is ready. Do not expose the server
to other networks just to bypass this check.

The preparation command runs real engine trials to obtain the source reports,
snapshots all three presentations, and checks them through the experiment engine.
It preserves earlier output by requiring a new directory. The optional browser
checks require the Python `playwright` package and its Chromium browser. Both
were already available in the development environment. Use
`--skip-engineering-checks` to prepare the views without those checks.

The review page has no external assets, requests, or runtime dependencies.
The default first presentation is assigned at random. Review that view first,
record your judgment, and then compare the others. Try at least one failed or
rejected case. Download feedback when finished. Answers remain drafts until
recorded, and editing a recorded answer returns it to a draft.

Generated source evidence, participant feedback, screenshots, and browser test
responses stay under ignored local output directories. Automated responses are
explicitly labeled as test data. Do not count them as user observations.

## Current findings

The revised local run is `generated/review-trial-2/`. Each presentation retained
all required source facts across three cases and two repetitions. The engine
reported no improvement for either alternative. This is expected: the automated
check measures fact retention, not whether a person understands the report.
Required facts inside a disclosure are checked after opening that disclosure.
The raw JSON disclosure does not count toward those checks.

The current version passed 32 browser checks, including reference values,
unchanged baseline wording, feedback separation and recovery, downloads,
keyboard access, narrow layouts, text contrast, and markup displayed as text.
The original engine's 34 behavioral tests also passed. These checks do not
establish full accessibility, production security, or product usefulness.

Assistant visual review of the first version found crowded table labels and too
much detail in summary A. The revised version separates labels and puts the
individual requirement reviews behind a disclosure in A. This is a design
hypothesis awaiting user feedback, not a validated product lesson.

No human preference has been recorded. No supported product lesson has been
claimed. Reserved engineering validation remains unused. The next step is an
actual reviewer attempting the task and explaining their judgment.

## First-use observation

The user could not open the supplied `http://127.0.0.1:8765/` address from their
browser. They identified that the assistant was running in a container. The
server returned HTTP 200 inside that container. Those checks had not established
access from the user's browser.

Live mount inspection confirmed that this environment shares the project folder
with the host at the same path. The correction was to open the generated review
HTML file from that shared folder. The desktop opener accepted the request.
The user has not yet confirmed that the page appeared.

Proposed lesson: verify the reviewer's access path when preparing a trial in a
container. This observation concerns setup, and does not favor either report
presentation. It is not evidence of general learning transfer.

## Brief

Help a Product Lab builder understand an experiment result and choose a useful
next step without reading the engine source. This is a small trial of Product
Lab's own product experience. It does not test the full autonomous product idea.

The founder asked what was built, identified regression as a central problem,
and accepted a real product trial. Those statements establish the immediate
context. Difficulty reading the current report is a hypothesis, not an observed
user problem. The founder has not yet tried this report interface.

## Audience and journey

The primary persona is Product Lab's existing builder, defined in
[PRODUCT.json](../../PRODUCT.json). A proposed supporting persona is a product
owner who needs to judge the result without inspecting code.

| Empathy | Basis |
| --- | --- |
| Says: we need to know what better means and avoid regression | Founder's statements |
| Thinks: a better score may conceal a worse product | Hypothesis |
| Does: asks the assistant to explain what exists and proposes trials | Conversation |
| Feels: uncertainty about what the evidence permits | Hypothesis |

The journey starts when a trial finishes or fails. The builder reads its result,
identifies what is supported and what remains unknown, inspects evidence, and
decides what to try next. Success means a correct explanation and a defensible
next action, with uncertainty preserved.

## Alternatives, declared before implementation

- **Current report:** the existing terminal report, presented without changed
  wording. This is the local workflow baseline. It is not a comparison against
  the strongest external product-development tool.
- **A, decision summary:** lead with the result, scope, and an explicitly labeled
  suggested next step. Offer measurements and raw evidence beneath that summary.
  Hypothesis: this helps the builder orient quickly. Risk: the suggestion steers
  judgment or hides disagreement.
- **B, evidence comparison:** lead with candidate and reference measurements,
  requirements, and run history. Let the builder reach a conclusion from those
  details. Hypothesis: this helps inspect a decision. Risk: it requires more work
  before the builder understands the result.

Both alternatives consume the same verified engine reports. They do not change
the engine's verdict or grant product approval. Labels are neutral in the trial
interface, but this founder pilot is not blind.

## What counts as better

Record these human observations separately from engineering checks:

1. Can the reviewer state the result and its evidence scope correctly?
2. Can they distinguish experimental improvement from product acceptance?
3. Is their next action consistent with the result and validation state?
4. What was confusing, missing, or needlessly difficult?
5. Which presentation helps their actual work, and why?

A participant must not confuse simulation success with release readiness. A
supported lesson can justify product review and a fresh real task. A rejected
candidate needs revision. A failed validation attempt needs diagnosis and fresh
validation data. Rerunning exposed cases is not fresh confirmation.

The browser retains draft feedback locally when storage is available and can
download it as JSON. A preference alone does not establish task success. Reading
the same cases across views creates learning effects. Treat this as a formative
pilot to find problems, not a causal speed comparison or a general user study.

Automated checks measure faithful presentation and basic browser behavior only.
Equal engineering results produce no winning prototype. Human review and craft
remain pending until a person supplies evidence. Reserved engineering cases
remain unused until a proposed lesson exists.

## Quality choices and requirements

Clarity, completeness, and cost are the main tradeoffs. Summary A may hide detail
behind a disclosure; comparison B may use more space. Both must retain the same
evidence and unresolved requirements. No single weighted product score is used.

Security, privacy, integrity, correctness, accessibility, recovery, honesty, and
bounded actions follow the parent product context. This trial adds concrete
checks: render report strings as text, make no external requests, offer keyboard
access, preserve feedback across views, and keep source reports unchanged.
The page reads prepared local exports. It does not run experiments or change
their records. Exported reports have no live integrity check after preparation.

## Design intent

A builder reads dense evidence on a laptop at a desk in daylight. Use a white
surface, dark text, a restrained amber accent, familiar controls, and clear table
labels. The intended effect is that facts and unknowns are easy to inspect.
Use one system font and compact, consistent spacing. No decorative charts or
success scores. Review the complete workflow at desktop and narrow widths.

## Cost and evidence limits

Record preparation time, automated evaluator time, known model use, and human
effort separately. Unknown API cost remains unknown. Do not infer savings from
the engine's evaluator totals. The source recovery examples are simulations;
the report-reading task is the real product task under review.

This pilot cannot establish broad lesson transfer or Product Lab's advantage
over existing tools. That later comparison still needs fresh briefs, comparable
resources, representative users, and independent review.
