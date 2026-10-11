

\# Day 48 – Behavioral AI Research \& Design



\## 1. Objective

Design a non-invasive framework for describing observable interview-session signals.



\## 2. Signals considered

\- Eye gaze: measured gaze stability, if reliable measurement is available.

\- Head movement: movement-event frequency and stability over time.

\- Facial engagement: explicitly defined observable facial activity; not emotion or personality.

\- Attention patterns: observable off-screen events, if measured consistently.

\- Gestures: count of defined movement events, not an inferred nervousness score.



\## 3. Measurement approach

The prototype accepts normalized demo metrics between 0 and 1.

It does not capture video, detect faces, or track eyes.

Sample values are synthetic and must not be presented as real observations.



\## 4. Signal-to-score mapping

Each metric is multiplied by its configured weight.

The weighted sum is multiplied by 100 to produce a descriptive

Signal Consistency Index from 0 to 100.



\## 5. Non-invasive principles

\- Obtain informed consent.

\- Explain what is measured and why.

\- Minimize collection and retention.

\- Offer a non-camera alternative.

\- Allow reasonable accommodations.

\- Keep a human reviewer involved.

\- Do not infer honesty, personality, mental state, or job suitability.



\## 6. Limitations

Eye gaze, movement, and facial activity can vary with culture,

disability, neurodiversity, camera position, lighting, device quality,

fatigue, and personal communication style.

A low or high index does not establish candidate quality.



\## 7. Status

Research and software prototype using synthetic input.

Real-world validity, accessibility, privacy, and fairness testing remain necessary.



