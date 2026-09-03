# Day 4 – Data Understanding & Structuring

## 1. Objective

The objective of Day 4 is to understand recruitment data and convert unstructured resume and job description information into structured AI-ready formats.

The analysis covers 10 resumes from different professional domains and job descriptions for different roles.

---

# 2. Resume Dataset

A total of 10 resumes were analyzed.

| No. | Candidate | Designation | Domain | Experience |
|---|---|---|---|---|
| 1 | Arjun Nair | Senior Software Developer | Software Development | 6 years |
| 2 | Reshma Pillai | Senior Data Analyst | Data Analytics | 5 years |
| 3 | Vishnu Prasad | Regional Sales Manager | Sales | 9 years |
| 4 | Meera Krishnan | Marketing Manager | Digital Marketing | 7 years |
| 5 | Sandeep Kumar | Senior Financial Analyst | Finance | 6 years |
| 6 | Priya Varma | Senior Talent Acquisition Specialist | Human Resources | 7 years |
| 7 | Aiswarya Raj | Senior Graphic Designer | Design | 5 years |
| 8 | Karthik Suresh | Senior Engineer – Production | Mechanical Engineering | 8 years |
| 9 | Fathima Beevi | Customer Support Team Lead | Customer Support | 6 years |
| 10 | Lakshmi Devi | Senior Secondary Mathematics Teacher | Education | 8 years |

---

# 3. Domain Analysis

The resumes represent different professional domains.

### Software Development

Arjun Nair has experience in full-stack software development.

Key skills include:

- JavaScript
- TypeScript
- React
- Node.js
- Express
- MongoDB
- PostgreSQL
- REST APIs
- GraphQL
- Docker
- AWS
- CI/CD

### Data Analytics

Reshma Pillai has experience in data analytics.

Key skills include:

- SQL
- Python
- pandas
- NumPy
- Power BI
- DAX
- Excel
- VBA
- Statistical Analysis
- ETL

### Sales

Vishnu Prasad has experience in FMCG sales management.

Key skills include:

- Salesforce CRM
- Sales Forecasting
- Territory Planning
- Trade Promotion Management
- Excel
- Team Leadership
- B2B Negotiation
- Client Relationship Management

### Digital Marketing

Meera Krishnan has experience in digital marketing and brand strategy.

Key skills include:

- SEO
- SEM
- Google Ads
- Google Analytics
- Meta Ads Manager
- HubSpot
- Content Strategy
- Marketing Automation
- Budget Planning
- Brand Storytelling

### Finance

Sandeep Kumar has experience in financial analysis.

Key skills include:

- Financial Modeling
- Advanced Excel
- SAP FICO
- Power BI
- Variance Analysis
- GST
- Statutory Compliance

### Human Resources

Priya Varma has experience in recruitment and talent acquisition.

Key skills include:

- Applicant Tracking Systems
- Greenhouse
- Zoho Recruit
- Boolean Sourcing
- LinkedIn
- Naukri
- HRIS
- Interview Coordination
- Stakeholder Management
- Negotiation

### Graphic Design

Aiswarya Raj has experience in graphic and brand design.

Key skills include:

- Figma
- Adobe Photoshop
- Adobe Illustrator
- Adobe InDesign
- After Effects
- Brand Storytelling
- Typography
- Layout
- Creative Direction

### Mechanical Engineering

Karthik Suresh has experience in production planning and process improvement.

Key skills include:

- AutoCAD
- SolidWorks
- GD&T
- Production Planning
- MRP
- Six Sigma
- Root Cause Analysis
- Shop-floor Supervision
- Process Documentation

### Customer Support

Fathima Beevi has experience in customer service and team leadership.

Key skills include:

- Zendesk
- Freshdesk
- Voice Support
- Chat Support
- Excel
- Conflict Resolution
- Team Coordination
- Coaching
- Active Listening

### Education

Lakshmi Devi has experience as a mathematics teacher.

