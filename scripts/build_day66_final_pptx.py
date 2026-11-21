"""Build 20-slide OpenXML (.pptx) presentation for Day 66 with embedded real diagrams & screenshots."""

from __future__ import annotations

import html
import struct
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DAY66 = ROOT / "day66_presentation_preparation"
OUT_PPTX = DAY66 / "presentation" / "ZecPath_Final_Presentation.pptx"
DIAG = DAY66 / "diagrams"
SHOTS = DAY66 / "screenshots"


def _png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        w, h = struct.unpack(">II", data[16:24])
        return w, h
    return 1440, 900


# Slide definitions: (title, bullets, optional_image_path)
SLIDES: list[tuple[str, list[str], Path | None]] = [
    ("ZecPath AI Hiring System", [
        "AI-Powered Resume Screening, Multi-Round Evaluation & Governance Platform",
        "70-Day Engineering Portfolio | FastAPI + SQLite + Local NLP + Vanilla JS",
        "Decision-Support Architecture: Human-in-the-Loop Mandatory",
    ], None),
    ("Project Introduction", [
        "Local-first recruitment evaluation platform built across 70 structured milestones.",
        "Unifies resume parsing, ATS scoring, eligibility, screening, interviews, and reporting.",
        "125 REST endpoints (/api/v1/*) + single-page recruiter workspace (static/index.html).",
    ], SHOTS / "01_dashboard.png"),
    ("Problem Statement", [
        "Recruitment pipelines fragment evidence across spreadsheets, ATS tools, and interview notes.",
        "Silent zero-penalties for uncompleted interview rounds distort candidate comparisons.",
        "Opaque automated rejections create compliance, fairness, and auditability risks.",
    ], None),
    ("Existing Recruitment Challenges", [
        "Manual resume screening is slow and inconsistent across job openings.",
        "Lack of structured rubrics across HR, technical, and coding assessments.",
        "Missing audit trails and inability to explain why a candidate was shortlisted or held.",
    ], None),
    ("Proposed AI Solution (ZecPath)", [
        "Transparent 4-factor ATS scoring with exact resume snippet evidence.",
        "Non-punitive behavioral & integrity signals that flag for human review only.",
        "Configurable role-weighted cross-round aggregation with missing-stage renormalization.",
    ], None),
    ("Project Objectives", [
        "Automate structured extraction and deterministic rubric evaluation.",
        "Preserve mandatory human review for every consequential hiring decision.",
        "Provide tamper-evident SHA-256 audit logging and 14-section Hiring Intelligence Reports.",
    ], None),
    ("Complete System Architecture", [
        "Frontend: Vanilla JS workspace (static/index.html) + Swagger (/docs).",
        "Backend: FastAPI (src/main.py, src/api.py) with PBKDF2-SHA256 & RBAC.",
        "Storage & Logs: SQLite (src/database.py) + JSONL observability telemetry.",
    ], DIAG / "system_architecture.png"),
    ("Technology Stack Actually Used", [
        "Backend: Python 3.12, FastAPI, Uvicorn, Pydantic schemas, SQLite.",
        "Frontend: Vanilla HTML5 / CSS3 / JavaScript (no external SPA build step).",
        "AI / Analysis: Local sentence embeddings + deterministic NLP/AST rubrics.",
        "Testing & QA: Pytest suite + Playwright headless Chrome E2E verification.",
    ], None),
    ("Overall Hiring Pipeline (10 Stages)", [
        "Resume Upload -> Parsing -> ATS -> Eligibility -> Screening -> HR -> Tech -> Machine Test.",
        "Stages feed Cross-Round Aggregation -> Final Recommendation -> Human Review -> Report.",
    ], DIAG / "hiring_pipeline.png"),
    ("Resume Upload & Parsing", [
        "Async 202 upload (POST /api/v1/resumes/upload) for TXT, DOCX, PDF (<= 5 MiB).",
        "Background processing_jobs extract sections, skills, experience, and education.",
    ], SHOTS / "02_resume_upload.png"),
    ("ATS Scoring & Candidate Matching", [
        "Formula: 0.40 * Skills + 0.25 * Semantic + 0.20 * Experience + 0.15 * Education.",
        "Whole-word skill matching + exact evidence snippets returned in API & UI.",
    ], SHOTS / "04_ats_score_breakdown.png"),
    ("Eligibility & Screening Evaluation", [
        "Mandatory eligibility rules classify ELIGIBLE, REVIEW_REQUIRED, or REJECTED.",
        "Screening pipeline evaluates clarity, relevance, completeness, and consistency.",
    ], SHOTS / "05_screening_output.png"),
    ("HR Interview Assessment", [
        "Role- and experience-aware question bank with dynamic follow-up triggers.",
        "Evaluates communication fluency, filler words, hesitation, and aptitude.",
    ], SHOTS / "06_interview_assessments.png"),
    ("Technical Interview & Machine Test", [
        "Technical Interview: 5-dimension rubric + depth classification (shallow/moderate/deep).",
        "Machine Test: AST & static rubric analysis (limitation: no OS container sandbox).",
    ], SHOTS / "07_technical_machine_test.png"),
    ("Cross-Round Scoring & Aggregation", [
        "Combines 5 stages using role_weight_configurations.",
        "Missing stages use exclude_and_renormalize; SHA-256 input_fingerprint prevents duplicates.",
    ], DIAG / "ai_module_interaction.png"),
    ("Final Recommendation & Human Review", [
        "Classifies SELECTED, HOLD_REVIEW, or REJECTED; eligibility failure overrides high scores.",
        "Recruiter APPROVE / OVERRIDE / REJECT logged in recommendation_decision_history.",
    ], SHOTS / "09_final_recommendation.png"),
    ("Hiring Intelligence Report", [
        "14-section executive report generated from persisted multi-stage evidence.",
        "Exportable in JSON, HTML, Markdown, and PDF 1.4 formats.",
    ], SHOTS / "10_hiring_intelligence_report.png"),
    ("Data Flow, Security & Observability", [
        "PBKDF2 auth, 4 RBAC roles, tenant isolation, SHA-256 hash-chained audit_events.",
        "ObservabilityASGIMiddleware tracks P50/P95 latency, error rate, and alerts.",
    ], DIAG / "data_flow.png"),
    ("Actual End-to-End Demo Results (Day 63 Data)", [
        "Aarav Sharma (Strong Python): 92.0% Fit -> SELECTED | Pooja Hegde (Data): 92.0% -> SELECTED.",
        "Meera Patel (Partial): 72.0% -> HOLD_REVIEW | Rohan Verma (Low): 44.0% -> REJECTED.",
        "Live E2E uploaded candidate verified through all 10 stages + human approval.",
    ], SHOTS / "08_cross_round_score.png"),
    ("Limitations, Roadmap & Q&A", [
        "Honest Limitations: Prototype SQLite, AST-only code check, synthetic 12-case benchmark.",
        "Roadmap: Candidate-facing screening UI, PostgreSQL pooling, micro-VM code sandbox.",
        "Thank you — Ready for live application demonstration and Q&A.",
    ], None),
]


