# Day 20 – ATS Scoring Methodology & Formula Specification

## 1. Multi-Factor Scoring Formula

The ZecPath ATS Score evaluates a candidate against a specific Job Opening across four orthogonal, explainable dimensions:

$$\text{Final ATS Score} = (w_{\text{skill}} \times S_{\text{skill}}) + (w_{\text{sem}} \times S_{\text{sem}}) + (w_{\text{exp}} \times S_{\text{exp}}) + (w_{\text{edu}} \times S_{\text{edu}})$$

Subject to:

$$\sum_{i} w_i = 1.0 \quad \text{and} \quad 0.0 \le S_i \le 100.0 \quad \forall i$$

---

## 2. Component Definitions

### A. Skills Match Score ($S_{\text{skill}}$)
- **Weight:** $40\%$ ($w_{\text{skill}} = 0.40$ for Python Developer / Technical Roles).
- **Calculation:** Compares candidate skills (reported + extracted from resume) against opening requirements:
  - Required Skills carry $80\%$ of the component score.
  - Preferred Skills carry $20\%$ of the component score.
- **Formula:**
  $$S_{\text{skill}} = \left(0.80 \times \frac{|\text{Matched Required}|}{|\text{Total Required}|} \times 100\right) + \left(0.20 \times \frac{|\text{Matched Preferred}|}{|\text{Total Preferred}|} \times 100\right)$$

### B. Semantic Similarity Score ($S_{\text{sem}}$)
- **Weight:** $25\% - 30\%$ ($w_{\text{sem}} = 0.30$ for Python Developer).
- **Calculation:** Encodes de-identified candidate resume text and structured job description using SentenceTransformers `all-MiniLM-L6-v2`.
- **Formula:**
  $$S_{\text{sem}} = \max\left(0.0, \, \min\left(100.0, \, \frac{\vec{u} \cdot \vec{v}}{\|\vec{u}\|_2 \|\vec{v}\|_2} \times 100\right)\right)$$

### C. Experience Relevance Score ($S_{\text{exp}}$)
- **Weight:** $20\%$ ($w_{\text{exp}} = 0.20$).
- **Calculation:** Ratio between candidate verified years of experience and minimum required experience:
  $$S_{\text{exp}} = \min\left(100.0, \, \frac{\text{Years Found}}{\text{Minimum Years Required}} \times 100\right)$$
  *(If no minimum experience is specified by the job, $S_{\text{exp}} = 100.0$)*.

### D. Education Alignment Score ($S_{\text{edu}}$)
- **Weight:** $10\% - 15\%$ ($w_{\text{edu}} = 0.10$ for Python Developer).
- **Calculation:** Hierarchical degree tier mapping:
  - $\text{High School} \to \text{Associate} \to \text{Bachelor} \to \text{Master} \to \text{Doctorate}$.
  - Candidate with degree tier $\ge$ job requirement receives $100.0\%$. Partial credit ($50\% - 75\%$) awarded for adjacent tiers.

---

## 3. Score Categorization Bands

Once computed, scores are categorized into qualitative review bands:

| Band | Score Range | Action Required |
|---|---|---|
| **EXCELLENT** | $80.0\% - 100.0\%$ | Strongly recommended for immediate technical shortlisting. |
| **GOOD** | $65.0\% - 79.9\%$ | Recommended for recruiter review and eligibility screening. |
| **MODERATE** | $50.0\% - 64.9\%$ | Borderline match; requires recruiter manual review of skill gaps. |
| **LOW** | $0.0\% - 49.9\%$ | Significant mismatch; flag for secondary review or archival. |

---

## 4. Human-in-the-Loop Decision Guardrail

Under no circumstances does an ATS score autonomously trigger employment offers or automated candidate rejections. The system serves strictly as **decision support**:
- Every score is accompanied by itemized evidence (matched skills, missing skills, raw cosine similarity).
- Final hiring decisions require human recruiter confirmation and audit logging.

