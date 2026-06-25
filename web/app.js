const state = {
  options: null,
};

const els = {
  targetRole: document.querySelector("#targetRole"),
  targetCompany: document.querySelector("#targetCompany"),
  strategyButton: document.querySelector("#strategyButton"),
  strategyStatus: document.querySelector("#strategyStatus"),
  targetResults: document.querySelector("#targetResults"),
  resumeText: document.querySelector("#resumeText"),
  resumeFile: document.querySelector("#resumeFile"),
  extractionBox: document.querySelector("#extractionBox"),
  extractionTitle: document.querySelector("#extractionTitle"),
  extractionMeta: document.querySelector("#extractionMeta"),
  extractionWarnings: document.querySelector("#extractionWarnings"),
  seniority: document.querySelector("#seniority"),
  jobDescription: document.querySelector("#jobDescription"),
  analyzeButton: document.querySelector("#analyzeButton"),
  status: document.querySelector("#status"),
  score: document.querySelector("#score"),
  readiness: document.querySelector("#readiness"),
  scoreNumber: document.querySelector("#scoreNumber"),
  bestFit: document.querySelector("#bestFit"),
  companyFit: document.querySelector("#companyFit"),
  breakdown: document.querySelector("#breakdown"),
  statRounds: document.querySelector("#statRounds"),
  statAcceptance: document.querySelector("#statAcceptance"),
  statSalary: document.querySelector("#statSalary"),
  statFocus: document.querySelector("#statFocus"),
  statCulture: document.querySelector("#statCulture"),
  pros: document.querySelector("#pros"),
  cons: document.querySelector("#cons"),
  missing: document.querySelector("#missing"),
  actions: document.querySelector("#actions"),
  path: document.querySelector("#path"),
  roadmap: document.querySelector("#roadmap"),
  projects: document.querySelector("#projects"),
  rewrites: document.querySelector("#rewrites"),
  themeToggle: document.querySelector("#themeToggle"),
};

async function loadOptions() {
  const response = await fetch("/api/options");
  state.options = await response.json();
  fillSelect(els.targetRole, state.options.roles, "gpu_software");
  fillSelect(els.targetCompany, state.options.companies, "nvidia");
}

function fillSelect(select, options, selected) {
  select.innerHTML = "";
  for (const option of options) {
    const item = document.createElement("option");
    item.value = option.id;
    item.textContent = option.label;
    item.selected = option.id === selected;
    select.appendChild(item);
  }
}

async function analyze() {
  const resumeText = els.resumeText.value.trim();
  const resumeFile = els.resumeFile.files[0];
  if (!resumeText && !resumeFile) {
    setStatus("Paste resume text or upload a PDF first.", true);
    return;
  }

  setStatus("Analyzing...");
  els.analyzeButton.disabled = true;

  try {
    const response = resumeFile
      ? await analyzeUpload(resumeFile)
      : await analyzeText(resumeText);

    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error || "Analysis failed");
    }

    render(payload);
    renderExtraction(payload);
    
    if (payload.best_fit_roles && payload.best_fit_roles.length > 0) {
      els.targetRole.value = payload.best_fit_roles[0].id;
    }
    if (payload.company_fit && payload.company_fit.length > 0) {
      els.targetCompany.value = payload.company_fit[0].id;
    }
    els.targetResults.hidden = true;
    
    setStatus("Analysis complete. Select a target role and company to generate a strategy.");
  } catch (error) {
    setStatus(error.message, true);
  } finally {
    els.analyzeButton.disabled = false;
  }
}

function renderExtraction(data) {
  if (!data.extraction) {
    return;
  }

  els.resumeText.value = data.extracted_text || els.resumeText.value;
  els.extractionBox.hidden = false;
  els.extractionTitle.textContent = `PDF extraction: ${data.extraction.quality}`;
  els.extractionMeta.textContent = `${data.extraction.engine} selected, ${data.extraction.page_count} page(s), ${data.extraction.score}/100 quality score. Extracted text was placed in the resume text box.`;
  renderList(els.extractionWarnings, data.extraction.warnings || []);
}

function analyzeText(resumeText) {
  return fetch("/api/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      resumeText,
      jobDescription: els.jobDescription.value.trim(),
      seniority: els.seniority.value,
    }),
  });
}

function analyzeUpload(resumeFile) {
  const form = new FormData();
  form.append("resumeFile", resumeFile);
  form.append("jobDescription", els.jobDescription.value.trim());
  form.append("seniority", els.seniority.value);
  return fetch("/api/analyze-upload", {
    method: "POST",
    body: form,
  });
}

function render(data) {
  els.score.textContent = `${data.score}/100`;
  els.readiness.textContent = data.readiness;
  els.scoreNumber.textContent = data.score;
  renderBestFit(data.best_fit_roles);
  renderCompanyFit(data.company_fit);
}

function renderTargetStats(data) {
  renderBreakdown(data.score_breakdown);
  
  if (data.company_stats) {
    els.statRounds.textContent = data.company_stats.interview_rounds || "--";
    els.statAcceptance.textContent = data.company_stats.acceptance_rate || "--";
    els.statSalary.textContent = data.company_stats.compensation || "--";
    els.statFocus.textContent = data.company_stats.focus_areas ? data.company_stats.focus_areas.join(" • ") : "--";
    els.statCulture.textContent = data.company_stats.culture_values ? data.company_stats.culture_values.join(" • ") : "--";
  }

  renderList(els.pros, data.pros);
  renderList(els.cons, data.cons);
  renderChips(els.missing, data.missing_skills);
  renderList(els.actions, data.priority_actions);
  renderList(els.path, data.highest_probability_path);
  renderRoadmap(data.roadmap);
  renderList(els.projects, data.recommended_projects);
  renderRewrites(data.rewrite_suggestions);
  els.targetResults.hidden = false;
}

