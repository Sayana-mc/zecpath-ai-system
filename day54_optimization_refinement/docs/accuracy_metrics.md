

\# Day 54 — Accuracy Metrics



\## Confusion matrix

\- True positive: predicted suitable and labelled suitable.

\- False positive: predicted suitable but labelled not suitable.

\- True negative: predicted not suitable and labelled not suitable.

\- False negative: predicted not suitable but labelled suitable.



\## Metrics

\- Accuracy = (TP + TN) / (TP + TN + FP + FN)

\- Precision = TP / (TP + FP)

\- Recall = TP / (TP + FN)

\- Specificity = TN / (TN + FP)

\- F1 = 2 \* Precision \* Recall / (Precision + Recall)



A metric is set to zero if its denominator is zero.



\## Evaluation method

1\. Load labelled examples.

2\. Evaluate a range of thresholds.

3\. Calculate the confusion matrix at each threshold.

4\. Compare precision, recall and F1.

5\. Inspect the identities and evidence for errors.

6\. Validate the selected approach on a separate representative dataset.



\## Dataset warning

The supplied examples are synthetic. The calculated metrics demonstrate the evaluation method and are not real-world hiring accuracy estimates. A small sample can produce unstable results.



