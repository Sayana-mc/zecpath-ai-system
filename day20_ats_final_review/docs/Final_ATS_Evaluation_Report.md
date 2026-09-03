DAY 19 – ATS DOCUMENTATION \& KNOWLEDGE TRANSFER 

ZecPath – AI-Powered Resume Screening and Hiring Assistant 

Prepared By: Sayana M C 

Date: 30 August 2026 

&#x20;

1\. Introduction 

Day 19 of the Zecpath AI System project focused on ATS Documentation and Knowledge Transfer. The 

objective of this phase was to make the Applicant Tracking System maintainable, explainable, and 

extendable by documenting its architecture, data flow, scoring logic, development procedures, and 

troubleshooting methods. 

The documentation consolidates the work completed during the previous ATS development, testing, 

and optimization stages into a structured technical reference. It explains how resumes are processed, 

how candidate information is extracted, how skills and experience are detected, how candidates are 

matched with job requirements, how ATS scores and decisions are generated, and how the system can 

be maintained and extended. 

The Day 19 work also included preparing architecture and data-flow documentation, scoring 

documentation, developer guidance, and troubleshooting notes. These resources provide future 

developers with a clear understanding of the system and reduce dependency on the original 

implementation process. 

&#x20;

2\. Objective 

The main objective of Day 19 was to create complete technical documentation and knowledge-transfer 

material for the ATS. 

The objectives were: 

• Document the overall ATS architecture. 

• Document the ATS data flow. 

• Explain resume processing. 

• Document candidate information extraction. 

• Explain skill and entity detection. 

• Document candidate scoring logic. 

• Explain candidate ranking and decision generation. 

• Prepare developer instructions. 

• Prepare troubleshooting documentation. 

• Make the system easier to maintain. 

• Make future modifications and extensions easier. 

• Consolidate knowledge from previous development stages. 

3\. Day 19 Tasks Completed 

The following tasks were completed: 

1\. Created documentation project structure. 

2\. Created technical documentation. 

3\. Created developer guide. 

4\. Created scoring logic documentation. 

5\. Created architecture documentation. 

6\. Created data-flow documentation. 

7\. Created troubleshooting documentation. 

8\. Reviewed Day 17 ATS testing results. 

9\. Reviewed Day 18 optimization and performance results. 

10\. Organized the documentation for knowledge transfer. 

11\. Prepared the final documentation structure for submission. 

&#x20;

4\. Project Directory Creation 

A separate Day 19 documentation project was created. 

The project directory used was: 

C:\\Users\\sayan\\Documents\\zecpath-ai-system\\day19\_ats\_documentation 

The following directories were created: 

docs 

diagrams 

developer\_guide 

New-Item -ItemType Directory -Force docs 

New-Item -ItemType Directory -Force diagrams 

New-Item -ItemType Directory -Force developer\_guide 

Figure 1: Creation of the Day 19 documentation project directories 

5\. Documentation Project Structure 

The documentation project was organized into separate sections according to their purpose. 

The final structure was: 

day19\_ats\_documentation/ 

│ 

├── docs/ 

│   ├── ATS\_Technical\_Documentation.md 

│   └── ATS\_Developer\_Guide.md 

│ 

├── diagrams/ 

│   ├── ATS\_Architecture.txt 

│   └── ATS\_Data\_Flow.txt 

│ 

├── scoring/ 

│   └── Scoring\_Logic.md 

│ 

├── troubleshooting/ 

│   ├── TROUBLESHOOTING.md 

│   └── Troubleshooting\_Notes.md 

│ 

├── developer\_guide/ 

│   └── Developer\_Guide.md 

│ 

└── screenshots/ 

The directory structure separates technical documentation, architecture information, scoring logic, 

troubleshooting information, and developer guidance. 

Get-ChildItem -Recurse 

&#x20;

Figure 2: Final Day 19 documentation project structure 

6\. Technical Documentation 

The main technical documentation file created was: 

docs\\ATS\_Technical\_Documentation.md 

The file documents: 