def build_pptx() -> None:
    OUT_PPTX.parent.mkdir(parents=True, exist_ok=True)
    slide_count = len(SLIDES)
    slide_overrides = "\n".join(
        f'  <Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        for i in range(1, slide_count + 1)
    )
    content_types = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-officedocument.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="png" ContentType="image/png"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
  <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
{slide_overrides}
</Types>"""

    root_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
</Relationships>"""

    sld_ids = "\n".join(
        f'    <p:sldId id="{255 + i}" r:id="rId{i + 1}"/>'
        for i in range(1, slide_count + 1)
    )
    presentation_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>
  <p:sldIdLst>
{sld_ids}
  </p:sldIdLst>
  <p:sldSz cx="12192000" cy="6858000"/>
  <p:notesSz cx="6858000" cy="9144000"/>
</p:presentation>"""

    pres_rels_items = "\n".join(
        f'  <Relationship Id="rId{i + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>'
        for i in range(1, slide_count + 1)
    )
    pres_rels = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>
{pres_rels_items}
</Relationships>"""

    slide_master = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/></p:spTree></p:cSld>
  <p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>
  <p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst>
</p:sldMaster>"""

    slide_master_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>
</Relationships>"""

    slide_layout = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank">
  <p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/></p:spTree></p:cSld>
