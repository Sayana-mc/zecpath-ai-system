DAY 32 – SCREENING SYSTEM FINALIZATION

ZecPath – AI-Powered Resume Screening and Hiring Assistant

Prepared By: Sayana M C

Date: 23 September 2026



1\. Objective

The objective of Day 32 was to finalize the AI Screening System and prepare it for production handover.

The work focused on:

•	Completing the overall AI screening workflow.

•	Preparing final technical documentation.

•	Explaining the API and module structure.

•	Demonstrating the end-to-end screening process.

•	Preparing the project for code and logic handover.

•	Evaluating the final screening system.



2\. Work Completed

The final system combines the modules developed during the previous days:

HR Screening Questions

↓

Voice / Transcript Input

↓

Speech-to-Text \& Cleaning

↓

Answer Intent Understanding

↓

Information Extraction

↓

Answer Validation

↓

Screening Scoring

↓

Confidence / Sentiment Analysis

↓

Conversation Flow Handling

↓

Screening Report Generation

↓

Final Recruiter-Friendly Result



3\. Deliverable 1 – Complete AI Screening System

3.1 Description

The Complete AI Screening System integrates the individual screening components into a single workflow.

The system processes candidate answers and produces structured screening information including:

•	Candidate answers

•	Detected intent

•	Extracted information

•	Answer validation

•	Screening scores

•	Confidence indicators

•	Conversation status

•	Recruiter-friendly screening results

3.2 Main System Flow

Candidate

↓

Screening Question

↓

Candidate Response

↓

Transcript Processing

↓

Intent Detection

↓

Information Extraction

↓

Answer Validation

↓

Scoring

↓

Confidence / Behavioral Analysis

↓

Screening Report

3.3 Main Components

Component	Purpose

HR Question Dataset	Stores screening questions

Transcript Processor	Cleans transcript text

Intent Classifier	Identifies answer intent

Information Extractor	Extracts skills, experience, salary and availability

Answer Validator	Detects vague/off-topic answers

Scoring Engine	Calculates screening scores

Confidence Analysis	Analyses communication signals

Conversation Flow	Handles silence, confusion and retries

Report Generator	Generates recruiter-ready output



4\. Deliverable 2 – Technical Documentation

4.1 Project Structure

Use your actual final folder structure here. A suitable documentation structure is:

zecpath-ai-system/

│

├── day22\_hr\_screening\_dataset/

├── day23\_transcript\_data\_architecture/

├── day24\_speech\_to\_text/

├── day25\_answer\_intent\_engine/

├── day26\_screening\_scoring\_engine/

├── day27\_confidence\_sentiment\_analysis/

├── day28\_ai\_screening\_report/

├── day29\_conversation\_flow/

├── day30\_screening\_system\_testing/

├── day31\_edge\_case\_handling/

│

└── day32\_screening\_system\_finalization/

&#x20;   ├── src/

&#x20;   ├── tests/

&#x20;   ├── output/

&#x20;   └── README.md

4.2 Technical Architecture

Input Layer

↓

Transcript / Candidate Answer

↓

Processing Layer

↓

Intent + Extraction + Validation

↓

Evaluation Layer

↓

Scoring + Confidence + Behavioral Signals

↓

Decision Layer

↓

Conversation / Screening Result

↓

Reporting Layer

↓

Recruiter Report

4.3 Technologies Used

Python

Pytest

JSON

Regular Expressions

PowerShell

Virtual Environment

Git / GitHub



5\. API Design Explanation

5.1 Purpose

The API layer provides a structured way for external applications such as the Zecpath frontend, recruiter dashboard or voice screening system to communicate with the screening engine.

5.2 Example API Flow

POST /screening/start

↓

Start candidate screening



POST /screening/answer

↓

Process candidate answer



GET /screening/{candidate\_id}

↓

Retrieve screening information



GET /screening/{candidate\_id}/report

↓

Generate final screening report

5.3 Example Request

{

&#x20;   "candidate\_id": "C001",

&#x20;   "question\_id": "Q001",

&#x20;   "answer": "I have experience with Python, SQL and Power BI."

}

5.4 Example Response

{

&#x20;   "candidate\_id": "C001",

&#x20;   "question\_id": "Q001",

&#x20;   "intent": "skills",

&#x20;   "answer\_status": "valid",

&#x20;   "extracted\_information": {

&#x20;       "skills": \[

&#x20;           "Python",

&#x20;           "SQL",

&#x20;           "Power BI"

&#x20;       ]

&#x20;   }

}



6\. Deliverable 3 – Live Demo Output

6.1 Demo Objective

The end-to-end demo was used to verify that the complete screening workflow works from candidate input to final screening output.

6.2 Demo Input

Example candidate responses:

I have experience with Python, SQL, Excel and Power BI.

I have one year of experience including a data analyst internship.

I am available to join immediately.

I am expecting around 4 LPA.

6.3 Expected Processing

Candidate Answer

↓

Intent Detection

↓

Information Extraction

↓

Validation

↓

Scoring

↓

Final Screening Result

6.4 Example Demo Output

Candidate ID: C001

Skills:

Python

SQL

Excel

Power BI

Experience:

1 year

Availability:

Immediate

Salary Expectation:

4 LPA

Answer Status:

Valid

Screening Evaluation:

Completed



7\. Deliverable 4 – Screening AI Evaluation Report

7.1 Purpose

The evaluation report documents the final testing and performance of the screening system.

The system was evaluated for:

•	Intent detection

•	Information extraction

•	Answer validation

•	Scoring

•	Conversation handling

•	Edge-case handling

•	Final report generation

7.2 Evaluation Areas

Area	Evaluation

Intent Detection	Skills, experience, availability and salary intents