• ATS overview 

• System architecture 

• Resume processing 

• Data flow 

• Candidate profile extraction 

• Skill detection 

• Experience detection 

• Candidate-job matching 

• ATS scoring 

• Candidate ranking 

• Decision generation 

• Testing references 

• Optimization references 

• Maintainability 

• Extensibility 

notepad docs\\ATS\_Technical\_Documentation.md 

&#x20;

Figure 3: ATS technical documentation containing system overview and technical workflow 

&#x20;

7\. ATS Architecture Documentation 

The architecture documentation was created in: 

diagrams\\ATS\_Architecture.txt 

The architecture describes the major ATS components and their relationships. 

The major components include: 

Resume Input 

↓ 

Text Extraction 

↓ 

Text Cleaning / Normalization 

↓ 

Section Detection 

↓ 

Entity / Skill Detection 

↓ 

Candidate Profile 

↓ 

Job Requirement Processing 

↓ 

Candidate-Job Matching 

↓ 

ATS Scoring 

↓ 

Candidate Ranking 

↓ 

Decision Generation 

↓ 

ATS Output 

&#x20;

&#x20;

&#x20;

&#x20;

notepad diagrams\\ATS\_Architecture.txt 

&#x20;

Figure 4: High-level architecture of the AI-powered ATS 

&#x20;

8\. ATS Data Flow Documentation 

The ATS data flow was documented in: 

diagrams\\ATS\_Data\_Flow.txt 

The documented data flow is: 

Candidate Resume 

↓ 

Resume Text 

↓ 

Cleaned Text 

↓ 

Resume Sections 

↓ 

Extracted Entities 

↓ 

Candidate Profile 

↓ 

Job Requirements 

↓ 

Matching Process 

↓ 

ATS Score 

↓ 

Candidate Ranking 

↓ 

AI Decision 

↓ 

Final ATS Output 

notepad diagrams\\ATS\_Data\_Flow.txt 

&#x20;

Figure 5: ATS data-flow documentation 

&#x20;

9\. Scoring Logic Documentation 

The scoring logic was documented in: 

scoring\\Scoring\_Logic.md 

The documentation explains how candidate information is considered during ATS evaluation. 

The major evaluation factors include: 

• Skill relevance 

• Experience relevance 

• Education relevance 

• Project relevance 

• Overall candidate-job relevance 

The resulting ATS score is used to rank candidates and support the final decision. 

The three main ATS decisions are: 

SHORTLISTED 

The candidate is considered a strong match for the job. 

REVIEW 

The candidate requires additional human evaluation. 

REJECTED 

The candidate does not sufficiently match the job requirements according to the ATS evaluation. 

notepad scoring\\Scoring\_Logic.md 

Figure 6: ATS candidate scoring and decision logic documentation 

&#x20;

10\. Developer Guide 

The developer guide was created to provide future developers with instructions for working with the 

ATS. 

The main developer guide is: 

developer\_guide\\Developer\_Guide.md 

The developer guide contains information about: 

• Project structure 

• Environment setup 

• Running the system 

• Running tests 

• Important modules 

• Maintenance 

• Troubleshooting 

• Extension guidelines 

notepad developer\_guide\\Developer\_Guide.md 

&#x20;

Figure 7: ATS developer guide for system maintenance and future development 

&#x20;

11\. Troubleshooting Documentation 

Troubleshooting documentation was created to record common problems encountered during ATS 

development and their solutions. 

The documentation includes problems such as: 

ModuleNotFoundError 

Example: 

ModuleNotFoundError: No module named 'src' 

The recommended solution is to execute modules from the correct project root using: 

python -m src.module\_name 

For example: 

python -m src.performance\_benchmark 

Missing Test Directory 

Example: 

ERROR: file or directory not found: tests 

The solution is to navigate to the correct project directory before executing: 

python -m pytest -v tests 

Missing Source File 

Example: 

can't open file 'src\\noisy\_resume\_handler.py' 

The project structure can be checked using: 

Get-ChildItem -Recurse 

