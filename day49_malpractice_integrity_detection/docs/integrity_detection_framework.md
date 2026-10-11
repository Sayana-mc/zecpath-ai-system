

\# Day 49 – Integrity Detection Framework



\## Objective

Design a system that identifies interview events requiring integrity review.



\## Signals

\- Tab-switch frequency

\- Loss of interview-window focus

\- Supplied external-audio event counts

\- Repeated looking-away events



\## Processing flow

Event Collection

&#x20;   -> Consent and Input Validation

&#x20;   -> Threshold Comparison

&#x20;   -> Pattern Analysis

&#x20;   -> Risk Tags and Warnings

&#x20;   -> Human Review



\## Detection methods

1\. Threshold-based flags for individual event categories.

2\. Pattern-based review when multiple categories exceed thresholds.

3\. Explainable records containing counts, thresholds, tags, and messages.

4\. Integration with Day 48 as optional descriptive context.



\## Limitations

The prototype consumes supplied event counts. It does not implement

real-time tab tracking, microphone-based external-voice detection,

or camera-based gaze detection.



An event flag is not proof of cheating. Human review and a fair

opportunity for the candidate to explain are required.