async function generateStrategy() {
  const resumeText = els.resumeText.value.trim();
  if (!resumeText) {
    els.strategyStatus.textContent = "Please analyze a resume first.";
    els.strategyStatus.style.color = "#b64242";
    return;
  }

  els.strategyButton.disabled = true;
  els.strategyStatus.textContent = "Generating strategy...";
  els.strategyStatus.style.color = "";

  try {
    const response = await fetch("/api/target-stats", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        resumeText,
        targetRole: els.targetRole.value,
        targetCompany: els.targetCompany.value,
        jobDescription: els.jobDescription.value.trim(),
        seniority: els.seniority.value,
      }),
    });

    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error || "Failed to generate strategy");
    }

    renderTargetStats(payload);
    els.strategyStatus.textContent = "Strategy generated successfully.";
    document.querySelector("#exportButton").style.display = "block";
  } catch (error) {
    els.strategyStatus.textContent = error.message;
    els.strategyStatus.style.color = "#b64242";
  } finally {
    els.strategyButton.disabled = false;
  }
}

function renderBestFit(items) {
  els.bestFit.innerHTML = "";
  for (const item of items) {
    const row = document.createElement("div");
    row.className = "fit-row";
    row.innerHTML = `
      <div class="fit-top">
        <strong>${escapeHtml(item.label)}</strong>
        <span>${item.score}/100</span>
      </div>
      <div class="track"><div class="fill" style="width: ${item.score}%"></div></div>
    `;
    els.bestFit.appendChild(row);
  }
}

function renderCompanyFit(items) {
  els.companyFit.innerHTML = "";
  for (const item of items.slice(0, 5)) {
    const missing = item.missing && item.missing.length ? `Missing: ${item.missing.join(", ")}` : "Strong keyword match";
    const row = document.createElement("div");
    row.className = "fit-row";
    row.innerHTML = `
      <div class="fit-top">
        <strong>${escapeHtml(item.label)}</strong>
        <span>${item.score}%</span>
      </div>
      <div class="track"><div class="fill" style="width: ${item.score}%"></div></div>
      <small>${escapeHtml(missing)}</small>
    `;
    els.companyFit.appendChild(row);
  }
}

function renderBreakdown(breakdown) {
  els.breakdown.innerHTML = "";
  const maxByKey = {
    role_fit: 20,
    systems_low_level: 20,
    gpu_ai_compiler_specialization: 20,
    projects: 15,
    cs_fundamentals: 10,
    impact_metrics: 10,
    ats_formatting: 5,
    company_alignment_bonus: 5,
    job_description_bonus: 5,
  };

  for (const [key, value] of Object.entries(breakdown)) {
    const max = maxByKey[key] || 20;
    const percent = Math.round((value / max) * 100);
    const row = document.createElement("div");
    row.className = "bar-row";
    row.innerHTML = `
      <div class="bar-top">
        <span>${labelize(key)}</span>
        <strong>${value}/${max}</strong>
      </div>
      <div class="track"><div class="fill" style="width: ${Math.min(100, percent)}%"></div></div>
    `;
    els.breakdown.appendChild(row);
  }
}

function renderList(target, items) {
  target.innerHTML = "";
  if (!items || !items.length) {
    const li = document.createElement("li");
    li.textContent = "No issues found.";
    target.appendChild(li);
    return;
  }
  for (const item of items) {
    const li = document.createElement("li");
    li.textContent = item;
    target.appendChild(li);
  }
}

function renderChips(target, items) {
  target.innerHTML = "";
  if (!items || !items.length) {
    const chip = document.createElement("span");
    chip.className = "chip";
    chip.textContent = "No major gaps";
    target.appendChild(chip);
    return;
  }
  for (const item of items) {
    const chip = document.createElement("span");
    chip.className = "chip";
    chip.textContent = item;
    target.appendChild(chip);
  }
}

function renderRoadmap(roadmap) {
  els.roadmap.innerHTML = "";
  els.roadmap.className = "timeline";
  for (const [key, items] of Object.entries(roadmap)) {
    const step = document.createElement("section");
    step.className = "timeline-item";
    step.innerHTML = `<h4>${labelize(key)}</h4>`;
    const list = document.createElement("ul");
    for (const item of items) {
      const li = document.createElement("li");
      li.textContent = item;
      list.appendChild(li);
    }
    step.appendChild(list);
    els.roadmap.appendChild(step);
  }
}

function renderRewrites(items) {
  els.rewrites.innerHTML = "";
  for (const item of items) {
    const block = document.createElement("div");
    block.className = "rewrite";
    block.innerHTML = `
      <p><span>Before</span>${escapeHtml(item.before)}</p>
      <p><span>After</span>${escapeHtml(item.after)}</p>
    `;
    els.rewrites.appendChild(block);
  }
}

function labelize(key) {
  return key
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function setStatus(message, isError = false) {
  els.status.textContent = message;
  els.status.style.color = isError ? "#b64242" : "";
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

els.analyzeButton.addEventListener("click", analyze);
if (els.strategyButton) {
  els.strategyButton.addEventListener("click", generateStrategy);
}

if (els.themeToggle) {
  els.themeToggle.addEventListener("click", () => {
    const isDark = document.documentElement.getAttribute("data-theme") === "dark";
    if (isDark) {
      document.documentElement.removeAttribute("data-theme");
      els.themeToggle.textContent = "🌙";
    } else {
      document.documentElement.setAttribute("data-theme", "dark");
      els.themeToggle.textContent = "☀️";
    }
  });
}

loadOptions().catch((error) => setStatus(error.message, true));
