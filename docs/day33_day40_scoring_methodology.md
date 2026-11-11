# Days 33–40: AI HR Interview Scoring Methodology

## 1. Principles of Explainable HR Scoring
1. **Explainability Over Black-Box Numbers:** Every candidate score can be broken down into concrete evidence and sub-scores.
2. **Fairness & Bias Reduction:** Language structure and communication clarity are prioritized without penalizing dialect or regional syntax variants.
3. **Transparent Weighting:** Composite scoring strictly follows documented linear weights normalizing between `0.0` and `100.0`.
4. **Subsystem Isolation:** HR Interview scores do not distort or overwrite ATS resume credentials or Voice Screening results.

---

## 2. Mathematical Formulation

$$\text{Overall HR Score} = w_{\text{rel}} \cdot S_{\text{rel}} + w_{\text{comm}} \cdot S_{\text{comm}} + w_{\text{conf}} \cdot S_{\text{conf}} + w_{\text{cons}} \cdot S_{\text{cons}}$$

Where default weights are:
- $w_{\text{rel}} = 0.40$ (Answer Relevance)
- $w_{\text{comm}} = 0.25$ (Communication Skills)
- $w_{\text{conf}} = 0.15$ (Confidence & Composure)
- $w_{\text{cons}} = 0.20$ (Factual Consistency Across Turns)

---

## 3. Communication Component Breakdown
The communication score $S_{\text{comm}}$ represents an average of 6 evaluated metrics:
- **Fluency:** Sentence completion, flow, and absence of staccato fragmenting.
- **Grammar:** Basic syntactic coherence, capitalization, punctuation boundaries.
- **Vocabulary:** Lexical diversity (type-token ratio) and professional technical vocabulary.
- **Clarity:** Directness of expression without run-on ambiguity.
- **Structure:** Use of sequential discourse markers (`firstly`, `secondly`, `consequently`, `because`).
- **Filler Control:** Penalizes high ratios of verbal fillers (`um`, `uh`, `like`, `you know`, `basically`).

---

## 4. Contradiction & Penalty Logic
- Contradictory statements detected across interview turns apply a strict $-20.0$ penalty on consistency and flag the dossier with a `REVIEW_FLAG`.
- Low confidence or excessive hesitation flags require manual recruiter review before advancement.

