\# ATS Technical Documentation



\## AI-Powered Applicant Tracking System



Project: Zecpath AI System

Module: Applicant Tracking System (ATS)

Documentation Phase: Day 19

Purpose: Technical Documentation and Knowledge Transfer



\---



\# 1. Introduction



The Applicant Tracking System (ATS) is an AI-powered recruitment support system designed to automate resume processing, candidate information extraction, candidate-job matching, scoring, ranking, and decision generation.



The purpose of this technical documentation is to provide a structured reference for understanding the ATS architecture, processing workflow, scoring mechanism, optimization components, testing references, troubleshooting procedures, and future extension possibilities.



This documentation is intended to make the ATS maintainable, explainable, and extendable for future developers.



\---



\# 2. Objectives



The main objectives of the ATS are:



\- Process candidate resumes efficiently.

\- Extract useful candidate information.

\- Identify relevant skills and entities.

\- Detect candidate experience.

\- Compare candidate profiles with job requirements.

\- Calculate candidate-job compatibility scores.

\- Rank candidates based on their scores.

\- Generate recruitment decisions.

\- Support automated and human-assisted screening.

\- Provide a maintainable and extendable architecture.



\---



\# 3. System Overview



The ATS converts unstructured resume information into structured candidate information and evaluates the candidate against a target job.



The major processing pipeline is:



Resume Input

&#x20;   ↓

Text Extraction

&#x20;   ↓

Text Cleaning and Normalization

&#x20;   ↓

Resume Section Detection

&#x20;   ↓

Entity and Skill Detection

&#x20;   ↓

Candidate Profile

&#x20;   ↓

Job Requirement Processing

&#x20;   ↓

Candidate-Job Matching

&#x20;   ↓

ATS Scoring

&#x20;   ↓

Candidate Ranking

&#x20;   ↓

Decision Generation

&#x20;   ↓

ATS Output



\---



\# 4. Major System Components



The major components of the ATS include:



1\. Resume Input

2\. Text Extraction

3\. Text Normalization

4\. Resume Section Detection

5\. Entity Detection

6\. Skill Detection

7\. Experience Detection

8\. Candidate Profile Generation

9\. Job Requirement Processing

10\. Candidate-Job Matching

11\. ATS Scoring

12\. Candidate Ranking

13\. Decision Generation

14\. Testing

15\. Performance Optimization

16\. Caching

17\. Troubleshooting and Monitoring



\---



\# 5. Resume Processing



The resume processing stage converts the original resume document into machine-readable text.



The processing pipeline includes:



\- Resume input validation.

\- Text extraction.

\- Whitespace normalization.

\- Bullet normalization.

\- Noise reduction.

\- Section identification.

\- Entity detection.

\- Skill detection.

\- Experience detection.



The processed information is then used for candidate evaluation.



\---



\# 6. Text Normalization



Resume text can contain inconsistent spaces, special characters, formatting issues, and noisy characters.



The normalization stage improves the quality of extracted text.



The normalization process includes:



\- Removing unnecessary whitespace.

\- Normalizing bullet characters.

\- Reducing formatting inconsistencies.

\- Handling common noisy characters.

\- Preparing text for downstream processing.



Example:



Original:



Pyth0n     Developer!!!

Skilled in SQL!!!

P0WER BI



Normalized:



Python Developer! Skilled in SQL! Power BI



This improves the reliability of subsequent processing.



\---



\# 7. Resume Sections



Important resume sections used by the ATS include:



\- Summary

\- Skills

\- Experience

\- Education

\- Projects

\- Certifications



These sections contain the information most relevant to candidate-job matching.



\---



\# 8. Entity Detection



Entity detection identifies important information from resume text.



Examples include:



\- Technical skills

\- Years of experience

\- Candidate-related information

\- Other relevant profile entities



Example:



Input:



Data Analyst with 3 years of experience.



Detected experience:



3 years



Entity detection converts unstructured resume text into structured information.



\---



\# 9. Skill Detection



The ATS identifies relevant skills from candidate resumes.



Example skills include:



\- Python

\- SQL

\- Power BI

\- TensorFlow

\- Pandas

\- NumPy



Detected skills are used during candidate-job matching.



\---



\# 10. Candidate Profile



The extracted resume information is organized into a structured candidate profile.



The profile may contain:



\- Candidate information

\- Skills

\- Experience

\- Education

\- Projects

\- Certifications

\- Summary

\- Other relevant extracted entities



The structured profile is used as input to the matching and scoring stages.



\---



\# 11. Job Requirement Processing



The target job contains requirements that are used to evaluate candidates.



Relevant requirements may include:



\- Required skills

\- Preferred skills

\- Experience requirements

\- Education requirements

\- Role-specific requirements



The job requirements are compared with the candidate profile.



\---



\# 12. Candidate-Job Matching



Candidate-job matching compares the extracted candidate profile with the target job requirements.



The matching process considers:



\- Skill relevance

\- Experience relevance

\- Education relevance

\- Project relevance

\- Overall profile relevance



The matching results are used by the ATS scoring mechanism.



