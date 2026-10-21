"""Run the Day 58 proposal validation and generate local outputs."""
import json
import sys
from pathlib import Path

from .coaching import build_coaching_plan
from .feature_registry import list_features
from .reporting import atomic_write_json, build_proposal_report, write_markdown
from .roadmap import validate_roadmap

ROOT = Path(__file__).resolve().parents[1]


def load_json(path):
    try:
        with path.open("r", encoding="utf-8") as stream:
            return json.load(stream)
    except FileNotFoundError as exc:
        raise RuntimeError(f"Required input file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON in {path} at line {exc.lineno}, column {exc.colno}") from exc


def main():
    try:
        roadmap = validate_roadmap(load_json(ROOT / "config" / "roadmap_config.json"))
        candidate = load_json(ROOT / "data" / "sample_candidate.json")
        features = list_features()
        coaching = build_coaching_plan(candidate)
        report = build_proposal_report(roadmap, features, coaching)
        out = ROOT / "output"
        atomic_write_json(out / "innovation_proposal.json", report)
        write_markdown(out / "ai_roadmap_and_innovation_proposal.md", report)
        atomic_write_json(out / "candidate_coaching_preview.json", coaching)
        print("DAY 58 — ADVANCED FEATURE PROPOSAL")
        print(f"Roadmap phases: {report['roadmap_phase_count']}")
        print(f"Features registered: {report['feature_count']}")
        print(f"Coaching suggestions: {len(coaching['skills_to_practice'])}")
        print(f"Human review required: {report['principles']['human_review_required']}")
        print(f"Automatic rejection enabled: {report['principles']['automatic_rejection_enabled']}")
        print(f"Emotion inference for hiring enabled: {report['principles']['emotion_inference_for_hiring_enabled']}")
        print(f"Reports generated: {out}")
        return 0
    except (RuntimeError, ValueError, OSError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
