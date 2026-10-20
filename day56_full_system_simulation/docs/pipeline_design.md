# Day 56 — Pipeline Design

The local simulation validates seven stages: resume intake, ATS keyword scoring, screening, HR interview, technical interview, machine test, and final advisory recommendation.

Stage weights: ATS 20%, screening 15%, HR interview 20%, technical interview 30%, machine test 15%. Weights must sum to 100%; all scores must be within 0–100.

The ATS stage measures required-skill keyword coverage in synthetic resume text. Screening and interview scores are pre-labelled synthetic inputs. The final score is mapped to an advisory category, and human review remains mandatory.

The simulation compares AI advisory output with a supplied human judgment label, flags score gaps above 15 points, flags label mismatches, and detects strong ATS keyword coverage paired with low interview/test scores.

A comparison label of REJECTED is used only to compare against the supplied human label. It does not trigger automatic rejection.
