"use strict";

(() => {
  const data = window.TRIAL_DATA;
  const reportNode = document.getElementById("report");
  if (!data || !Array.isArray(data.cases) || !data.cases.length) {
    reportNode.textContent = "This review has no prepared reports. Run the trial preparation command, then open its index.html.";
    document.getElementById("feedback-form").hidden = true;
    return;
  }
  const labels = {current: "Current report", a: "Prototype A", b: "Prototype B"};
  const fixedView = window.TRIAL_VARIANT;
  const params = new URLSearchParams(location.search);
  const requested = params.get("view");
  let firstView = Object.hasOwn(labels, requested) ? requested : ["current", "a", "b"][crypto.getRandomValues(new Uint8Array(1))[0] % 3];
  let view = Object.hasOwn(labels, fixedView) ? fixedView : firstView;
  let selected = data.cases.find(c => c.id === params.get("case")) || data.cases[0];
  const storageKey = `productlab-review:${data.id}`;
  let storageWorks = true;
  let answers = {};
  let visits = [];
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey) || "null");
    if (saved && saved.schema === 1 && saved.trial === data.id && saved.answers && typeof saved.answers === "object" && !Array.isArray(saved.answers) && Array.isArray(saved.visits)) {
      answers = saved.answers || {};
      visits = saved.visits || [];
      if (Object.hasOwn(labels, saved.first_view)) firstView = saved.first_view;
      if (!fixedView && !Object.hasOwn(labels, requested)) view = Object.hasOwn(labels, saved.last_view) ? saved.last_view : firstView;
      if (!params.has("case")) selected = data.cases.find(c => c.id === saved.last_case) || selected;
    } else if (saved !== null) {
      storageWorks = false;
    }
  } catch { storageWorks = false; }

  const el = (tag, text, className) => {
    const node = document.createElement(tag);
    if (text !== undefined && text !== null) node.textContent = String(text);
    if (className) node.className = className;
    return node;
  };
  const number = value => typeof value === "number" && Number.isFinite(value) ? String(Number(value.toPrecision(4))) : "Not measured";
  const currentKey = () => `${view}:${selected.id}`;
  const fields = ["finding", "next-step", "friction", "ease"];
  const status = document.getElementById("feedback-status");
  const now = () => new Date().toISOString();

  function payload() {
    return {
      schema: 1, trial: data.id, prepared_at: data.prepared_at,
      first_view: firstView, last_view: view, last_case: selected.id, exported_at: now(),
      attribution: "Participant entered. Identity is not authenticated. Responses are not scored automatically.",
      cases: data.cases.map(c => ({id: c.id, report_digest: c.digest})),
      candidates: data.candidates, answers, visits,
    };
  }

  function persist() {
    try { if (storageWorks) localStorage.setItem(storageKey, JSON.stringify(payload())); }
    catch { storageWorks = false; }
    if (!storageWorks) {
      status.textContent = "Saved feedback could not be read or written. Existing stored data is preserved. Keep this page open and download your feedback.";
      status.classList.add("error");
    }
  }

  function saveDraft() {
    const previous = answers[currentKey()] || {};
    const value = Object.fromEntries(fields.map(id => [id, document.getElementById(id).value]));
    const changed = fields.some(id => (previous[id] || "") !== value[id]);
    if (!changed) return;
    answers[currentKey()] = {...value, recorded: false, updated_at: now(), candidate_digest: data.candidates[view], report_digest: selected.digest};
    persist();
    updateCount();
    if (storageWorks) status.textContent = "Draft saved in this browser. Record it when ready.";
  }

  function updateCount() {
    const count = Object.values(answers).filter(answer => answer.recorded).length;
    document.getElementById("response-count").textContent = `${count} judgment${count === 1 ? "" : "s"} recorded.`;
  }

  function loadDraft() {
    const saved = answers[currentKey()] || {};
    for (const id of fields) document.getElementById(id).value = saved[id] || "";
    status.textContent = saved.recorded ? "Judgment recorded. Editing it returns it to a draft." : "";
    if (!storageWorks) persist();
    updateCount();
  }

  function table(caption, headings, rows) {
    const wrapper = el("div", null, "table-scroll");
    wrapper.tabIndex = 0;
    wrapper.setAttribute("role", "region");
    wrapper.setAttribute("aria-label", caption);
    const node = el("table");
    node.append(el("caption", caption));
    const head = el("thead");
    const titles = el("tr");
    for (const heading of headings) {
      const th = el("th", heading);
      th.scope = "col";
      titles.append(th);
    }
    head.append(titles);
    const body = el("tbody");
    for (const row of rows) {
      const tr = el("tr");
      row.forEach((value, index) => {
        const td = el(index === 0 ? "th" : "td", null, index ? "numeric" : "");
        if (index === 0) td.scope = "row";
        if (value instanceof Node) td.append(value); else td.textContent = String(value);
        tr.append(td);
      });
      body.append(tr);
    }
    node.append(head, body);
    wrapper.append(node);
    return wrapper;
  }

  function measurement(value) {
    const cell = el("span", value ? number(value.mean) : "Not measured");
    if (value) cell.append(el("small", `Observed range ${number(value.low)} to ${number(value.high)}`));
    return cell;
  }

  function latestRun(report) { return report.runs[report.runs.length - 1] || null; }

  function runStatus(run) {
    if (!run) return "No runs";
    if (run.status !== "complete") return run.status;
    return run.lesson_verdict || run.decision?.status || run.status;
  }

  function conclusion(report) {
    const run = latestRun(report);
    const outcome = runStatus(run);
    const evidence = report.contract.contract.evidence_kind;
    const validationUsed = report.state.validation_used;
    const pending = (report.quality || []).some(q => q.status !== "ready_for_owner_review");
    const titles = {
      supported: evidence === "simulation" ? "Lesson supported in this simulation" : "Lesson supported on these automated tasks",
      rejected: "Lesson rejected on these tasks",
      reject: "Candidate rejected on these tasks",
      accept: "Candidate improved on development tasks",
      baseline: "Starting measurements recorded",
      inconclusive: "Improvement remains inconclusive",
      failed: "Trial failed. No new conclusion is supported.",
      running: "Trial is still marked running",
      "No runs": "No experiment has run yet",
    };
    let next;
    if (outcome === "failed") next = "Inspect the failure and repair the experiment.";
    else if (outcome === "running") next = "Check whether the process is still active. Recover it only after it has stopped.";
    else if (["reject", "rejected"].includes(outcome)) next = "Inspect the failed requirement or loss. Revise the candidate before another comparison.";
    else if (["supported", "accept"].includes(outcome)) next = "Review the candidate with a person doing the intended task. Record what helps and what remains unclear.";
    else if (outcome === "baseline") next = "Propose a different candidate and an experiment that could change the product decision.";
    else if (outcome === "No runs") next = "Register a starting candidate and run the development tasks.";
    else next = "Inspect the uncertainty before deciding which additional evidence is worth collecting.";
    if (validationUsed) next += " Any further validation needs fresh cases in a new study.";
    return {run, outcome, title: titles[outcome] || `Recorded result: ${outcome}`, next, pending};
  }

  function context(report) {
    const contract = report.contract.contract;
    const persona = contract.product.personas.find(p => p.id === contract.product.journeys.find(j => j.id === contract.journey)?.persona);
    const container = el("div");
    container.append(el("p", `${contract.product.name} / ${persona?.name || "Audience not recorded"}`, "context"));
    container.append(el("h2", contract.question, "question"));
    const metadata = el("div", null, "metadata");
    metadata.append(el("span", `Evidence: ${contract.evidence_kind}`), el("span", `Validation consumed: ${report.state.validation_used ? "True" : "False"}`));
    const current = report.runs.find(r => r.id === report.state.current);
    metadata.append(el("span", `Current reference: ${current?.candidate || "none"} (run ${report.state.current || "none"})`));
    container.append(metadata);
    return container;
  }

  function resultBlock(report, suggest) {
    const result = conclusion(report);
    const section = el("section", null, "result");
    section.dataset.status = result.outcome;
    section.append(el("h3", result.title));
    if (result.run) section.append(el("p", `Run ${result.run.id} / candidate ${result.run.candidate || "not recorded"} / ${result.outcome}`, "subtle"));
    for (const reason of result.run?.decision?.reasons || []) section.append(el("p", reason));
    if (result.run?.error) section.append(el("p", result.run.error, "error"));
    if (suggest) {
      section.append(el("h3", "Suggested next step"));
      section.append(el("p", result.next));
      section.append(el("p", "This suggestion follows the recorded state. You choose the next experiment.", "subtle"));
    }
    section.append(el("p", "Human product value is untested. Experimental improvement does not grant product approval."));
    return section;
  }

  function metrics(report) {
    const run = latestRun(report);
    const section = el("section", null, "section");
    section.append(el("h3", "Measurements"));
    if (!run?.summary) {
      section.append(el("p", "No complete measurements for the latest run. Earlier results remain in the run history."));
      return section;
    }
    const validation = run.phase === "validation";
    const reference = report.runs.find(r => r.id === run.current);
    const original = report.runs.find(r => r.id === run.original);
    const controlSummary = validation ? run.control_summary : reference?.summary;
    const originalSummary = validation ? run.original_summary : original?.summary;
    const caption = validation ? "Same reserved tasks, measured in this validation run" : "Development results; reference measurements come from earlier runs";
    const headings = ["Metric", `Candidate: ${run.candidate}`, `Current: ${run.control || reference?.candidate || "none"}`, `Original: ${run.original_candidate || original?.candidate || "none"}`];
    const rows = report.contract.contract.metrics.map(metric => {
      const name = el("span", metric.name);
      name.append(el("small", `${metric.direction}; ${metric.role}`));
      return [name, measurement(run.summary[metric.name]), measurement(controlSummary?.[metric.name]), measurement(originalSummary?.[metric.name])];
    });
    section.append(table(caption, headings, rows));
    section.append(el("p", "Ranges describe repeated observations. They are not confidence intervals.", "subtle"));
    return section;
  }

  function requirements(report, compact) {
    const section = el("section", null, "section");
    section.append(el("h3", "Product requirements and craft"));
    const candidate = latestRun(report)?.candidate;
    const quality = (report.quality || []).find(q => q.candidate === candidate);
    if (!quality) {
      section.append(el("p", "No candidate review is available. No product approval is established."));
      return section;
    }
    const readable = value => value.replaceAll("_", " ");
    const pending = Object.values(quality.areas).filter(value => ["pending", "unknown"].includes(value)).length;
    section.append(el("p", `Candidate ${candidate}: ${readable(quality.status)}. ${pending} reviews unresolved.`));
    const rows = Object.entries(quality.areas).map(([area, value]) => {
      const name = el("span", area.replaceAll("-", " "));
      const requirement = report.contract.contract.product.essentials.find(item => item.id === area);
      if (requirement) name.append(el("small", requirement.requirement));
      return [name, readable(value)];
    });
    const evidence = table("Recorded reviews for the latest candidate", ["Requirement", "Status"], rows);
    if (compact) {
      const detail = el("details");
      detail.dataset.requirements = "true";
      detail.append(el("summary", "Inspect each requirement and review"), evidence);
      section.append(detail);
    } else section.append(evidence);
    section.append(el("p", "Review identities are caller supplied. Reported passes require inspection of their evidence.", "subtle"));
    return section;
  }

  function history(report) {
    const section = el("section", null, "section");
    section.append(el("h3", "Run history"));
    if (!report.runs.length) section.append(el("p", "No runs recorded."));
    else section.append(table("Completed, failed, and active attempts", ["Run", "Candidate", "Phase", "Result"], report.runs.map(run => [run.id, run.candidate || "not recorded", run.phase, runStatus(run)])));
    const cost = report.costs;
    if (cost) section.append(el("p", `${cost.completed_evaluations} completed evaluator calls; ${number(cost.wall_seconds)} seconds. ${cost.cost_unknown_evaluations} calls have unknown reported cost. This excludes full authoring, model, and human effort.`, "subtle"));
    return section;
  }

  function download(name, value) {
    const url = URL.createObjectURL(new Blob([JSON.stringify(value, null, 2) + "\n"], {type: "application/json"}));
    const anchor = el("a");
    anchor.href = url;
    anchor.download = name;
    document.body.append(anchor);
    anchor.click();
    anchor.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  function evidence() {
    const details = el("details", null, "source");
    details.append(el("summary", "Inspect the source report"));
    details.append(el("p", `Prepared report SHA-256: ${selected.digest}`, "subtle"));
    const button = el("button", "Download source JSON");
    button.type = "button";
    button.addEventListener("click", () => download(`${selected.id}.json`, selected.report));
    details.append(button, el("pre", JSON.stringify(selected.report, null, 2), "raw"));
    return details;
  }

  function render() {
    reportNode.replaceChildren();
    const report = selected.report;
    if (view === "current") reportNode.append(el("pre", selected.original_text, "raw original"));
    else {
      reportNode.append(context(report));
      if (view === "a") reportNode.append(resultBlock(report, true), metrics(report), requirements(report, true), history(report));
      else reportNode.append(metrics(report), requirements(report, false), history(report), resultBlock(report, false));
    }
    reportNode.append(evidence());
    for (const button of document.querySelectorAll("[data-view]")) {
      button.setAttribute("aria-pressed", String(button.dataset.view === view));
      if (fixedView) button.hidden = button.dataset.view !== fixedView;
    }
    document.getElementById("view-notice").textContent = `${labels[view]} · ${selected.label}. Feedback is saved separately for each view and case.`;
    visits.push({view, case: selected.id, at: now()});
    persist();
    loadDraft();
  }

  for (const entry of data.cases) {
    const option = el("option", entry.label);
    option.value = entry.id;
    option.selected = entry.id === selected.id;
    document.getElementById("case").append(option);
  }
  document.getElementById("case").addEventListener("change", event => {
    saveDraft();
    selected = data.cases.find(c => c.id === event.target.value);
    render();
  });
  for (const button of document.querySelectorAll("[data-view]")) button.addEventListener("click", () => {
    saveDraft();
    view = button.dataset.view;
    render();
  });
  for (const id of fields) document.getElementById(id).addEventListener("input", saveDraft);
  document.getElementById("feedback-form").addEventListener("submit", event => {
    event.preventDefault();
    saveDraft();
    if (!document.getElementById("finding").value.trim() || !document.getElementById("next-step").value.trim()) {
      status.textContent = "Write a finding and a next step before recording this judgment.";
      return;
    }
    answers[currentKey()].recorded = true;
    answers[currentKey()].recorded_at = now();
    persist();
    updateCount();
    if (storageWorks) status.textContent = "Judgment recorded in this browser. Download it when ready to share.";
  });
  document.getElementById("download-feedback").addEventListener("click", () => {
    saveDraft();
    download(`productlab-feedback-${data.id}.json`, payload());
  });
  document.getElementById("provenance").textContent = `Trial ${data.id} · prepared ${data.prepared_at}. Prototype selection and human review remain open.`;
  render();
})();
