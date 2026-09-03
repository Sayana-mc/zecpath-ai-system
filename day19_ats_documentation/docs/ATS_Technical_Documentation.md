\# ATS Technical Documentation



\## 1. Project Overview



The Zecpath ATS (Applicant Tracking System) is an AI-powered resume screening and candidate evaluation system.



The system is designed to automate important parts of the recruitment workflow, including resume processing, text extraction, candidate analysis, ATS scoring, candidate ranking, decision generation, testing, optimization, and documentation.



The system was developed incrementally across multiple development days.



The major development stages included:



\- Resume text extraction

\- Resume preprocessing

\- Resume section normalization

\- Candidate-job matching

\- ATS scoring

\- Candidate ranking

\- AI decision generation

\- ATS system testing

\- Performance optimization

\- Noisy resume handling

\- Entity detection optimization

\- Documentation and knowledge transfer





\## 2. Objectives



The main objectives of the ATS are:



1\. Extract useful information from resumes.

2\. Normalize resume text for reliable processing.

3\. Identify important candidate information.

4\. Compare candidate profiles with job requirements.

5\. Generate ATS scores.

6\. Rank candidates according to their scores.

7\. Generate recruitment decisions.

8\. Test AI decisions against manual review.

9\. Improve processing performance.

10\. Handle noisy and inconsistent resume text.

11\. Provide maintainable technical documentation.





\## 3. System Workflow



The overall ATS workflow can be represented as:



Resume

&#x20;   ↓

Resume Text Extraction

&#x20;   ↓

Text Cleaning and Normalization

&#x20;   ↓

Resume Section Detection

&#x20;   ↓

Entity / Skill Detection

&#x20;   ↓

Candidate Profile Processing

&#x20;   ↓

Job Requirement Processing

&#x20;   ↓

Candidate-Job Matching

&#x20;   ↓

ATS Score Calculation

&#x20;   ↓

Candidate Ranking

&#x20;   ↓

AI Decision

&#x20;   ↓

Testing and Validation

&#x20;   ↓

Performance Optimization





\## 4. Major Components



\### 4.1 Resume Extraction



The resume extraction stage converts uploaded resume files into machine-readable text.



The system processes resume content before sending it to later stages.



The extraction pipeline focuses on:



\- Text extraction

\- Whitespace normalization

\- Bullet normalization

\- Text cleaning

\- Handling unnecessary formatting

\- Preparing text for downstream processing





\### 4.2 Resume Normalization



Resume text may contain:



\- Multiple spaces

\- Different bullet characters

\- Unnecessary line breaks

\- OCR-related character errors

\- Special characters

\- Inconsistent capitalization



The optimization stage introduced text normalization to improve downstream processing.



Example:



Original:



Pyth0n     Developer!!!

Skilled in SQL!!!

P0WER BI



Normalized:



Python Developer! Skilled in SQL! Power BI





\### 4.3 Entity Detection



The ATS identifies important entities from resume text.



Examples include:



\- Skills

\- Years of experience

\- Technologies

\- Job-related keywords



The Day 18 optimization included efficient skill detection and experience detection.



Example:



Input:



Data Analyst with 3 years of experience.



Detected experience:



3 years





\### 4.4 Candidate Matching



Candidate information is compared with job requirements.



Relevant factors include:



\- Required skills

\- Candidate skills

\- Experience

\- Job role

\- Resume content

\- Profile relevance





\### 4.5 ATS Scoring



The candidate receives an ATS score based on the matching process.



The score is then used to support candidate ranking and decision generation.





\### 4.6 Candidate Ranking



Candidates are ranked according to their final ATS scores.



The ranking output contains information such as:



\- Candidate name

\- ATS score

\- Decision

\- Rank

\- Job ID

\- Job title





\### 4.7 AI Decision



The ATS produces recruitment decisions.



The supported decisions used during testing were:



\- SHORTLISTED

\- REVIEW

\- REJECTED





\### 4.8 ATS Testing



Day 17 introduced systematic testing of the ATS.



AI decisions were compared against manually reviewed decisions.



Testing covered:



\- Tech profiles

\- Non-tech profiles

\- Fresher profiles

\- Senior profiles



The system was evaluated using:



\- Accuracy

\- Precision

\- Recall

\- F1 score

\- Confusion matrix

\- Mismatch cases





\## 5. Day 17 Testing Results



The ATS was tested using 55 candidate-job test cases.



Results:



\- Total test cases: 55

\- Accuracy: 94.55%

\- Precision: 100%

\- Recall: 57.14%

\- F1 Score: 72.73%

\- True Positives: 4

\- True Negatives: 48

