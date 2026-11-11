# Day 36: Confidence & Behavioral Signals with Ethical Safeguards

## 1. Overview
The Confidence & Behavioral Signals analyzer observes textual markers of hesitation, pause frequency, uncertainty phrasing, sentiment, and cross-turn factual consistency.

---

## 2. Analyzed Indicators

### 2.1 Hesitation & Pauses
- Detects textual pauses (e.g., `...`, `--`, `[pause]`) and hesitation utterances (`uh`, `um`, `er`, `ah`).

### 2.2 Uncertainty Phrasing
- Flags hedging qualifiers that dilute professional conviction:
  `maybe`, `i guess`, `i suppose`, `not really sure`, `perhaps`, `i think so`.

### 2.3 Cross-Response Contradiction Detection
- Analyzes candidate statements across multiple interview turns to detect:
  - Quantitative tenure contradictions (e.g. "I have 5 years experience" in turn 1 vs "I have 2 years experience" in turn 4).
  - Direct negation contradictions (e.g. claiming deep Kubernetes mastery in intro vs stating they never operated clusters in technical review).

---

## 3. Strict Ethical Safeguards & Legal Disclaimers
> **Mandatory Disclaimer:** Behavioral and confidence signals reflect observable communication markers and phrasing patterns only. They do not constitute an evaluation of internal psychological stress, emotional stability, or personality traits.
> 
> Recruiter discretion and human review are required before any hiring decision is finalized.