</p:sldLayout>"""

    slide_layout_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>"""

    theme_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="ZecPathTheme">
  <a:themeElements>
    <a:clrScheme name="ZecPath">
      <a:dk1><a:srgbClr val="102A43"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1>
      <a:dk2><a:srgbClr val="334E68"/></a:dk2><a:lt2><a:srgbClr val="F3F6F9"/></a:lt2>
      <a:accent1><a:srgbClr val="176B87"/></a:accent1><a:accent2><a:srgbClr val="0F766E"/></a:accent2>
      <a:accent3><a:srgbClr val="D99000"/></a:accent3><a:accent4><a:srgbClr val="176B3A"/></a:accent4>
      <a:accent5><a:srgbClr val="486581"/></a:accent5><a:accent6><a:srgbClr val="A4262C"/></a:accent6>
      <a:hlink><a:srgbClr val="176B87"/></a:hlink><a:folHlink><a:srgbClr val="486581"/></a:folHlink>
    </a:clrScheme>
    <a:fontScheme name="ZecPathFonts"><a:majorFont><a:latin typeface="Calibri"/></a:majorFont><a:minorFont><a:latin typeface="Calibri"/></a:minorFont></a:fontScheme>
    <a:fmtScheme name="ZecPathFmt"><a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst><a:lnStyleLst><a:ln w="9525"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst><a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst><a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst></a:fmtScheme>
  </a:themeElements>
</a:theme>"""

    with zipfile.ZipFile(OUT_PPTX, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", root_rels)
        zf.writestr("ppt/presentation.xml", presentation_xml)
        zf.writestr("ppt/_rels/presentation.xml.rels", pres_rels)
        zf.writestr("ppt/slideMasters/slideMaster1.xml", slide_master)
        zf.writestr("ppt/_rels/slideMasters/slideMaster1.xml.rels", slide_master_rels)
        zf.writestr("ppt/slideLayouts/slideLayout1.xml", slide_layout)
        zf.writestr("ppt/_rels/slideLayouts/slideLayout1.xml.rels", slide_layout_rels)
        zf.writestr("ppt/theme/theme1.xml", theme_xml)

        media_idx = 0
        for idx, (title, bullets, img_path) in enumerate(SLIDES, start=1):
            has_img = img_path is not None and img_path.exists()
            body_w = 5400000 if has_img else 10800000
            font_sz = 1600 if has_img else 2000
            paras = "\n".join(
                f'<a:p><a:pPr marL="270000" indent="-270000"><a:buChar char="•"/></a:pPr>'
                f'<a:r><a:rPr lang="en-US" sz="{font_sz}" dirty="0"><a:solidFill><a:srgbClr val="172433"/></a:solidFill></a:rPr>'
                f'<a:t>{html.escape(b)}</a:t></a:r></a:p>'
                for b in bullets
            )

            pic_xml = ""
            rel_extra = ""
            if has_img:
                media_idx += 1
                media_name = f"image{media_idx}.png"
                zf.write(img_path, f"ppt/media/{media_name}")
                pw, ph = _png_size(img_path)
                max_w, max_h = 5600000, 4600000
                scale = min(max_w / pw, max_h / ph)
                cx, cy = int(pw * scale), int(ph * scale)
                pic_xml = f"""
      <p:pic>
        <p:nvPicPr><p:cNvPr id="4" name="Image {media_idx}"/><p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>
        <p:blipFill><a:blip r:embed="rId2"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>
        <p:spPr><a:xform><a:off x="6250000" y="1450000"/><a:ext cx="{cx}" cy="{cy}"/></a:xform><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>
      </p:pic>"""
                rel_extra = f'\n  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/{media_name}"/>'

            slide_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr/>
      <p:sp>
        <p:nvSpPr><p:cNvPr id="2" name="Title"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:spPr><a:xform><a:off x="550000" y="380000"/><a:ext cx="11000000" cy="780000"/></a:xform><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:solidFill><a:srgbClr val="102A43"/></a:solidFill></p:spPr>
        <p:txBody><a:bodyPr anchor="ctr" lIns="180000"/><a:lstStyle/><a:p><a:r><a:rPr lang="en-US" sz="2400" b="1" dirty="0"><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill></a:rPr><a:t>{idx}. {html.escape(title)}</a:t></a:r></a:p></p:txBody>
      </p:sp>
      <p:sp>
        <p:nvSpPr><p:cNvPr id="3" name="Body"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:spPr><a:xform><a:off x="550000" y="1450000"/><a:ext cx="{body_w}" cy="4800000"/></a:xform><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>
        <p:txBody><a:bodyPr wrap="square"/><a:lstStyle/>{paras}</p:txBody>
      </p:sp>{pic_xml}
    </p:spTree>
  </p:cSld>
</p:sld>"""
            slide_rels = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>{rel_extra}
</Relationships>"""
            zf.writestr(f"ppt/slides/slide{idx}.xml", slide_xml)
            zf.writestr(f"ppt/_rels/slides/slide{idx}.xml.rels", slide_rels)

    print(f"Built {OUT_PPTX} with {slide_count} slides.")


if __name__ == "__main__":
    build_pptx()
