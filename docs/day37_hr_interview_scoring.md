# Day 37: Explainable HR Interview Scoring Engine

## 1. Score Composition & Weightings
The HR Interview scoring engine normalizes multi-dimensional candidate data onto an explainable `0–100` composite scale using configurable weights:

$$\text{Overall HR Score} = (0.40 \times \text{Relevance}) + (0.25 \times \text{Communication}) + (0.15 \times \text{Confidence}) + (0.20 \times \text{Consistency})$$

| Component | Weight | Metric Source |
| :--- | :--- | :--- |
| **Answer Relevance** | 40% | Topic alignment between question keywords and candidate answer |
| **Communication Skill** | 25% | Multi-factor fluency, grammar, vocabulary, clarity, structure, filler control |
| **Confidence & Clarity** | 15% | Pacing, lack of excessive hesitation, lack of hedge uncertainty phrases |
| **Consistency** | 20% | Cross-turn factual agreement and absence of conflicting assertions |

---

## 2. Score Classification
- **EXCELLENT (85.0 – 100.0):** Strong topical depth, articulate communication, high consistency.
- **STRONG (75.0 – 84.9):** Solid responses, minor fillers or brief vagueness, consistent facts.
- **MODERATE (60.0 – 74.9):** Requires clarification, frequent fillers, or minor contradictions.
- **DEVELOPING (< 60.0):** Incomplete responses, persistent uncertainty, material contradictions.

---

## 3. Subsystem Separation
- ATS resume scores (Day 1–15) evaluate document credentials and semantic matching.
- Screening scores (Day 24–32) evaluate preliminary candidate eligibility and basic responses.
- HR Interview scores (Day 33–40) evaluate conversational depth, communication, and reasoning.
- All three scores are persisted separately in the database and never overwritten.

