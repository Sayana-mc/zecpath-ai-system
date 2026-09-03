# AI Data Entity Design

## 1. Overview

The ZECpath AI System uses structured data entities to represent candidates, job descriptions, skills, and professional experience.

The purpose of the entity design is to convert unstructured recruitment information into AI-ready structured data.

---

## 2. Candidate Profile

A Candidate Profile represents the basic information of a job applicant.

### Main attributes

- Candidate ID
- Name
- Email
- Phone
- Location
- Current designation
- Total experience

### Example

```json
{
  "candidate_id": "C001",
  "name": "Arjun Nair",
  "email": "arjun.nair@example.com",
  "location": "Kochi, Kerala",
  "current_designation": "Senior Software Developer",
  "total_experience_years": 6
}