\---



\# 13. ATS Scoring



The ATS generates a compatibility score representing how well the candidate matches the target job.



The score is based on relevant candidate and job information.



Important matching factors include:



\- Skill matching

\- Experience matching

\- Education matching

\- Project relevance

\- Overall profile relevance



The final score is used for ranking and decision generation.



\---



\# 14. Candidate Ranking



After candidate scores are generated, candidates are ranked according to their scores.



Higher-scoring candidates receive higher rankings.



The ranking output can contain:



\- Candidate name

\- Candidate score

\- Candidate rank

\- Job information

\- AI decision



Candidate ranking helps recruiters identify stronger candidates efficiently.



\---



\# 15. Decision Generation



The ATS uses candidate evaluation results to generate a recruitment decision.



The main decision categories are:



SHORTLISTED



The candidate is considered a strong match and can proceed to the next recruitment stage.



REVIEW



The candidate requires additional human evaluation.



REJECTED



The candidate does not sufficiently match the current job requirements according to the ATS evaluation.



\---



\# 16. Testing Reference



During Day 17, the ATS was tested using candidate-job test cases and manual review results.



Total test cases:



55



Testing metrics:



Accuracy: 94.55%

Precision: 100%

Recall: 57.14%

F1 Score: 72.73%



True Positives: 4

True Negatives: 48

False Positives: 0

False Negatives: 3

Mismatch Cases: 7



The testing demonstrated high overall accuracy and precision while identifying opportunities for improving recall.



\---



\# 17. Optimization Reference



During Day 18, the ATS was optimized for performance and stability.



The optimization work included:



\- Optimized text extraction.

\- Noisy resume handling.

\- Entity detection optimization.

\- Prompt optimization.

\- Resume caching.

\- Memory monitoring.

\- Performance benchmarking.

\- Stability testing.



Benchmark results included:



Text normalization time: 0.012259 seconds

Entity detection time: 0.000347 seconds

Peak memory usage: 912.57 KB



The performance checks passed successfully.



The stability test suite completed with:



7 tests passed.



\---



\# 18. Prompt Optimization



Prompt optimization reduces unnecessary information sent to the language model.



Important resume sections are prioritized:



\- Summary

\- Skills

\- Experience

\- Education

\- Projects

\- Certifications



The optimization approach:



\- Sends relevant resume sections only.

\- Removes unnecessary content.

\- Limits excessive text.

\- Reduces prompt size.



This helps control model input size and processing requirements.



\---



\# 19. Resume Caching



A resume caching mechanism was implemented to avoid repeatedly processing the same resume.



The cache generates a SHA-256 hash from the resume file content.



The generated hash is used as the cache key.



If a resume has already been processed, cached extracted text can be reused.



This reduces unnecessary repeated processing.



\---



\# 20. Maintainability



The ATS follows a modular approach.



Important modules include:



\- optimized\_extractor

\- noisy\_resume\_handler

\- entity\_optimizer

\- memory\_monitor

\- prompt\_optimizer

\- resume\_cache

\- performance\_benchmark



A modular structure allows developers to modify or replace individual components without redesigning the complete system.



\---



\# 21. Extensibility



The ATS can be extended in future development.



Possible extensions include:



\- Additional resume formats.

\- Improved OCR support.

\- Additional entity types.

\- Improved skill matching.

\- Advanced scoring models.

\- Additional job categories.

\- Explainable AI features.

\- Larger performance test datasets.

\- Additional automated tests.

\- Recruitment platform integration.



\---



\# 22. Troubleshooting Reference



Common development issues include:



ModuleNotFoundError:

No module named 'src'



This can occur when a module is executed from an incorrect context.



Recommended command:



python -m src.performance\_benchmark



Test directory errors can occur when pytest is executed outside the correct project directory.



Recommended command:



python -m pytest -v tests



The project structure can be checked using:



Get-ChildItem -Recurse



\---



\# 23. Developer Execution



The virtual environment should be activated before development.



Example:



..\\.venv\\Scripts\\Activate.ps1



Python modules should preferably be executed using module syntax:



python -m src.module\_name



Tests can be executed using:



python -m pytest -v tests



\---



\# 24. Knowledge Transfer



The documentation provides future developers with information about:



\- ATS architecture.

\- Resume processing.

\- Text normalization.

\- Entity detection.

\- Candidate-job matching.

\- Scoring.

\- Ranking.

\- Decision generation.

\- Testing.

\- Optimization.

\- Troubleshooting.

\- Maintenance.

\- Future extension.



This reduces dependency on the original developer and supports future maintenance.



\---



\# 25. Conclusion



Day 19 completed the technical documentation and knowledge-transfer phase of the ATS project.



The system architecture, data flow, candidate processing, scoring logic, troubleshooting procedures, developer instructions, and extension guidelines were documented.



The documentation provides a structured reference for developers to understand, maintain, debug, and extend the ATS system.



The Day 19 documentation therefore improves the maintainability, explainability, and long-term extensibility of the AI-powered Applicant Tracking System.