notepad troubleshooting\\Troubleshooting\_Notes.md 

Figure 8: ATS troubleshooting and error-resolution documentation 

&#x20;

12\. Developer Environment and Execution 

The project uses a Python virtual environment for development. 

The virtual environment was activated using: 

..\\.venv\\Scripts\\Activate.ps1 

The prompt displayed: 

(.venv) 

indicating that the virtual environment was active. 

Screenshot 9 – Virtual Environment 

Insert screenshot here. 

Capture the PowerShell window showing the virtual environment activation. 

Caption: 

&#x20;

Figure 9: Activation of the Python virtual environment for ATS development 

&#x20;

13\. Reference to Day 17 ATS Testing 

The documentation also incorporates the results obtained during Day 17 ATS system testing. 

The Day 17 system processed: 

55 candidate-job test cases 

The final results were: 

Metric Result 

Total Test Cases 55 

Accuracy 94.55% 

Precision 100% 

Recall 57.14% 

F1 Score 72.73% 

True Positives 4 

True Negatives 48 

False Positives 0 

False Negatives 3 

Mismatch Cases 7 

These results provide a documented baseline for understanding ATS behavior before and during 

optimization. 

&#x20;

14\. Day 17 Testing Output 

The Day 17 testing command was: 

python -m src.main 

The important output was: 

ATS TESTING RESULTS 

================================================================= 

Total test cases : 55 

Accuracy         : 0.9455 

Precision        : 1.0000 

Recall           : 0.5714 

F1 Score         : 0.7273 

True Positives   : 4 

True Negatives   : 48 

False Positives  : 0 

False Negatives  : 3 

Mismatch cases   : 7 

Figure 10: Day 17 ATS testing results used as a documented system baseline 

&#x20;

15\. Day 18 Optimization Reference 

The Day 19 documentation also references the optimization work completed during Day 18. 

The optimization activities included: 

• Optimized text extraction 

• Noisy resume handling 

• Entity detection optimization 

• Prompt optimization 

• Resume caching 

• Memory monitoring 

• Performance benchmarking 

• Stability testing 

This information was documented so future developers can understand which optimization techniques 

are already available in the ATS. 

&#x20;

16\. Day 18 Performance Benchmark 

The performance benchmark was executed using: 

python -m src.performance\_benchmark 

The benchmark produced: 

DAY 18 - ATS PERFORMANCE BENCHMARK 

================================================================= 

Benchmark Results ----------------------------------------------------------------- 

Text normalization time : 0.012259 seconds 

Entity detection time   : 0.000347 seconds 

Peak memory usage       : 912.57 KB 

Performance checks: 

PASS - Text normalization is within target. 

PASS - Entity detection is within target. 

Benchmark completed successfully. 

================================================================= 

The benchmark confirmed that both text normalization and entity detection were within their defined 

performance targets. 

Figure 11: Day 18 ATS performance benchmark results 

17\. Day 18 Stability Testing 

The stability test suite was executed using: 

python -m pytest -v tests 

The final result was: 

collected 7 items 

tests/test\_performance.py::test\_text\_normalization\_speed PASSED 

tests/test\_performance.py::test\_entity\_detection\_speed PASSED 

tests/test\_stability.py::test\_empty\_resume PASSED 

tests/test\_stability.py::test\_noisy\_text PASSED 

tests/test\_stability.py::test\_skill\_detection PASSED 

tests/test\_stability.py::test\_experience\_detection PASSED 

tests/test\_stability.py::test\_missing\_experience PASSED 

=================================================== 

7 passed 

=================================================== 

This confirmed that all seven implemented performance and stability tests passed successfully. 

&#x20;

Figure 12: Day 18 ATS performance and stability tests successfully passing 

&#x20;

18\. Noisy Resume Handling 

The ATS documentation includes the noisy resume handling implemented during Day 18. 

Example input: 

Pyth0n     Developer!!! 

Skilled in SQL!!! 

P0WER BI 

The normalized result was: 

