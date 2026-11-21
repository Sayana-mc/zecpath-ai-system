"""Generate 4 genuine architecture/pipeline/interaction/data-flow PNG diagrams for Day 66."""

from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parent.parent
DIAG_DIR = ROOT / "day66_presentation_preparation" / "diagrams"


def _box(ax, x, y, w, h, title, subtitle="", fc="#e6f2f5", ec="#176b87", tc="#102a43"):
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.03",
        facecolor=fc, edgecolor=ec, linewidth=1.8,
    )
    ax.add_patch(patch)
    if subtitle:
        ax.text(x + w / 2, y + h * 0.64, title, ha="center", va="center", fontsize=10, fontweight="bold", color=tc)
        ax.text(x + w / 2, y + h * 0.30, subtitle, ha="center", va="center", fontsize=8, color="#334e68")
    else:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center", fontsize=10, fontweight="bold", color=tc)


def _arrow(ax, x1, y1, x2, y2, label="", color="#334e68"):
    arr = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=13, linewidth=1.5, color=color)
    ax.add_patch(arr)
    if label:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.02, label, ha="center", va="bottom", fontsize=7.5, color=color)


def make_system_architecture():
    fig, ax = plt.subplots(figsize=(12, 7), dpi=180)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("ZecPath AI Hiring System — Actual System Architecture", fontsize=14, fontweight="bold", color="#102a43", pad=12)

    _box(ax, 0.04, 0.75, 0.22, 0.16, "Recruiter User", "Browser / Swagger Client", fc="#fff7df", ec="#d99000")
    _box(ax, 0.34, 0.75, 0.28, 0.16, "Frontend Workspace", "static/index.html (Vanilla JS)\n6 Tabs + Login + Monitoring", fc="#e6f2f5", ec="#176b87")
    _box(ax, 0.70, 0.75, 0.26, 0.16, "Swagger OpenAPI", "/docs & /openapi.json\n125 /api/v1/* Endpoints", fc="#e6f2f5", ec="#176b87")

    _box(ax, 0.10, 0.48, 0.80, 0.18, "FastAPI Application (src/main.py + src/api.py)",
         "Auth (PBKDF2 + HTTP-only Cookie / Basic) | ObservabilityASGIMiddleware | Validation & RBAC",
         fc="#d9e2ec", ec="#102a43")

    _box(ax, 0.04, 0.22, 0.28, 0.18, "ATS & Screening Engines", "resume_analysis, ats_scoring_engine,\neligibility, screening_pipeline", fc="#e3fcec", ec="#176b3a")
    _box(ax, 0.36, 0.22, 0.28, 0.18, "Interview & Tech Engines", "hr_interview_pipeline, technical_*\nmachine_test_engine (AST)", fc="#e3fcec", ec="#176b3a")
    _box(ax, 0.68, 0.22, 0.28, 0.18, "Decision & Governance", "cross_round, final_recommendation,\nreport_generator, security_governance", fc="#e3fcec", ec="#176b3a")

    _box(ax, 0.08, 0.03, 0.38, 0.12, "SQLite Persistence (src/database.py)", "data/zecpath.sqlite3 | FK + SHA-256 audit_events", fc="#f0f4f8", ec="#486581")
    _box(ax, 0.54, 0.03, 0.38, 0.12, "Files, Logs & Reports", "uploads/, logs/*.jsonl, JSON/HTML/MD/PDF reports", fc="#f0f4f8", ec="#486581")

    _arrow(ax, 0.26, 0.83, 0.34, 0.83, "HTTP")
    _arrow(ax, 0.48, 0.75, 0.48, 0.66, "REST /api/v1")
    _arrow(ax, 0.83, 0.75, 0.75, 0.66, "API Calls")
    _arrow(ax, 0.25, 0.48, 0.18, 0.40)
    _arrow(ax, 0.50, 0.48, 0.50, 0.40)
    _arrow(ax, 0.75, 0.48, 0.82, 0.40)
    _arrow(ax, 0.27, 0.22, 0.27, 0.15)
    _arrow(ax, 0.50, 0.22, 0.35, 0.15)
    _arrow(ax, 0.82, 0.22, 0.73, 0.15)

    fig.tight_layout()
    fig.savefig(DIAG_DIR / "system_architecture.png", bbox_inches="tight")
    plt.close(fig)


def make_hiring_pipeline():
    fig, ax = plt.subplots(figsize=(13, 5.5), dpi=180)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("ZecPath Complete 10-Stage Hiring Pipeline", fontsize=14, fontweight="bold", color="#102a43", pad=12)

    top_stages = [
        ("1. Resume Upload", "TXT/DOCX/PDF\n202 Async Job"),
        ("2. ATS Scoring", "40/25/20/15\nWeighted Match"),
        ("3. Eligibility", "Mandatory Skills\n& Tenure Gate"),
        ("4. Screening", "Text/Audio\n4-Factor Rubric"),
        ("5. HR Interview", "Follow-ups +\nCommunication"),
    ]
    bot_stages = [
        ("6. Tech Interview", "Role Questions\n5-Dim Rubric"),
        ("7. Machine Test", "AST & Static\nCode Analysis"),
        ("8. Cross-Round", "Role Weights +\nRenormalization"),
        ("9. Final Rec", "SELECTED / HOLD\n/ REJECTED"),
        ("10. Human Review", "Recruiter Sign-off\n+ 14-Sec Report"),
    ]

    for i, (t, s) in enumerate(top_stages):
        x = 0.03 + i * 0.195
        _box(ax, x, 0.58, 0.165, 0.24, t, s, fc="#e6f2f5", ec="#176b87")
        if i < 4:
            _arrow(ax, x + 0.165, 0.70, x + 0.195, 0.70)

    _arrow(ax, 0.89, 0.58, 0.89, 0.42)

    for i, (t, s) in enumerate(reversed(bot_stages)):
        x = 0.03 + (4 - i) * 0.195
        fc = "#fff7df" if "Human" in t else "#e3fcec"
        ec = "#d99000" if "Human" in t else "#176b3a"
        _box(ax, x, 0.18, 0.165, 0.24, t, s, fc=fc, ec=ec)
        if i < 4:
            _arrow(ax, x, 0.30, x - 0.03, 0.30)

    fig.tight_layout()
    fig.savefig(DIAG_DIR / "hiring_pipeline.png", bbox_inches="tight")
    plt.close(fig)


