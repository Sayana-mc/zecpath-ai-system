"""Pure-Python OpenXML (.pptx) generator for Day 66 ZecPath Demo Presentation."""

from __future__ import annotations

import html
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_PPTX = ROOT / "final_submission" / "09_Presentation" / "day66_zecpath_demo_presentation.pptx"

SLIDES = [
    ("ZecPath AI Hiring System", [
        "AI-Powered Resume Screening, Multi-Round Evaluation & Governance Platform",
        "70-Day Engineering Portfolio | FastAPI + SQLite + Local NLP + Vanilla JS",
        "Decision-Support Architecture: Human-in-the-Loop Mandatory",
    ]),
    ("Problem Statement & Objectives", [
        "Fragmented hiring pipelines lose evidence between ATS, screening, and interviews.",
        "Silent zero-penalties for missing rounds distort candidate comparisons.",
        "Objective: Unified, auditable, non-punitive, role-weighted evaluation platform.",
    ]),
    ("System Architecture", [
        "Frontend: Vanilla HTML/CSS/JS Recruiter Workspace (static/index.html) at /",
        "Backend: FastAPI REST API (src/api.py mounted at /api/v1) + Swagger (/docs)",
        "Persistence: SQLite (data/zecpath.sqlite3 via src/database.py) with FK & migrations",
        "Observability: ObservabilityASGIMiddleware + structured JSONL telemetry logs",
    ]),
    ("Resume Parsing & 4-Factor ATS Scoring", [
        "Async upload via POST /api/v1/resumes/upload (202 Accepted + processing_jobs)",
        "Extracts text (TXT, PDF, DOCX), sections, skills, experience, education",
        "ATS Formula: 0.40*Skills + 0.25*Semantic + 0.20*Experience + 0.15*Education",
    ]),
    ("Mandatory Eligibility & Multi-Stage Assessments", [
        "Eligibility Engine (src/eligibility.py): ELIGIBLE, REVIEW, or REJECTED",
        "API-Only Assessment Stages: Screening, HR Interview, Technical Interview, Machine Test",
        "Non-Punitive Safeguards: Integrity & behavioral signals trigger human review only",
        "Honest Limitation: Machine test uses AST/static checks (no OS/container sandbox)",
    ]),
    ("Day 51: Cross-Round Aggregation Engine", [
        "Combines 5 stages with configurable role weights (role_weight_configurations)",
        "Explicit stage_status: COMPLETED, PENDING, NOT_STARTED, NOT_APPLICABLE",
        "Missing stages excluded & remaining weights renormalized proportionally",
        "SHA-256 input_fingerprint prevents duplicate evaluations",
    ]),
    ("Day 52: Final Recommendation & Human Review", [
        "Classifies SELECTED, HOLD_REVIEW, or REJECTED via role thresholds",
        "Mandatory Eligibility Override: ELIGIBILITY REJECTED overrides high scores",
        "Confidence = Coverage (50%) + Evidence Quality (30%) + Consistency (20%)",
        "Recruiter APPROVAL / OVERRIDE / REJECTION logged in recommendation_decision_history",
    ]),
    ("Day 53 & 54: Reports & Threshold Optimization", [
        "Day 53: 14-section Hiring Intelligence Reports in JSON, HTML, Markdown, and PDF 1.4",
        "Day 54: Synthetic validation dataset (12 cases) confusion matrix, Precision/Recall/F1",
        "Measured benchmark: 91.7% accuracy at selected_min=80.0 (synthetic data only)",
    ]),
    ("Day 55 & 61: Security, RBAC & Observability", [
        "PBKDF2-SHA256 auth, HTTP-only cookies, 4 RBAC roles, tenant_id isolation (403)",
        "SHA-256 hash-chained audit_events with tamper detection (/api/v1/audit/verify)",
        "Day 61: Live P50/P95 latency, error rate, and alert evaluation (/api/v1/monitoring/*)",
    ]),
    ("Live Demo Sequence & Roadmap", [
        "Demo: Login -> Openings/ATS -> Cross-Round -> Recommendation -> PDF Report -> Governance",
        "Short-Term Roadmap: Candidate-facing screening/coaching UI & async batch workers",
        "Medium/Long-Term: PostgreSQL pooling, Redis cache, micro-VM code sandbox",
    ]),
]

CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
  <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
  {slide_overrides}
</Types>"""

ROOT_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
</Relationships>"""

PRESENTATION_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>
  <p:sldIdLst>{sld_ids}</p:sldIdLst>
  <p:sldSz cx="12192000" cy="6858000"/>
  <p:notesSz cx="6858000" cy="9144000"/>
</p:presentation>"""

PRES_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>
  {slide_rels}
</Relationships>"""

SLIDE_MASTER = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/></p:spTree></p:cSld>
  <p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>
  <p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst>
</p:sldMaster>"""

SLIDE_MASTER_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
</Relationships>"""

SLIDE_LAYOUT = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank">
  <p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/></p:spTree></p:cSld>
</p:sldLayout>"""

SLIDE_LAYOUT_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>"""