Python Developer! Skilled in SQL! Power BI 

The noisy resume handler improves the quality of text supplied to downstream ATS processing. 

python src\\noisy\_resume\_handler.py 

Figure 13: Noisy resume normalization demonstration 

&#x20;

19\. Important Source Modules Documented 

The Day 19 documentation references the following Day 18 optimization modules: 

src/ 

├── entity\_optimizer.py 

├── memory\_monitor.py 

├── noisy\_resume\_handler.py 

├── optimized\_extractor.py 

├── performance\_benchmark.py 

├── prompt\_optimizer.py 

└── resume\_cache.py 

These modules represent different optimization and reliability components of the ATS. 

Their responsibilities include: 

Module Purpose 

optimized\_extractor.py Optimized resume text extraction 

noisy\_resume\_handler.py Handling noisy resume text 

entity\_optimizer.py Efficient entity and skill detection 

memory\_monitor.py Monitoring memory usage 

performance\_benchmark.py Measuring system performance 

prompt\_optimizer.py Reducing unnecessary model input 

resume\_cache.py Reusing previously processed resume content 

&#x20;

20\. Important Code Evidence 

The Day 19 documentation does not require copying every source file into the report. Instead, selected 

implementation evidence is documented. 

Example – Prompt Optimization 

File: 

src\\prompt\_optimizer.py 

Important implementation concept: 

IMPORTANT\_SECTIONS = { 

&#x20;   "summary", 

&#x20;   "skills", 

&#x20;   "experience", 

&#x20;   "education", 

&#x20;   "projects", 

&#x20;   "certifications", 

} 

The implementation selects relevant resume sections and ignores unnecessary sections before preparing 

model input. 

Example – Resume Cache 

File: 

src\\resume\_cache.py 

The cache generates a SHA-256 hash from the resume file content: 

key = self.\_cache\_key(file\_path) 

This key is used to identify cached resume-processing results. 

Example – Stability Testing 

File: 

tests\\test\_stability.py 

The tests verify: 

def test\_empty\_resume(): 

&#x20;   result = normalize\_noisy\_text("") 

&#x20;   assert result == "" 

and: 

def test\_skill\_detection(): 

&#x20;   text = "Python SQL Power BI" 

&#x20;   skills = detect\_skills(text) 

&#x20;   assert "python" in skills 

&#x20;   assert "sql" in skills 

&#x20;   assert "power bi" in skills 

These tests verify that the ATS continues to behave correctly for empty input, noisy text, skill detection, 

and experience detection. 

&#x20;

Figure 14: Selected source-code evidence for ATS optimization, caching, and stability testing 

&#x20;

21\. Documentation Validation 

The documentation project structure was verified using: 

Get-ChildItem -Recurse 

The resulting project contained the required documentation resources. 

The final documentation files included: 

docs\\ATS\_Technical\_Documentation.md 

docs\\ATS\_Developer\_Guide.md 

diagrams\\ATS\_Architecture.txt 

diagrams\\ATS\_Data\_Flow.txt 

scoring\\Scoring\_Logic.md 

troubleshooting\\Troubleshooting\_Notes.md 

developer\_guide\\Developer\_Guide.md 

Figure 15: Final documentation files created for Day 19 

22\. Maintainability 

The ATS has been documented using modular components. 

This makes it possible to modify individual parts without changing the complete system. 

For example: 

• Text extraction can be improved independently. 

• Skill detection can be updated independently. 

• Prompt optimization can be modified independently. 

• Caching can be improved independently. 

• Scoring logic can be adjusted independently. 

• Troubleshooting information can be updated as new issues are discovered. 

This modular approach improves long-term maintainability. 

&#x20;

23\. Explainability 

The documentation improves explainability by describing how an ATS decision is generated. 

The general decision path is: 

Resume 

↓ 

Extracted Information 

↓ 

Detected Skills / Experience 

↓ 

Job Requirement Matching 

↓ 

ATS Score 

↓ 

Candidate Rank 

↓ 

SHORTLISTED / REVIEW / REJECTED 

