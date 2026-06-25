"""Rule-based resume analysis engine."""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Any

from .knowledge_base import (
    ATS_SECTIONS,
    COMPANY_PROFILES,
    CORE_FOUNDATION,
    IMPACT_TERMS,
    ROLE_PROFILES,
)

import spacy
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # Fallback if spacy model is not downloaded
    nlp = None


@dataclass
class Finding:
    title: str
    detail: str
    severity: str = "medium"


@dataclass
class BaseAnalysisResult:
    score: int
    readiness: str
    best_fit_roles: list[dict[str, Any]]
    company_fit: list[dict[str, Any]]
    ats_issues: list[str]
    detected_signals: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TargetStatsResult:
    score_breakdown: dict[str, int]
    pros: list[str]
    cons: list[str]
    missing_skills: list[str]
    company_stats: dict[str, Any]
    rewrite_suggestions: list[dict[str, str]]
    roadmap: dict[str, list[str]]
    recommended_projects: list[str]
    highest_probability_path: list[str]
    priority_actions: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def analyze_base_resume(
    resume_text: str,
    job_description: str = "",
    seniority: str = "mid"
) -> BaseAnalysisResult:
    text = _normalize(resume_text)
    raw_lines = [line.strip() for line in resume_text.splitlines() if line.strip()]
    doc = nlp(text) if nlp else None

    systems_score, systems_missing, systems_hits = _weighted_score(
        text, _systems_keywords(), max_points=20, doc=doc, seniority=seniority
    )
    specialization_score, specialization_missing, specialization_hits = _weighted_score_with_expected(
        text, _specialization_keywords(), max_points=20, expected_weight=26, doc=doc, seniority=seniority
    )
    project_score = _project_score(text, raw_lines)
    foundation_score, foundation_missing, foundation_hits = _weighted_score(
        text, CORE_FOUNDATION, max_points=10, doc=doc, seniority=seniority
    )
    impact_score = _impact_score(text, raw_lines)
    ats_score, ats_issues = _ats_score(text)

    # Let's get the best fit role to estimate a 'role_score' and 'company_score' for the base score
    best_fit = _best_fit_roles(text)
    company_fit = _company_fit(text)

    top_role_id = best_fit[0]["id"] if best_fit else "gpu_software"
    top_company_id = company_fit[0]["id"] if company_fit else "general"
    
    role = ROLE_PROFILES.get(top_role_id, ROLE_PROFILES["gpu_software"])
    company = COMPANY_PROFILES.get(top_company_id, COMPANY_PROFILES["general"])

    role_must_score, _, _ = _weighted_score(text, role["must_have"], max_points=14, doc=doc, seniority=seniority)
    role_signal_score, _, _ = _weighted_score_with_expected(text, role["strong_signals"], max_points=6, expected_weight=16, doc=doc, seniority=seniority)
    role_score = min(20, role_must_score + role_signal_score)

    company_score, _, company_hits = _weighted_score_with_expected(
        text, company.get("keywords", {}), max_points=10, expected_weight=22, doc=doc, seniority=seniority
    )

    jd_missing: list[str] = []
    jd_bonus = 0
    if job_description.strip():
        jd_keywords = _extract_job_keywords(job_description)
        jd_score, jd_missing, _ = _weighted_score(text, jd_keywords, max_points=8, doc=doc, seniority=seniority)
        jd_bonus = min(5, jd_score // 2)

    base_score = (
        role_score
        + systems_score
        + specialization_score
        + project_score
        + foundation_score
        + impact_score
        + ats_score
    )
    score = min(100, base_score + min(5, company_score // 2) + jd_bonus)

    # detected signals should merge from best fit role and top company
    role_must_hits = [k for k, v in role["must_have"].items() if _contains(text, k)]
    role_signal_hits = [k for k, v in role["strong_signals"].items() if _contains(text, k)]
    detected = sorted(set(role_must_hits + role_signal_hits + systems_hits + specialization_hits + foundation_hits + company_hits))

    return BaseAnalysisResult(
        score=score,
        readiness=_readiness(score),
        best_fit_roles=best_fit,
        company_fit=company_fit,
        ats_issues=ats_issues,
        detected_signals=detected[:24],
    )


def generate_target_stats(
    resume_text: str,
    target_role: str,
    target_company: str,
    job_description: str = "",
    seniority: str = "mid"
) -> TargetStatsResult:
    text = _normalize(resume_text)
    raw_lines = [line.strip() for line in resume_text.splitlines() if line.strip()]
    doc = nlp(text) if nlp else None

    role_key = target_role if target_role in ROLE_PROFILES else "gpu_software"
    company_key = target_company if target_company in COMPANY_PROFILES else "general"
    role = ROLE_PROFILES[role_key]
    company = COMPANY_PROFILES[company_key]

    role_must_score, role_missing, role_must_hits = _weighted_score(text, role["must_have"], max_points=14, doc=doc, seniority=seniority)
    role_signal_score, role_signal_missing, role_signal_hits = _weighted_score_with_expected(
        text, role["strong_signals"], max_points=6, expected_weight=16, doc=doc, seniority=seniority
    )
    role_score = min(20, role_must_score + role_signal_score)
    role_missing = role_missing + role_signal_missing
    role_hits = role_must_hits + role_signal_hits

    systems_score, _, systems_hits = _weighted_score(text, _systems_keywords(), max_points=20, doc=doc, seniority=seniority)
    specialization_score, specialization_missing, specialization_hits = _weighted_score_with_expected(
        text, _specialization_keywords(), max_points=20, expected_weight=26, doc=doc, seniority=seniority
    )
    project_score = _project_score(text, raw_lines)
    foundation_score, _, foundation_hits = _weighted_score(text, CORE_FOUNDATION, max_points=10, doc=doc, seniority=seniority)
    impact_score = _impact_score(text, raw_lines)
    ats_score, ats_issues = _ats_score(text)
    company_score, company_missing, company_hits = _weighted_score_with_expected(
        text, company["keywords"], max_points=10, expected_weight=22, doc=doc, seniority=seniority
    )

    jd_missing: list[str] = []
    jd_bonus = 0
    if job_description.strip():
        jd_keywords = _extract_job_keywords(job_description)
        jd_score, jd_missing, _ = _weighted_score(text, jd_keywords, max_points=8, doc=doc, seniority=seniority)
        jd_bonus = min(5, jd_score // 2)

    base_score = (
        role_score
        + systems_score
        + specialization_score
        + project_score
        + foundation_score
        + impact_score
        + ats_score
    )
    score = min(100, base_score + min(5, company_score // 2) + jd_bonus)

    detected = sorted(set(role_hits + systems_hits + specialization_hits + foundation_hits + company_hits))
    missing = _rank_missing(role_missing + company_missing + specialization_missing + jd_missing)
    best_fit = _best_fit_roles(text)
    company_fit = _company_fit(text)

    pros = _pros(score, detected, project_score, impact_score, role["label"], company["label"])
    cons = _cons(missing, ats_issues, project_score, impact_score, specialization_score)
    rewrites = _rewrite_suggestions(raw_lines, role["label"])
    projects = _recommended_projects(role_key, missing)
    roadmap = _roadmap(role_key, company_key, missing, project_score, specialization_score)
    priority_actions = _priority_actions(missing, project_score, impact_score, score)
    highest_probability_path = _highest_probability_path(text, best_fit, company_fit, project_score, impact_score)

    company_stats = company.get("stats", {})
    # Use static salary matrix instead of dynamic fetching as requested
    compensation = _get_static_salary(company_key, role_key, seniority)
    company_stats["compensation"] = compensation

    return TargetStatsResult(
        score_breakdown={
            "role_fit": role_score,
            "systems_low_level": systems_score,
            "gpu_ai_compiler_specialization": specialization_score,
            "projects": project_score,
            "cs_fundamentals": foundation_score,
            "impact_metrics": impact_score,
            "ats_formatting": ats_score,
            "company_alignment_bonus": min(5, company_score // 2),
            "job_description_bonus": jd_bonus,
        },
        pros=pros,
        cons=cons,
        company_stats=company_stats,
        missing_skills=missing[:14],
        rewrite_suggestions=rewrites,
        roadmap=roadmap,
        recommended_projects=projects,
        highest_probability_path=highest_probability_path,
        priority_actions=priority_actions,
    )


def available_options() -> dict[str, Any]:
    return {
        "roles": [{"id": key, "label": value["label"]} for key, value in ROLE_PROFILES.items()],
        "companies": [{"id": key, "label": value["label"]} for key, value in COMPANY_PROFILES.items()],
    }


def _normalize(text: str) -> str:
    lowered = text.lower()
    lowered = lowered.replace("c plus plus", "c++")
    lowered = lowered.replace("c/c++", "c c++")
    lowered = lowered.replace("system software", "systems software")
    lowered = re.sub(r"\s+", " ", lowered)
    return lowered


def _contains(text: str, term: str) -> bool:
    term = term.lower()
    if term in {"c", "c++", "c#"}:
        return bool(re.search(rf"(?<![a-z0-9+#]){re.escape(term)}(?![a-z0-9+#])", text))
    return term in text

def _get_static_salary(company_key: str, role_key: str, seniority: str) -> str:
    # Base compensation matrix (Mid-level) in LPA
    base_salaries = {
        "nvidia": 30,
        "amd": 25,
        "qualcomm": 24,
        "intel": 22,
        "arm": 26,
        "broadcom": 28,
        "apple": 35,
        "tesla": 28,
        "meta_rl": 40,
        "cruise": 32,
        "synopsys": 24,
        "cadence": 24,
        "general": 18
    }
    
    base = base_salaries.get(company_key, 18)
    
    # Adjust for role specialization
    if role_key in ["gpu_software", "ai_performance"]:
        base *= 1.1
    elif role_key in ["compiler", "ai_infra"]:
        base *= 1.2
        
    # Adjust for seniority
    if seniority == "junior":
        base *= 0.6
    elif seniority == "senior":
        base *= 1.5
        
    # Create a realistic ±15% band
    low = round(base * 0.85, 1)
    high = round(base * 1.15, 1)
    
    low_str = f"{int(low)}" if low.is_integer() else f"{low}"
    high_str = f"{int(high)}" if high.is_integer() else f"{high}"
    
    return f"\u20b9{low_str} - \u20b9{high_str} LPA"

def _is_active_skill(doc: Any, text: str, term: str) -> bool:
    # If spacy is not loaded or term not found, fallback to basic check
    if doc is None or not _contains(text, term):
        return _contains(text, term)

    # Basic check for weak verbs
    weak_verbs = {"learn", "study", "familiar", "know", "read", "understand", "explore"}
    
    # We find sentences containing the term
    term_lower = term.lower()
    for sent in doc.sents:
        if term_lower in sent.text.lower():
            # Check if main verbs in the sentence are weak
            verbs = [token.lemma_.lower() for token in sent if token.pos_ == "VERB"]
            if verbs and all(v in weak_verbs for v in verbs):
                return False # Skill used in weak context
            return True
            
    return True

def _weighted_score(text: str, weights: dict[str, int], max_points: int, doc: Any = None, seniority: str = "mid") -> tuple[int, list[str], list[str]]:
    total_weight = sum(weights.values()) or 1
    hit_weight = 0
    missing = []
    hits = []
    
    # Adjust expectations based on seniority
    multiplier = 1.0
    if seniority == "junior":
        multiplier = 1.2 # Easier to score points
    elif seniority == "senior":
        multiplier = 0.8 # Harder to score points

    for term, weight in weights.items():
        if _is_active_skill(doc, text, term):
            hit_weight += weight
            hits.append(term)
        else:
            missing.append(term)
            
    score = round((hit_weight / total_weight) * max_points * multiplier)
    return min(max_points, score), missing, hits


def _weighted_score_with_expected(
    text: str,
    weights: dict[str, int],
    max_points: int,
    expected_weight: int,
    doc: Any = None,
    seniority: str = "mid"
) -> tuple[int, list[str], list[str]]:
    hit_weight = 0
    missing = []
    hits = []
    
    # Adjust expectations based on seniority
    expected = expected_weight
    if seniority == "junior":
        expected = max(1, expected_weight - 4)
    elif seniority == "senior":
        expected = expected_weight + 4

    for term, weight in weights.items():
        if _is_active_skill(doc, text, term):
            hit_weight += weight
            hits.append(term)
        else:
            missing.append(term)
    score = round((hit_weight / max(1, expected)) * max_points)
    return min(max_points, score), missing, hits


def _systems_keywords() -> dict[str, int]:
    return {
        "c++": 5,
        "c": 3,
        "linux": 5,
        "operating systems": 4,
        "memory management": 4,
        "multithreading": 4,
        "concurrency": 4,
        "debugging": 3,
        "gdb": 2,
        "performance": 4,
        "networking": 2,
        "kernel": 4,
        "drivers": 4,
    }


def _specialization_keywords() -> dict[str, int]:
    return {
        "cuda": 6,
        "rocm": 5,
        "hip": 4,
        "triton": 5,
        "llvm": 5,
        "mlir": 4,
        "compiler": 4,
        "pytorch": 3,
        "tensorrt": 4,
        "vulkan": 3,
        "opencl": 3,
        "firmware": 3,
        "device driver": 4,
        "profiling": 4,
        "gpu": 5,
    }


def _project_score(text: str, lines: list[str]) -> int:
    has_projects = "project" in text or any("github" in line.lower() for line in lines)
    if not has_projects:
        return 3

    score = 7
    project_terms = [
        "cuda",
        "gpu",
        "compiler",
        "linux",
        "kernel",
        "driver",
        "firmware",
        "triton",
        "pytorch",
        "vulkan",
        "rocm",
        "performance",
        "benchmark",
    ]
    score += min(5, sum(1 for term in project_terms if _contains(text, term)))
    score += min(3, _metric_count(text))
    return min(15, score)


def _impact_score(text: str, lines: list[str]) -> int:
    hits = sum(1 for term in IMPACT_TERMS if term in text)
    metrics = _metric_count(text)
    action_lines = sum(
        1
        for line in lines
        if re.match(r"^[-*]?\s*(built|developed|optimized|implemented|designed|created|reduced|improved)", line.lower())
    )
    return min(10, hits // 2 + metrics + min(3, action_lines))


def _metric_count(text: str) -> int:
    return len(re.findall(r"(\d+(\.\d+)?\s*(%|x|ms|s|gb|mb|kb|qps|fps|lpa|users|requests|seconds|minutes))", text))


def _ats_score(text: str) -> tuple[int, list[str]]:
    issues = []
    present = [section for section in ATS_SECTIONS if section in text]
    score = min(5, 1 + len(set(present)))
    if "skills" not in text:
        issues.append("Add a clear Skills section grouped by language, systems, GPU/AI, and tools.")
    if "projects" not in text and "project" not in text:
        issues.append("Add a Projects section because hardware-company software roles reward proof of depth.")
    if len(text.split()) < 250:
        issues.append("Resume text looks too short; add technical bullets with project depth and impact.")
        score = max(1, score - 1)
    if len(text.split()) > 900:
        issues.append("Resume may be too dense; keep it closer to one focused page if you are early career.")
    return score, issues


def _extract_job_keywords(job_description: str) -> dict[str, int]:
    jd = _normalize(job_description)
    known = _systems_keywords() | _specialization_keywords() | CORE_FOUNDATION
    extracted = {term: weight for term, weight in known.items() if _contains(jd, term)}
    return extracted or known


def _rank_missing(missing: list[str]) -> list[str]:
    priority = {
        "c++": 100,
        "linux": 95,
        "cuda": 92,
        "gpu": 90,
        "performance": 88,
        "profiling": 84,
        "operating systems": 82,
        "rocm": 80,
        "hip": 78,
        "triton": 76,
        "llvm": 74,
        "compiler": 72,
        "pytorch": 70,
        "memory management": 68,
        "multithreading": 66,
    }
    unique = sorted(set(missing), key=lambda item: (-priority.get(item, 0), item))
    return unique


def _best_fit_roles(text: str) -> list[dict[str, Any]]:
    fits = []
    for key, profile in ROLE_PROFILES.items():
        must_score, _, must_hits = _weighted_score(profile_text := text, profile["must_have"], max_points=70)
        signal_score, _, signal_hits = _weighted_score_with_expected(
            profile_text, profile["strong_signals"], max_points=30, expected_weight=16
        )
        score = min(100, must_score + signal_score)
        hits = must_hits + signal_hits
        fits.append({"id": key, "label": profile["label"], "score": score, "matched": hits[:6]})
    return sorted(fits, key=lambda item: item["score"], reverse=True)[:3]


def _company_fit(text: str) -> list[dict[str, Any]]:
    fits = []
    for key, profile in COMPANY_PROFILES.items():
        if key == "general":
            continue
        score, missing, hits = _weighted_score_with_expected(
            text, profile["keywords"], max_points=100, expected_weight=22
        )
        fits.append(
            {
                "id": key,
                "label": profile["label"],
                "score": score,
                "matched": hits[:7],
                "missing": _rank_missing(missing)[:5],
            }
        )
    return sorted(fits, key=lambda item: item["score"], reverse=True)


def _pros(
    score: int,
    detected: list[str],
    project_score: int,
    impact_score: int,
    role_label: str,
    company_label: str,
) -> list[str]:
    pros = []
    if score >= 75:
        pros.append(f"Strong baseline for {role_label} roles at {company_label}.")
    elif score >= 60:
        pros.append(f"Promising baseline for {role_label}, with clear upgrade points.")
    else:
        pros.append("Good starting point, but the resume needs sharper low-level software evidence.")
    if detected:
        pros.append("Detected relevant signals: " + ", ".join(detected[:8]) + ".")
    if project_score >= 11:
        pros.append("Projects show enough technical direction to build a strong hardware-company narrative.")
    if impact_score >= 7:
        pros.append("Impact language and metrics are present, which helps with premium compensation roles.")
    return pros[:5]


def _cons(
    missing: list[str],
    ats_issues: list[str],
    project_score: int,
    impact_score: int,
    specialization_score: int,
) -> list[str]:
    cons = []
    if specialization_score < 10:
        cons.append("Specialization is not yet strong enough for NVIDIA/AMD-style shortlists.")
    if project_score < 10:
        cons.append("Projects need more systems, GPU, compiler, firmware, or performance depth.")
    if impact_score < 6:
        cons.append("Bullets need measurable results such as speedup, latency, throughput, memory, or scale.")
    if missing:
        cons.append("Missing high-value keywords: " + ", ".join(missing[:7]) + ".")
    cons.extend(ats_issues[:2])
    return cons[:6]


def _rewrite_suggestions(lines: list[str], role_label: str) -> list[dict[str, str]]:
    weak = []
    for line in lines:
        stripped = line.strip("-* ")
        if 30 <= len(stripped) <= 180 and not _has_metric(stripped):
            if any(term in stripped.lower() for term in ["project", "built", "developed", "created", "worked", "made", "implemented"]):
                weak.append(stripped)
        if len(weak) == 3:
            break

    suggestions = []
    for line in weak:
        suggestions.append(
            {
                "before": line,
                "after": _rewrite_line(line, role_label),
            }
        )
    if not suggestions:
        suggestions.append(
            {
                "before": "Built a machine learning project using Python.",
                "after": "Optimized a Python/PyTorch inference pipeline, benchmarked latency and throughput, and documented the bottlenecks relevant to GPU software roles.",
            }
        )
    return suggestions


def _has_metric(text: str) -> bool:
    return bool(re.search(r"\d", text)) or any(term in text.lower() for term in ["latency", "throughput", "speedup"])


def _rewrite_line(line: str, role_label: str) -> str:
    base = re.sub(r"\s+", " ", line).rstrip(".")
    return (
        f"{base}; add benchmark evidence such as runtime, latency, throughput, memory usage, "
        f"or speedup to make it credible for {role_label} shortlists."
    )


def _recommended_projects(role_key: str, missing: list[str]) -> list[str]:
    projects = list(ROLE_PROFILES[role_key]["project_ideas"])
    if "c++" in missing:
        projects.append("Modern C++ systems project using threads, RAII, profiling, and tests.")
    if "linux" in missing:
        projects.append("Linux debugging project with gdb, perf, strace, and a short technical write-up.")
    return projects[:5]


def _roadmap(
    role_key: str,
    company_key: str,
    missing: list[str],
    project_score: int,
    specialization_score: int,
) -> dict[str, list[str]]:
    company = COMPANY_PROFILES[company_key]["label"]
    role = ROLE_PROFILES[role_key]["label"]
    top_missing = missing[:5]
    return {
        "30_days": [
            "Polish C++, OS, DSA, and Linux fundamentals with daily problem solving and notes.",
            "Rewrite resume bullets with action, tool, outcome, and metric.",
            f"Collect 8-12 keywords from current {company} job posts for {role}.",
        ],
        "60_days": [
            "Build one specialization project: CUDA/ROCm, compiler, systems, firmware, graphics, or AI performance.",
            "Add benchmark tables and profiling screenshots or logs to the project README.",
            "Close these gaps first: " + (", ".join(top_missing) if top_missing else "company-specific keywords."),
        ],
        "90_days": [
            "Create a second deeper project that shows performance engineering or low-level debugging.",
            "Prepare role-specific resume versions for NVIDIA, AMD, Qualcomm, Intel, and EDA companies.",
            "Practice interviews: DSA, C++ internals, OS, concurrency, and project deep dives.",
        ],
        "120_days": [
            "Apply in focused batches with referrals and a tailored resume for each role.",
            "Publish short technical write-ups for your strongest projects.",
            "Track callback rate and improve resume keywords every 15 applications.",
        ],
    }


def _priority_actions(missing: list[str], project_score: int, impact_score: int, score: int) -> list[str]:
    actions = []
    if score < 70:
        actions.append("Choose one role track and stop presenting the resume as generic software engineering.")
    if project_score < 11:
        actions.append("Add one project with measurable performance results before applying aggressively.")
    if impact_score < 7:
        actions.append("Rewrite bullets to include numbers: speedup, latency, throughput, memory, scale, or rank.")
    for skill in missing[:3]:
        actions.append(f"Add credible evidence for {skill}, either through a project or coursework.")
    return actions[:6]


def _highest_probability_path(
    text: str,
    best_fit: list[dict[str, Any]],
    company_fit: list[dict[str, Any]],
    project_score: int,
    impact_score: int,
) -> list[str]:
    top_role = best_fit[0] if best_fit else {"label": "Systems Software Engineer", "id": "systems_software"}
    top_company = company_fit[0] if company_fit else {"label": "NVIDIA", "missing": []}
    role_profile = ROLE_PROFILES.get(top_role["id"], ROLE_PROFILES["systems_software"])
    _, role_missing, _ = _weighted_score(text, role_profile["must_have"], max_points=10)

    path = [
        f"Best current path: aim first for {top_role['label']} roles at {top_company['label']}-style companies.",
        "There is no honest resume-only guarantee, but you can raise shortlist probability by closing the exact evidence gaps below.",
    ]

    missing = _rank_missing(role_missing + top_company.get("missing", []))
    if missing:
        path.append("Add credible resume evidence for: " + ", ".join(missing[:6]) + ".")
    if project_score < 12:
        path.append("Build one flagship project with benchmarks, code, README, and technical tradeoffs.")
    if impact_score < 8:
        path.append("Rewrite every major bullet with measurable proof: speedup, latency, throughput, memory, scale, or rank.")
    path.append("Apply with a tailored resume version for each company instead of one generic resume.")
    path.append("Prepare interview proof for the same story: C++, OS, DSA, debugging, and a deep project walkthrough.")
    return path[:7]


def _readiness(score: int) -> str:
    if score >= 85:
        return "High for INR 40 LPA+ shortlists"
    if score >= 70:
        return "Medium-high; close gaps before premium applications"
    if score >= 55:
        return "Medium; needs stronger specialization proof"
    return "Low; build role-specific projects first"
