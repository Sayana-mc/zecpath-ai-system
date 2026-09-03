\# Day 6 - Job Description Parsing System



\## 1. Objective



The objective of Day 6 is to convert employer job descriptions into structured and AI-readable job requirement objects.



The system extracts and normalizes:



\- Job role

\- Department

\- Domain

\- Required experience

\- Education

\- Required skills

\- Preferred skills

\- Soft skills

\- Responsibilities

\- Location

\- Employment type



\---



\## 2. Input



The input dataset is:



`input/job\_descriptions.json`



It contains 10 job descriptions:



1\. Python Developer

2\. Data Analyst

3\. AI/ML Engineer

4\. Financial Analyst

5\. HR Executive

6\. Graphic Designer

7\. Mechanical Engineer

8\. Customer Support Executive

9\. Mathematics Teacher

10\. Sales Manager



\---



\## 3. System Architecture



The parsing pipeline is:



Job Description JSON

&#x20;       |

&#x20;       v

JD Cleaner

&#x20;       |

&#x20;       v

Skill and Role Normalizer

&#x20;       |

&#x20;       v

JD Parser

&#x20;       |

&#x20;       v

AI-Readable JD Profile

&#x20;       |

&#x20;       v

Structured JSON Output



\---



\## 4. JD Cleaning



The `jd\_cleaner.py` module performs:



\- Whitespace normalization

\- Line-break normalization

\- Unicode artifact replacement

\- Title normalization

\- Experience normalization



\---



\## 5. Skill Normalization



The `skill\_normalizer.py` module maps skill variations to canonical names.



Examples:



| Input | Canonical Skill |

|---|---|

| powerbi | Power BI |

| structured query language | SQL |

| fast api | FastAPI |

| postgres | PostgreSQL |

| mongo | MongoDB |

| machine learning | Machine Learning |

| scikit learn | Scikit-learn |



Duplicate skills are removed.



\---



\## 6. Role Normalization



Role variations are mapped to canonical role names.



Examples:



| Input | Canonical Role |

|---|---|

| python programmer | Python Developer |

| machine learning engineer | AI/ML Engineer |

| ai ml engineer | AI/ML Engineer |

| math teacher | Mathematics Teacher |

| human resources executive | HR Executive |



\---



\## 7. Structured JD Profile



Each job description is converted into the following structure:



\- job\_id

\- role

\- experience

\- education

\- skills

\- responsibilities

\- location

\- employment\_type

\- ai\_metadata



\---



\## 8. AI Metadata



The system generates useful metadata:



\- Canonical role

\- Required skill count

\- Preferred skill count

\- Soft skill count



This information can later be used by the AI resume matching system.



\---



\## 9. Output



The parser generates one JSON file for each JD.



Example:



`JD001\_python\_developer.json`



The output is structured for downstream AI processing and candidate-job matching.



\---



\## 10. Testing



Automated tests are implemented using pytest.



The test suite verifies:



\- JD text cleaning

\- Skill normalization

\- Duplicate skill removal

\- Role normalization

\- Experience normalization

\- AI JD profile creation



\---



\## 11. Result



All job descriptions are successfully converted into structured AI-readable profiles.



The resulting JD profiles can be used in later stages for:



\- Resume-JD matching

\- Skill matching

\- Candidate ranking

\- AI recruitment

\- Applicant filtering

\- Retrieval-Augmented Generation