def make_ai_module_interaction():
    fig, ax = plt.subplots(figsize=(12, 6.5), dpi=180)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("ZecPath Module Interaction & Non-Punitive Safeguards", fontsize=14, fontweight="bold", color="#102a43", pad=12)

    _box(ax, 0.04, 0.68, 0.25, 0.20, "Resume & ATS Engine", "resume_analysis.py\nats_scoring_engine.py", fc="#e6f2f5", ec="#176b87")
    _box(ax, 0.37, 0.68, 0.25, 0.20, "Assessment Engines", "screening_pipeline.py\nhr_interview_pipeline.py\ntechnical_*, machine_test", fc="#e6f2f5", ec="#176b87")
    _box(ax, 0.70, 0.68, 0.26, 0.20, "Safeguard Signals", "integrity_engine.py\nbehavioral_ai_engine.py\n(Non-Punitive Only)", fc="#fff7df", ec="#d99000")

    _box(ax, 0.18, 0.36, 0.28, 0.20, "Cross-Round Engine", "cross_round_scoring_engine.py\nexclude_and_renormalize", fc="#e3fcec", ec="#176b3a")
    _box(ax, 0.54, 0.36, 0.28, 0.20, "Recommendation Engine", "final_recommendation_engine.py\nConfidence + Eligibility Override", fc="#e3fcec", ec="#176b3a")

    _box(ax, 0.18, 0.06, 0.28, 0.18, "Report Generator", "hiring_intelligence_report_\ngenerator.py (14 Sections)", fc="#f0f4f8", ec="#486581")
    _box(ax, 0.54, 0.06, 0.28, 0.18, "Audit & Observability", "security_governance.py\nobservability.py", fc="#f0f4f8", ec="#486581")

    _arrow(ax, 0.16, 0.68, 0.28, 0.56)
    _arrow(ax, 0.49, 0.68, 0.36, 0.56)
    _arrow(ax, 0.83, 0.68, 0.70, 0.56, "Review Flag")
    _arrow(ax, 0.46, 0.46, 0.54, 0.46)
    _arrow(ax, 0.68, 0.36, 0.32, 0.24)
    _arrow(ax, 0.68, 0.36, 0.68, 0.24)

    fig.tight_layout()
    fig.savefig(DIAG_DIR / "ai_module_interaction.png", bbox_inches="tight")
    plt.close(fig)


def make_data_flow():
    fig, ax = plt.subplots(figsize=(12, 6), dpi=180)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("ZecPath End-to-End Data Flow & Storage", fontsize=14, fontweight="bold", color="#102a43", pad=12)

    _box(ax, 0.04, 0.58, 0.19, 0.24, "Input Artifacts", "Job JSON, Candidate\nProfile, Resume File", fc="#fff7df", ec="#d99000")
    _box(ax, 0.29, 0.58, 0.19, 0.24, "Processing Jobs", "uploads/ + SQLite\nprocessing_jobs", fc="#e6f2f5", ec="#176b87")
    _box(ax, 0.54, 0.58, 0.19, 0.24, "Stage Evaluations", "ATS, Eligibility,\nScreening, HR, Tech, MT", fc="#e3fcec", ec="#176b3a")
    _box(ax, 0.79, 0.58, 0.17, 0.24, "Final Decision", "Cross-Round +\nRecommendation", fc="#e3fcec", ec="#176b3a")

    _box(ax, 0.12, 0.14, 0.34, 0.22, "SQLite Database (zecpath.sqlite3)", "openings, candidates, stage scores,\nrecommendation_decision_history,\naudit_events (SHA-256 chain)", fc="#f0f4f8", ec="#486581")
    _box(ax, 0.54, 0.14, 0.34, 0.22, "Exported Reports & Telemetry", "Hiring Intelligence Report\n(JSON, HTML, MD, PDF 1.4)\n+ logs/*.jsonl", fc="#f0f4f8", ec="#486581")

    _arrow(ax, 0.23, 0.70, 0.29, 0.70)
    _arrow(ax, 0.48, 0.70, 0.54, 0.70)
    _arrow(ax, 0.73, 0.70, 0.79, 0.70)
    _arrow(ax, 0.38, 0.58, 0.29, 0.36)
    _arrow(ax, 0.63, 0.58, 0.35, 0.36)
    _arrow(ax, 0.87, 0.58, 0.71, 0.36)

    fig.tight_layout()
    fig.savefig(DIAG_DIR / "data_flow.png", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    DIAG_DIR.mkdir(parents=True, exist_ok=True)
    make_system_architecture()
    make_hiring_pipeline()
    make_ai_module_interaction()
    make_data_flow()
    print("Generated 4 diagrams in", DIAG_DIR)


if __name__ == "__main__":
    main()
