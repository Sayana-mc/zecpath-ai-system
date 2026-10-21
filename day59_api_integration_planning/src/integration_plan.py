import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def load_config():
    return json.loads((ROOT/"config"/"integration_config.json").read_text(encoding="utf-8"))

def validate_config(c):
    if c.get("human_review_required") is not True: raise ValueError("Human review must remain required")
    if c.get("automatic_rejection_enabled") is not False: raise ValueError("Automatic rejection must remain disabled")
    if c.get("resume_processing",{}).get("mode") != "async": raise ValueError("Resume processing must be async")
    if c.get("interview_scoring",{}).get("mode") != "sync": raise ValueError("Interview scoring must be sync")
    if c.get("security",{}).get("tls_required") is not True: raise ValueError("TLS must be required")

def build_plan():
    c=load_config(); validate_config(c)
    return {
      "project":c["project"],"version":c["version"],
      "services":[
       {"name":"Resume Parsing API","method":"POST","path":"/v1/resume-jobs","mode":"async","success_status":202},
       {"name":"ATS Scoring API","method":"POST","path":"/v1/ats/score","mode":"sync","success_status":200},
       {"name":"Screening AI API","method":"POST","path":"/v1/screening/evaluate","mode":"sync","success_status":200},
       {"name":"Interview AI API","method":"POST","path":"/v1/interviews/score","mode":"sync","success_status":200,"timeout_seconds":c["interview_scoring"]["timeout_seconds"]},
       {"name":"Decision AI API","method":"POST","path":"/v1/decisions/recommend","mode":"sync","success_status":200}],
      "retry_policy":c["retry_policy"],"security":c["security"],
      "human_review_required":True,"automatic_rejection_enabled":False}

def write_outputs(plan):
    out=ROOT/"output"; out.mkdir(exist_ok=True)
    (out/"integration_plan.json").write_text(json.dumps(plan,indent=2),encoding="utf-8")
    lines=["# Day 59 — AI Integration Plan","",f"Project: {plan['project']}","",
      "| Service | Method | Endpoint | Mode | Success |","|---|---|---|---|---|"]
    for s in plan["services"]: lines.append(f"| {s['name']} | {s['method']} | `{s['path']}` | {s['mode']} | {s['success_status']} |")
    lines += ["","## Safeguards","- Human review required: Yes","- Automatic rejection: Disabled","",
      "## Retry policy","```json",json.dumps(plan["retry_policy"],indent=2),"```",
      "","Planning prototype only; no live AI API or production database is connected."]
    (out/"integration_plan.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