This allows developers and stakeholders to understand the stages involved in producing an ATS result. 

&#x20;

24\. Extensibility 

The documented architecture supports future extensions. 

Possible future improvements include: 

• Additional resume formats. 

• Improved OCR processing. 

• Additional entity types. 

• Advanced skill matching. 

• Improved scoring models. 

• Additional job categories. 

• More sophisticated explainability. 

• Larger test datasets. 

• More automated test cases. 

• Recruitment-platform integration. 

Because the ATS is organized into separate modules, new functionality can be introduced without 

redesigning the complete system. 

&#x20;

25\. Knowledge Transfer 

The knowledge-transfer documentation provides future developers with the information required to 

understand and work with the ATS. 

The documentation explains: 

• System architecture. 

• Data flow. 

• Resume processing. 

• Entity detection. 

• Scoring logic. 

• Candidate ranking. 

• Decision generation. 

• Performance optimization. 

• Testing. 

• Troubleshooting. 

• Development workflow. 

• Maintenance. 

• Future extensions. 

This makes the project easier for another developer to understand and continue. 

&#x20;

26\. Final Deliverables 

Only the following three deliverables are submitted for Day 19. 

Deliverable 1 – ATS Technical Documentation 

File: 

docs/ATS\_Technical\_Documentation.md 

This contains the complete technical explanation of the ATS system, including architecture, workflow, 

data flow, processing components, scoring, testing references, optimization references, maintainability, 

and extensibility. 

\# ATS Technical Documentation 

\## 1. Project Overview 

The Zecpath ATS (Applicant Tracking System) is an AI-powered resume screening and candidate 

evaluation system. 

The system is designed to automate important parts of the recruitment workflow, including resume 

processing, text extraction, candidate analysis, ATS scoring, candidate ranking, decision generation, 

testing, optimization, and documentation. 

The system was developed incrementally across multiple development days. 

The major development stages included: - Resume text extraction - Resume preprocessing - Resume section normalization - Candidate-job matching - ATS scoring - Candidate ranking - AI decision generation - ATS system testing - Performance optimization - Noisy resume handling - Entity detection optimization - Documentation and knowledge transfer 

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

↓ 

Resume Text Extraction 

↓ 

Text Cleaning and Normalization 

↓ 

Resume Section Detection 

↓ 

Entity / Skill Detection 

↓ 

Candidate Profile Processing 

↓ 

Job Requirement Processing 

↓ 

Candidate-Job Matching 

↓ 

ATS Score Calculation 

↓ 

Candidate Ranking 

↓ 

AI Decision 

↓ 

Testing and Validation 

↓ 

Performance Optimization 

\## 4. Major Components 

\### 4.1 Resume Extraction 

The resume extraction stage converts uploaded resume files into machine-readable text. 

The system processes resume content before sending it to later stages. 

The extraction pipeline focuses on: - Text extraction - Whitespace normalization - Bullet normalization - Text cleaning - Handling unnecessary formatting - Preparing text for downstream processing 

\### 4.2 Resume Normalization 

Resume text may contain: - Multiple spaces - Different bullet characters - Unnecessary line breaks - OCR-related character errors - Special characters - Inconsistent capitalization 

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

Examples include: - Skills - Years of experience - Technologies - Job-related keywords 

The Day 18 optimization included efficient skill detection and experience detection. 

Example: 

Input: 

Data Analyst with 3 years of experience. 

Detected experience: 

3 years 

\### 4.4 Candidate Matching 

Candidate information is compared with job requirements. 

Relevant factors include: - Required skills - Candidate skills - Experience - Job role - Resume content - Profile relevance 

\### 4.5 ATS Scoring 

The candidate receives an ATS score based on the matching process. 

The score is then used to support candidate ranking and decision generation. 

\### 4.6 Candidate Ranking 

Candidates are ranked according to their final ATS scores. 

The ranking output contains information such as: - Candidate name - ATS score - Decision - Rank - Job ID - Job title 

\### 4.7 AI Decision 

