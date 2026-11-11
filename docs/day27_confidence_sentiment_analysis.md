# Day 27 — Confidence and Sentiment Signal Analysis

## 1. Overview
Day 27 implements non-verbal and verbal behavioral signal detection to assist recruiters in evaluating communication effectiveness, candidate hesitation, and statement consistency.

## 2. Signal Dimensions
1. **Confidence & Hesitation:**
   - **Hesitation Markers:** Frequency of filler sounds and hesitation tokens (`um`, `uh`, `er`, `ah`, `you know`, `i mean`).
   - **Uncertainty Phrases:** Identification of speculative qualifiers (`i think`, `i guess`, `maybe`, `not sure`, `perhaps`).
   - **Pacing Metrics:** Words per minute (WPM) calculation categorized into `FAST` (>160 WPM), `NORMAL` (80–160 WPM), and `SLOW` (<80 WPM).
   - **Response Length:** Evaluated into `SHORT` (<10 words), `MEDIUM` (10–50 words), and `LONG` (>50 words).
2. **Sentiment Analysis:**
   - Lexical sentiment polarity analysis (`POSITIVE`, `NEUTRAL`, `NEGATIVE`) with normalized score (-1.0 to +1.0).
3. **Contradiction Detection:**
   - Compares current answers against historical facts supplied during the screening session (e.g. earlier stating 5 years experience, later stating 2 years).

## 3. SafeRecruiting Ethical Safeguards
- Behavioral and sentiment signals are strictly designated as **supplementary indicators**, not automated rejection criteria.
- Neurodivergent speech patterns, regional communication variations, and non-native accents are protected by ensuring that low confidence or hesitation triggers polite clarification rather than automatic disqualification.
- Persisted in the `behavioral_analysis` database table.