Information Extraction	Candidate information extraction

Answer Validation	Valid, vague and off-topic answers

Scoring	Clarity, relevance, completeness and consistency

Conversation Flow	Silence, confusion and repeated answers

Edge Cases	Missing answers, noise and language mixing

Report Generation	Recruiter-ready structured output

7.3 Evaluation Result

Use your actual final test result here:

Total Test Cases:

Passed:

Failed:

System Status:

If your final tests show all cases passing, write:

All final automated test cases passed successfully.

Overall Status: PASSED



8\. Day 32 Commands

8.1 Activate Virtual Environment

&#x20; 

Figure 1 – Activating Python Virtual Environment

cd C:\\Users\\sayan\\Documents\\zecpath-ai-system

.\\.venv\\Scripts\\Activate.ps1

8.2 Check Day 32 Project Structure

&#x20;

Figure 2 – Day 32 Project Structure

Get-ChildItem .\\day32\_screening\_system\_finalization -Recurse

8.3 Check Python Files

&#x20; 

Figure 3 – Day 32 Python Source Files

Get-ChildItem .\\day32\_screening\_system\_finalization\\src -Name



9\. Creating / Editing Files with Notepad

notepad .\\day32\_screening\_system\_finalization\\src\\main.py

&#x20;

Figure 4 – Day 32 Main System Code

For technical documentation:

notepad .\\day32\_screening\_system\_finalization\\README.md

Screenshot 

Figure 5 – Day 32 Technical Documentation

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

10\. Running Final Tests

Run the complete Day 32 test suite:

pytest .\\day32\_screening\_system\_finalization\\tests -v

Screenshot Title:

Figure 6 – Day 32 Final System Test Results

Expected successful format:

================ test session starts ================



collected ... items



... PASSED

... PASSED

... PASSED



================ ... passed in ...s ================

Use the actual terminal output in your screenshot.

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

11\. Running the Final AI Screening System

If your final entry-point file is main.py:

python .\\day32\_screening\_system\_finalization\\src\\main.py

Screenshot Title:

Figure 7 – Day 32 End-to-End AI Screening Demo

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

12\. Checking Generated Output

If your final system generates an output JSON:

Get-ChildItem .\\day32\_screening\_system\_finalization\\output

Screenshot Title:

Figure 8 – Generated Screening Output Files

Then display the output:

Get-Content .\\day32\_screening\_system\_finalization\\output\\screening\_report.json

If your actual filename is different, use the actual filename shown by Get-ChildItem.

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

13\. Checking JSON Output Clearly

For formatted JSON:

Get-Content .\\day32\_screening\_system\_finalization\\output\\screening\_report.json | ConvertFrom-Json | ConvertTo-Json -Depth 10

Screenshot Title:

Figure 9 – Final Structured Screening Report

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

14\. Final System Verification

Run:

pytest -v

Screenshot Title:

Figure 10 – Complete Zecpath AI System Test Verification

This verifies the complete project test suite.

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

15\. Git Verification

Check changed files:

git status

Screenshot Title:

Figure 11 – Git Status Before Final Commit

Check recent commits:

git log --oneline -5

Screenshot Title:

Figure 12 – Git Commit History

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

16\. Git Add and Commit

After confirming that everything is correct:

git add .

Then:

git status

Screenshot Title:

Figure 13 – Files Staged for Final Handover

Commit:

git commit -m "Finalize AI screening system"

Screenshot Title:

Figure 14 – Day 32 Final Commit

If your project uses a remote repository and you are supposed to push:

git push

Screenshot Title:

Figure 15 – Final Code Handover to Repository

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

17\. Final Handover Checklist

Before completing Day 32, verify:

☑ Source code completed

☑ Tests completed

☑ Technical documentation completed

☑ API design documented

☑ End-to-end demo completed

☑ Screening output generated

☑ Evaluation report completed

☑ Edge cases documented

☑ Code committed to Git

☑ Final project ready for handover

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

18\. Final Deliverables Summary

Deliverable 1 – Complete AI Screening System

The complete AI screening workflow was finalized by integrating the major components developed throughout the project.

Question

&#x20;  ↓

Candidate Answer

&#x20;  ↓

Transcript Processing

&#x20;  ↓

Intent Understanding

&#x20;  ↓

Information Extraction

&#x20;  ↓

Validation

&#x20;  ↓

Scoring

&#x20;  ↓

Confidence / Behavioral Analysis

&#x20;  ↓

Conversation Handling

&#x20;  ↓

Screening Report

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

Deliverable 2 – Technical Documentation

The technical documentation contains:

•	System architecture

•	Project structure

•	Module descriptions

•	Data flow

•	API design

•	Input/output formats

•	Testing procedure

•	Deployment/handover information

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

Deliverable 3 – Live Demo Output

The end-to-end demonstration shows:

•	Candidate screening question

•	Candidate response

•	Answer understanding

•	Information extraction

•	Validation

•	Scoring

•	Final screening result

•	Recruiter-friendly output

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

Deliverable 4 – Screening AI Evaluation Report

The evaluation report contains:

•	Test cases

•	Intent detection results

•	Extraction results

•	Validation results

•	Scoring results

•	Conversation-flow evaluation

•	Edge-case evaluation

•	Final test status

•	Observations and limitations

\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

19\. Conclusion

Day 32 completed the finalization stage of the AI Screening System.

The system was organized into a complete screening workflow covering candidate question handling, transcript processing, answer understanding, information extraction, validation, scoring, confidence analysis, conversation handling, edge-case handling and recruiter-friendly reporting.

The final system was tested, documented and prepared for code handover and end-to-end demonstration.

Final Status: AI Screening System Finalization Completed.