The ATS produces recruitment decisions. 

The supported decisions used during testing were: - SHORTLISTED - REVIEW - REJECTED 

\### 4.8 ATS Testing 

Day 17 introduced systematic testing of the ATS. 

AI decisions were compared against manually reviewed decisions. 

Testing covered: - Tech profiles - Non-tech profiles - Fresher profiles - Senior profiles 

The system was evaluated using: - Accuracy - Precision - Recall - F1 score - Confusion matrix - Mismatch cases 

\## 5. Day 17 Testing Results 

The ATS was tested using 55 candidate-job test cases. 

Results: - Total test cases: 55 - Accuracy: 94.55% - Precision: 100% - Recall: 57.14% - F1 Score: 72.73% - True Positives: 4 - True Negatives: 48 - False Positives: 0 

\- False Negatives: 3 - Mismatch Cases: 7 

These results showed that the ATS generated no false-positive shortlist decisions in the tested dataset, 

while several manually shortlisted candidates were classified differently by the AI system. 

\## 6. Day 18 Optimization 

Day 18 focused on improving ATS performance and stability. 

The implemented optimization areas included: - Optimized text extraction - Prompt optimization - Resume caching - Entity detection optimization - Memory monitoring - Noisy resume handling - Performance benchmarking - Stability testing 

\## 7. Performance Results 

The optimized system was benchmarked using the performance benchmark module. 

Observed results: 

Text normalization time: 

0.005928 seconds 

Entity detection time: 

0.000243 seconds 

Peak memory usage: 

912.57 KB 

Performance checks: - Text normalization: PASS - Entity detection: PASS 

\## 8. Stability Testing 

The stability test suite verified important ATS behaviors. 

The following tests were successfully executed: - Empty resume handling - Noisy text handling - Skill detection 

\- Experience detection - Missing experience handling - Text normalization performance - Entity detection performance 

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

Important resume sections are prioritized: - Summary - Skills - Experience - Education - Projects - Certifications 

Excessively large text is also limited using a maximum character threshold. 

This reduces unnecessary prompt content and can improve processing efficiency. 

\## 11. Resume Caching 

The ATS includes a resume cache mechanism. 

The cache uses a SHA-256 hash of resume file content as the cache key. 

If the same resume is processed repeatedly, cached information can be reused rather than unnecessarily 

repeating processing. 

Benefits: - Reduced repeated processing 

\- Improved efficiency - Reduced unnecessary computation - Faster repeated access 

\## 12. Performance Benchmarking 

The performance benchmark measures: 

1\. Text normalization time 

2\. Entity detection time 

3\. Processing performance 

4\. Memory usage 

The benchmark provides measurable performance information and checks whether processing remains 

within predefined targets. 

\## 13. Technology Stack 

The project uses Python as the main development language. 

Major technologies and tools used across the ATS project include: - Python - PyMuPDF - python-docx - Pandas - NumPy - Scikit-learn - Pytest - JSON - CSV - PowerShell - Git/GitHub - FastAPI - ChromaDB - Google Gemini / LLM components 

\## 14. Testing Strategy 

Testing is performed at multiple levels. 

\### Functional Testing 

Verifies that individual ATS components perform expected operations. 

\### Performance Testing 

Measures processing time and memory usage. 

\### Stability Testing 

Checks how the system behaves with: - Empty input - Noisy text - Missing information - Different candidate profiles 

\### ATS Decision Testing 

Compares AI decisions against manual reviewer decisions. 

This helps identify: - False positives - False negatives - Decision mismatches - Role-specific weaknesses 

\## 15. Known Limitations 

The current ATS has some limitations. 

1\. Recall is lower than precision in the Day 17 test results. 

2\. Some manually shortlisted candidates were not shortlisted by the AI. 

3\. Technical-role testing showed weaker performance in the tested dataset. 

4\. More diverse resumes are required for broader validation. 

5\. Larger datasets should be used for production-level validation. 

6\. More advanced OCR handling can be added for scanned resumes. 