\- False Positives: 0

\- False Negatives: 3

\- Mismatch Cases: 7



These results showed that the ATS generated no false-positive shortlist decisions in the tested dataset, while several manually shortlisted candidates were classified differently by the AI system.





\## 6. Day 18 Optimization



Day 18 focused on improving ATS performance and stability.



The implemented optimization areas included:



\- Optimized text extraction

\- Prompt optimization

\- Resume caching

\- Entity detection optimization

\- Memory monitoring

\- Noisy resume handling

\- Performance benchmarking

\- Stability testing





\## 7. Performance Results



The optimized system was benchmarked using the performance benchmark module.



Observed results:



Text normalization time:

0.005928 seconds



Entity detection time:

0.000243 seconds



Peak memory usage:

912.57 KB



Performance checks:



\- Text normalization: PASS

\- Entity detection: PASS





\## 8. Stability Testing



The stability test suite verified important ATS behaviors.



The following tests were successfully executed:



\- Empty resume handling

\- Noisy text handling

\- Skill detection

\- Experience detection

\- Missing experience handling

\- Text normalization performance

\- Entity detection performance



Final test result:



7 passed



Example command:



python -m pytest -v tests





\## 9. Noisy Resume Handling



The ATS includes normalization logic to handle noisy resume text.



The system can correct selected common character substitutions and normalize unnecessary whitespace.



Example:



Pyth0n → Python



P0WER BI → Power BI



The purpose of this process is to improve entity detection and downstream ATS processing.





\## 10. Prompt Optimization



Prompt optimization reduces unnecessary information sent to the model.



Important resume sections are prioritized:



\- Summary

\- Skills

\- Experience

\- Education

\- Projects

\- Certifications



Excessively large text is also limited using a maximum character threshold.



This reduces unnecessary prompt content and can improve processing efficiency.





\## 11. Resume Caching



The ATS includes a resume cache mechanism.



The cache uses a SHA-256 hash of resume file content as the cache key.



If the same resume is processed repeatedly, cached information can be reused rather than unnecessarily repeating processing.



Benefits:



\- Reduced repeated processing

\- Improved efficiency

\- Reduced unnecessary computation

\- Faster repeated access





\## 12. Performance Benchmarking



The performance benchmark measures:



1\. Text normalization time

2\. Entity detection time

3\. Processing performance

4\. Memory usage



The benchmark provides measurable performance information and checks whether processing remains within predefined targets.





\## 13. Technology Stack



The project uses Python as the main development language.



Major technologies and tools used across the ATS project include:



\- Python

\- PyMuPDF

\- python-docx

\- Pandas

\- NumPy

\- Scikit-learn

\- Pytest

\- JSON

\- CSV

\- PowerShell

\- Git/GitHub

\- FastAPI

\- ChromaDB

\- Google Gemini / LLM components





\## 14. Testing Strategy



Testing is performed at multiple levels.



\### Functional Testing



Verifies that individual ATS components perform expected operations.



\### Performance Testing



Measures processing time and memory usage.



\### Stability Testing



Checks how the system behaves with:



\- Empty input

\- Noisy text

\- Missing information

\- Different candidate profiles





\### ATS Decision Testing



Compares AI decisions against manual reviewer decisions.



This helps identify:



\- False positives

\- False negatives

\- Decision mismatches

\- Role-specific weaknesses





\## 15. Known Limitations



The current ATS has some limitations.



1\. Recall is lower than precision in the Day 17 test results.

2\. Some manually shortlisted candidates were not shortlisted by the AI.

3\. Technical-role testing showed weaker performance in the tested dataset.

4\. More diverse resumes are required for broader validation.

5\. Larger datasets should be used for production-level validation.

6\. More advanced OCR handling can be added for scanned resumes.





\## 16. Future Improvements



Potential future improvements include:



\- Better decision threshold calibration

\- Improved technical-role classification

\- Better OCR support

\- Larger testing datasets

\- More advanced semantic matching

\- Improved model response-time optimization

\- Production-grade monitoring

\- Automated regression testing

\- Improved explainability of ATS decisions





\## 17. Conclusion



The ATS was developed through an incremental engineering process covering resume processing, candidate ranking, testing, optimization, and documentation.



Day 17 validated the ATS using 55 candidate-job test cases and achieved 94.55% accuracy with 100% precision.



Day 18 improved system efficiency and stability. The optimized implementation achieved fast text normalization and entity detection performance while successfully passing all seven automated tests.



Day 19 documents the system architecture, processing workflow, scoring logic, troubleshooting procedures, and developer instructions to make the ATS easier to maintain, understand, and extend.