THEME_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="ZecPath">
  <a:themeElements>
    <a:clrScheme name="ZecPath">
      <a:dk1><a:srgbClr val="102A43"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1>
      <a:dk2><a:srgbClr val="334E68"/></a:dk2><a:lt2><a:srgbClr val="F3F6F9"/></a:lt2>
      <a:accent1><a:srgbClr val="176B87"/></a:accent1><a:accent2><a:srgbClr val="0F766E"/></a:accent2>
      <a:accent3><a:srgbClr val="D99000"/></a:accent3><a:accent4><a:srgbClr val="52677B"/></a:accent4>
      <a:accent5><a:srgbClr val="176B3A"/></a:accent5><a:accent6><a:srgbClr val="A4262C"/></a:accent6>
      <a:hlink><a:srgbClr val="176B87"/></a:hlink><a:folHlink><a:srgbClr val="52677B"/></a:folHlink>
    </a:clrScheme>
    <a:fontScheme name="ZecPath">
      <a:majorFont><a:latin typeface="Calibri"/><a:ea typeface=""/><a:cs typeface=""/></a:majorFont>
      <a:minorFont><a:latin typeface="Calibri"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont>
    </a:fontScheme>
    <a:fmtScheme name="ZecPath"><a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst><a:lnStyleLst><a:ln w="9525"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst><a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst><a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst></a:fmtScheme>
  </a:themeElements>
</a:theme>"""

SLIDE_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
</Relationships>"""


def _build_slide_xml(title: str, bullets: list[str], slide_no: int) -> str:
    bullet_paras = "\n".join(
        f"""<a:p><a:pPr marL="342900" indent="-228600"><a:buChar char="&#x2022;"/></a:pPr><a:r><a:rPr lang="en-US" sz="2000" dirty="0"><a:solidFill><a:srgbClr val="172433"/></a:solidFill></a:rPr><a:t>{html.escape(b)}</a:t></a:r></a:p>"""
        for b in bullets
    )
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:bg><p:bgPr><a:solidFill><a:srgbClr val="F8FAFC"/></a:solidFill><a:effectLst/></p:bgPr></p:bg>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr/>
      <p:sp>
        <p:nvSpPr><p:cNvPr id="2" name="HeaderBar"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="12192000" cy="1150000"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:solidFill><a:srgbClr val="102A43"/></a:solidFill></p:spPr>
        <p:txBody><a:bodyPr anchor="ctr" lIns="548640"/><a:lstStyle/><a:p><a:r><a:rPr lang="en-US" sz="3200" b="1" dirty="0"><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill></a:rPr><a:t>{html.escape(title)}</a:t></a:r></a:p></p:txBody>
      </p:sp>
      <p:sp>
        <p:nvSpPr><p:cNvPr id="3" name="BodyBox"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:spPr><a:xfrm><a:off x="685800" y="1500000"/><a:ext cx="10820400" cy="4600000"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>
        <p:txBody><a:bodyPr wrap="square"/><a:lstStyle/>{bullet_paras}</p:txBody>
      </p:sp>
      <p:sp>
        <p:nvSpPr><p:cNvPr id="4" name="Footer"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:spPr><a:xfrm><a:off x="685800" y="6300000"/><a:ext cx="10820400" cy="360000"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>
        <p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:r><a:rPr lang="en-US" sz="1200" dirty="0"><a:solidFill><a:srgbClr val="64748B"/></a:solidFill></a:rPr><a:t>ZecPath AI Hiring System | Slide {slide_no} of {len(SLIDES)}</a:t></a:r></a:p></p:txBody>
      </p:sp>
    </p:spTree>
  </p:cSld>
</p:sld>"""


def build_pptx() -> None:
    OUT_PPTX.parent.mkdir(parents=True, exist_ok=True)
    slide_overrides = "\n  ".join(
        f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        for i in range(1, len(SLIDES) + 1)
    )
    sld_ids = "".join(f'<p:sldId id="{255 + i}" r:id="rId{i + 2}"/>' for i in range(1, len(SLIDES) + 1))
    slide_rels = "\n  ".join(
        f'<Relationship Id="rId{i + 2}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>'
        for i in range(1, len(SLIDES) + 1)
    )

    with zipfile.ZipFile(OUT_PPTX, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", CONTENT_TYPES.format(slide_overrides=slide_overrides))
        zf.writestr("_rels/.rels", ROOT_RELS)
        zf.writestr("ppt/presentation.xml", PRESENTATION_XML.format(sld_ids=sld_ids))
        zf.writestr("ppt/_rels/presentation.xml.rels", PRES_RELS.format(slide_rels=slide_rels))
        zf.writestr("ppt/slideMasters/slideMaster1.xml", SLIDE_MASTER)
        zf.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", SLIDE_MASTER_RELS)
        zf.writestr("ppt/slideLayouts/slideLayout1.xml", SLIDE_LAYOUT)
        zf.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", SLIDE_LAYOUT_RELS)
        zf.writestr("ppt/theme/theme1.xml", THEME_XML)
        for idx, (title, bullets) in enumerate(SLIDES, start=1):
            zf.writestr(f"ppt/slides/slide{idx}.xml", _build_slide_xml(title, bullets, idx))
            zf.writestr(f"ppt/slides/_rels/slide{idx}.xml.rels", SLIDE_RELS)
    print(f"Generated {OUT_PPTX} ({len(SLIDES)} slides, {OUT_PPTX.stat().st_size} bytes)")


if __name__ == "__main__":
    build_pptx()