\## 16. Future Improvements 

Potential future improvements include: - Better decision threshold calibration - Improved technical-role classification - Better OCR support - Larger testing datasets - More advanced semantic matching - Improved model response-time optimization - Production-grade monitoring - Automated regression testing 

\- Improved explainability of ATS decisions 

\## 17. Conclusion 

The ATS was developed through an incremental engineering process covering resume processing, 

candidate ranking, testing, optimization, and documentation. 

Day 17 validated the ATS using 55 candidate-job test cases and achieved 94.55% accuracy with 100% 

precision. 

Day 18 improved system efficiency and stability. The optimized implementation achieved fast text 

normalization and entity detection performance while successfully passing all seven automated tests. 

Day 19 documents the system architecture, processing workflow, scoring logic, troubleshooting 

procedures, and developer instructions to make the ATS easier to maintain, understand, and extend. 

&#x20;

Deliverable 2 – Architecture Diagrams 

Files: 

diagrams/ATS\_Architecture.txt 

============================================================ 

ZECpath AI - ATS ARCHITECTURE 

============================================================ 

RESUME INPUT 

↓ 

Text Extraction       

optimized\_extractor   

↓ 

Text Normalization    

noisy\_resume\_handler  

↓ 

Resume Sections      

Summary / Skills     

Experience / Education 

Projects / Certs     

↓ 

Entity Detection      

Skills / Experience  

↓ 

Candidate-Job         

Matching              

↓ 

ATS Scoring           

↓ 

Candidate Ranking   

↓ 

AI Decision           

SHORTLISTED          

REVIEW               

REJECTED              

↓ 

ATS Testing     

Accuracy / Precision  

Recall / F1         

↓ 

Optimization         

Caching / Prompt      

Performance / Memory 

============================================================ 

diagrams/ATS\_Data\_Flow.txt 

============================================================ 

ATS DATA FLOW 

============================================================ 

Candidate Resume 

↓ 

Resume File        

↓ 

Text Extraction      

↓ 

Cleaning \&           

Normalization        

↓ 

Section Processing   

↓ 

Entity Detection      

Skills               

Experience            

↓ 

Job Requirement     

Processing         

↓ 

Candidate-Job         

Matching          

↓ 

ATS Score             

↓ 

Candidate Ranking    

↓ 

AI Decision           

↓ 

↓                           ↓ 

SHORTLISTED           REVIEW 

↓ 

REJECTED 

Testing Flow: 

AI Decision 

↓ 

Manual Review 

↓ 

Comparison 

↓ 

Accuracy / Precision / 

Recall / F1 / Mismatch 

These documents describe: 

• High-level ATS architecture. 

• Resume processing flow. 

• Candidate information flow. 

• Job matching flow. 

• Scoring and decision flow. 

&#x20;

Deliverable 3 – Developer Guide 

File: 

developer\_guide/Developer\_Guide.md 

The Developer Guide contains: 

• Environment setup. 

• Project structure. 

• Execution instructions. 

• Testing instructions. 

• Important modules. 

• Troubleshooting. 

• Maintenance instructions. 

• Extension guidelines. 

\# ATS Developer Guide 

\## 1. Introduction 

This guide explains how developers can understand, run, test, maintain, and extend the ATS. 

The system is organized into separate development stages so that individual components can be 

improved without changing the complete system. 

\## 2. Environment Setup 

Activate the Python virtual environment. 

Example: 

..\\.venv\\Scripts\\Activate.ps1 

Verify Python: 

python --version 

\## 3. Project Structure 

The overall Zecpath project contains multiple development-day directories. 

Important stages include: - Resume extraction - Candidate ranking 

\- ATS testing - ATS optimization - Documentation 

The Day 19 project contains documentation resources. 

\## 4. Running the ATS Components 

Developers should execute Python modules from the appropriate project root. 

Example: 

python -m src.performance\_benchmark 

For scripts that do not depend on package imports: 

python src\\noisy\_resume\_handler.py 

\## 5. Running Tests 