Key skills include:

- Curriculum Design
- Google Classroom
- Student Assessment
- Excel
- Classroom Management
- Parent-Teacher Coordination
- Mentoring

---

# 4. Skills Identified

The resumes contain both technical and interpersonal skills.

## Technical Skills

Examples include:

- Python
- SQL
- JavaScript
- React
- Node.js
- Power BI
- Excel
- Salesforce
- SAP FICO
- Figma
- AutoCAD
- SolidWorks
- Six Sigma
- Zendesk
- Google Classroom

## Interpersonal Skills

Examples include:

- Communication
- Leadership
- Teamwork
- Negotiation
- Mentoring
- Stakeholder Management
- Conflict Resolution
- Client Relationship Management
- Collaboration

---

# 5. Experience Patterns

The resumes show several common experience patterns.

## Career Progression

Many candidates show progression from junior or associate roles to senior roles.

Examples:

Junior Software Developer
→ Software Developer
→ Senior Software Developer

Junior Data Analyst
→ Data Analyst
→ Senior Data Analyst

Assistant Teacher
→ Mathematics Teacher
→ Senior Secondary Mathematics Teacher

Associate
→ Senior Associate
→ Team Lead

---

# 6. Designation Patterns

Common designation levels include:

- Junior
- Associate
- Executive
- Engineer
- Analyst
- Developer
- Manager
- Senior
- Team Lead
- Specialist

The designation generally indicates the candidate's career level and professional responsibility.

---

# 7. Education Patterns

The resumes contain different educational qualifications.

Examples:

- B.Tech Computer Science
- B.Sc Statistics
- BBA
- MBA Marketing
- M.Com Finance
- MBA Human Resources
- B.Des Communication Design
- B.Tech Mechanical Engineering
- B.Com
- B.Ed
- M.Sc Mathematics

Education information generally contains:

- Degree
- Field of study
- Institution
- Start year
- End year
- Grade or CGPA when available

---

# 8. Certification Patterns

Certifications found in the resumes include:

- AWS Certified Cloud Practitioner
- MongoDB Certified Developer Associate
- Google Data Analytics Professional Certificate
- Microsoft Power BI Data Analyst Associate
- CPSL
- Google Ads Certification
- HubSpot Content Marketing Certification
- CMA (US)
- SHRM-CP
- LinkedIn Certified Recruiter
- Google UX Design Certificate
- Adobe Certified Professional
- Six Sigma Green Belt
- SolidWorks Associate Certification
- Voice & Accent Training Certificate
- Kerala TET

Certifications provide additional evidence of professional knowledge and specialization.

---

# 9. Job Description Data

Job descriptions are structured separately from resume data.

Important JD attributes include:

- Job ID
- Job title
- Department
- Location
- Employment type
- Required skills
- Preferred skills
- Responsibilities
- Education requirements
- Experience requirements
- Certifications
- Soft skills

---

# 10. Standard Data Entities

The recruitment data is organized into four major entities:

## Candidate Profile

Stores basic candidate information.

## Job Profile

Stores job requirements and responsibilities.

## Skill Object

Stores skill name and skill category.

## Experience Object

Stores professional experience including designation, company and employment period.

---

# 11. Structured Data Transformation

The original resumes are unstructured documents.

The information is transformed into structured JSON objects.

Example:

Resume
→ Candidate Profile
→ Skills
→ Experience
→ Education
→ Certifications
→ Languages

This structure makes the data easier for AI systems to process.

---

# 12. AI Readiness

The structured data can support future ZECpath AI components such as:

- Resume parsing
- ATS matching
- Candidate screening
- Skill matching
- Candidate ranking
- Interview analysis
- Hiring decision support

---

# 13. Conclusion

The Day 4 analysis identified important recruitment data fields from 10 resumes covering different professional domains.

The identified information was organized into standard entities and JSON schema structures.

This provides a consistent foundation for further AI-based recruitment processing in the ZECpath AI System.