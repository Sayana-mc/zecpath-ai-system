# Day 34: Dynamic Follow-Up Logic & Adaptive Questioning Engine

## 1. Overview
The Adaptive Questioning Engine dynamically evaluates the quality, completeness, and confidence of a candidate's answer in real time, determining whether a targeted follow-up question is warranted.

---

## 2. Follow-Up Decision Tree

```mermaid
flowchart TD
    A["Candidate Answer Received"] --> B{"Response Length & Patterns"}
    
    B -->|"<= 4 words or empty"| C["Quality: Incomplete"]
    B -->|"Matches Vague Phrases"| D["Quality: Vague"]
    B -->|">= 15 words & Specific"| E["Quality: Complete"]
    
    C --> F["Generate CLARIFICATION Follow-Up"]
    D --> G["Generate EXAMPLE_BASED Follow-Up"]
    E --> H{"Confidence Level"}
    
    H -->|"High Confidence"| I["Generate SCENARIO_BASED Follow-Up"]
    H -->|"Normal Confidence"| J["Generate DEEPENING Follow-Up"]
    
    F --> K["Persist in hr_interview_followups"]
    G --> K
    I --> K
    J --> K
```

---

## 3. Adaptation Strategies
- **Clarification:** Prompted when responses fail minimum substance thresholds (e.g. "Could you elaborate on that and explain what steps you took?").
- **Example-Based:** Prompted when candidates make general claims without concrete evidence (e.g. "Could you provide a specific example from your experience to illustrate that point?").
- **Deepening / Scenario-Based:** Prompted on comprehensive, confident responses to probe edge cases, trade-offs, and critical decision points.
- **Repetition Prevention:** Enforces a hard limit of one adaptive follow-up per parent question to keep interviews structured and time-efficient.