Navigate to the appropriate project directory. 

Then run: 

python -m pytest -v tests 

The Day 18 stability and performance suite contains seven tests. 

Expected successful result: 

7 passed 

\## 6. Performance Benchmark 

Run: 

python -m src.performance\_benchmark 

The benchmark measures: - Text normalization time - Entity detection time - Peak memory usage 

The observed benchmark results were: 

Text normalization: 

0.005928 seconds 

Entity detection: 

0.000243 seconds 

Peak memory: 

912.57 KB 

\## 7. Noisy Resume Testing 

Run: 

python src\\noisy\_resume\_handler.py 

The demonstration verifies normalization of noisy resume text. 

Example: 

Pyth0n → Python 

P0WER BI → Power BI 

\## 8. Adding New Skills 

Skill detection can be extended by adding new supported skill patterns to the entity detection logic. 

After modifying the implementation: 

1\. Add or update tests. 

2\. Run pytest. 

3\. Verify that existing tests continue to pass. 

4\. Run the performance benchmark. 

\## 9. Adding New Resume Rules 

When adding a new extraction or normalization rule: 

1\. Implement the rule. 

2\. Test normal input. 

3\. Test noisy input. 

4\. Test missing input. 

5\. Test empty input. 

6\. Measure performance. 

7\. Document the change. 

\## 10. Maintaining Performance 

Developers should avoid unnecessary repeated processing. 

Recommended techniques include: - Text normalization - Prompt reduction - Resume caching - Efficient entity detection - Memory monitoring 

\## 11. Regression Testing 

Every major modification should be followed by: 

python -m pytest -v tests 

The performance benchmark should also be executed when changes affect processing speed. 

\## 12. Extension Guidelines 

Future developers can extend the system with: - Additional entity types - More resume formats - Better OCR - Additional scoring factors - Improved semantic matching - Additional recruitment decisions - API integration - Database integration - Monitoring 

\## 13. Documentation Maintenance 

Whenever system behavior changes, update: - ATS Technical Documentation - Scoring Logic - Troubleshooting Notes - Developer Guide 

Documentation should remain synchronized with the implementation. 

\## 14. Development Best Practices 

Developers should: - Keep modules focused on one responsibility. - Add tests for new functionality. - Avoid unnecessary processing. - Use clear function names. - Document important logic. - Validate edge cases. - Measure performance after optimization. - Keep troubleshooting information updated. 

\## 15. Conclusion 

The Developer Guide provides the information required for another developer to understand and 

continue development of the ATS. 

The combination of technical documentation, scoring documentation, troubleshooting notes, testing 

procedures, and performance information supports maintainability and future extension of the system. 

&#x20;

27\. Final Submission Structure 

The final Day 19 project should be organized as: 

DAY\_19\_ATS\_DOCUMENTATION/ 

│ 

├── 1. ATS Technical Documentation/ 

│   └── ATS\_Technical\_Documentation.md 

│ 

├── 2. Architecture Diagrams/ 

│   ├── ATS\_Architecture.txt 

│   └── ATS\_Data\_Flow.txt 

│ 

└── 3. Developer Guide/ 

&#x20;   └── Developer\_Guide.md 

The screenshots are supporting evidence for the main technical documentation and do not need to be 

treated as separate deliverables. 

&#x20;

28\. Conclusion 

Day 19 successfully completed the ATS Documentation and Knowledge Transfer phase of the Zecpath 

AI System. 

The system architecture, data flow, candidate scoring logic, troubleshooting procedures, developer 

instructions, testing references, and optimization information were documented in a structured manner. 

The documentation provides a clear technical reference for understanding how the ATS operates from 

resume input to candidate decision. It also provides developers with the information required to execute, 

maintain, troubleshoot, and extend the system. 

The combination of technical documentation, architecture diagrams, and developer guidance improves 

the maintainability, explainability, and extensibility of the ATS. 

Therefore, Day 19 successfully achieved its objective of preparing the ATS for effective knowledge 

transfer and future development. 

&#x20;

