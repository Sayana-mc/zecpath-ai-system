"""Seed realistic, professional synthetic demo candidates and openings for Days 45-50.

Fictional demo profiles requested by user:
- Arun Kumar (Senior Python Developer, 6 yrs experience)
- Neha Thomas (MERN Stack Developer, 3 yrs experience)
- Rahul Menon (Fresher / Junior Python Developer, 1 yr experience)
- Anjali Nair (Data Analyst, 2 yrs experience)
- Vivek Raj (Enterprise Java Developer, 4 yrs experience)
"""

import sys
from pathlib import Path

ROOT = Path(r"C:\Users\sayan\Documents\zecpath-ai-system")
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src import database

OPENINGS = [
    {
        "opening_id": "job_python_lead",
        "title": "Senior Python Developer",
        "description": "Architect high-throughput REST APIs, asynchronous task queues, and relational data pipelines using Python, FastAPI, and Redis.",
        "required_skills": ["Python", "FastAPI", "SQL", "System Design", "AsyncIO"],
        "preferred_skills": ["Docker", "Redis", "PostgreSQL", "Celery"],
        "status": "OPEN",
        "minimum_education": "Bachelor's degree in Computer Science or related field",
        "minimum_years_experience": 5.0,
    },
    {
        "opening_id": "job_mern_dev",
        "title": "MERN Stack Developer",
        "description": "Develop full-stack web applications using React, Node.js, Express, and MongoDB with modern responsive design.",
        "required_skills": ["React", "Node.js", "Express", "MongoDB", "REST APIs"],
        "preferred_skills": ["TypeScript", "Redux", "Tailwind CSS"],
        "status": "OPEN",
        "minimum_education": "Bachelor's degree in IT/Computer Science",
        "minimum_years_experience": 3.0,
    },
    {
        "opening_id": "job_java_eng",
        "title": "Enterprise Java Developer",
        "description": "Build scalable backend microservices using Java 17, Spring Boot, Hibernate, and Apache Kafka.",
        "required_skills": ["Java", "Spring Boot", "OOP Principles", "Microservices", "SQL"],
        "preferred_skills": ["Kafka", "Docker", "Kubernetes", "AWS"],
        "status": "OPEN",
        "minimum_education": "B.Tech in Computer Science or equivalent",
        "minimum_years_experience": 4.0,
    },
    {
        "opening_id": "job_data_analyst",
        "title": "Data Analyst & BI Specialist",
        "description": "Perform exploratory data analysis, dashboard creation, SQL transformations, and predictive cohort metrics.",
        "required_skills": ["SQL", "Python", "Data Cleaning", "Tableau", "Statistics"],
        "preferred_skills": ["Power BI", "Excel", "Pandas", "Scikit-Learn"],
        "status": "OPEN",
        "minimum_education": "Degree in Mathematics, Statistics, or Computer Science",
        "minimum_years_experience": 2.0,
    },
    {
        "opening_id": "job_fresher_python",
        "title": "Junior Python Developer",
        "description": "Entry-level development role for enthusiastic engineers with solid foundations in Python, data structures, and algorithms.",
        "required_skills": ["Python", "OOP", "SQL", "Git", "Problem Solving"],
        "preferred_skills": ["FastAPI", "HTML/CSS", "Linux"],
        "status": "OPEN",
        "minimum_education": "Bachelor's degree in Engineering or Computer Applications",
        "minimum_years_experience": 0.0,
    },
]

CANDIDATES = [
    {
        "candidate_id": "cand_arun_kumar",
        "name": "Arun Kumar",
        "email": "arun.kumar.dev@example.com",
        "opening_id": "job_python_lead",
        "skills": ["Python", "FastAPI", "SQL", "System Design", "AsyncIO", "Redis", "Docker", "PostgreSQL"],
        "resume_text": "Senior Python Backend Engineer with 6 years of experience architecting distributed microservices, FastAPI REST endpoints, and optimizing PostgreSQL database concurrency. Proven track record of scaling high-throughput APIs to 5,000+ req/sec.",
        "resume_filename": "Arun_Kumar_Senior_Python_Resume.pdf",
        "application_status": "INTERVIEW",
        "score": 88.5,
        "score_evidence": "Demonstrated 6 years of hands-on production experience in Python, FastAPI, and system architecture. Strong semantic alignment with required backend skills.",
        "location": "Bengaluru",
        "relocation_willingness": True,
        "work_mode_preference": "HYBRID",
        "availability_date": "2026-12-01",
    },
    {
        "candidate_id": "cand_neha_thomas",
        "name": "Neha Thomas",
        "email": "neha.thomas.mern@example.com",
        "opening_id": "job_mern_dev",
        "skills": ["React", "Node.js", "Express", "MongoDB", "REST APIs", "TypeScript", "Redux"],
        "resume_text": "Full Stack MERN Developer with 3 years experience building responsive web apps with React hooks, Node.js event-driven backend, Express middleware, and MongoDB database indexing.",
        "resume_filename": "Neha_Thomas_MERN_Stack_Resume.pdf",
        "application_status": "INTERVIEW",
        "score": 84.0,
        "score_evidence": "Solid 3-year track record in React component lifecycles, state management, and Node.js REST API engineering.",
        "location": "Kochi",
        "relocation_willingness": False,
        "work_mode_preference": "HYBRID",
        "availability_date": "2026-11-20",
    },
    {
        "candidate_id": "cand_rahul_menon",
        "name": "Rahul Menon",
        "email": "rahul.menon.tech@example.com",
        "opening_id": "job_fresher_python",
        "skills": ["Python", "OOP", "SQL", "Git", "Problem Solving", "FastAPI"],
        "resume_text": "Computer Science Graduate with 1 year internship experience developing Python automation tools, REST endpoints, and writing automated test cases. Winner of college hackathon.",
        "resume_filename": "Rahul_Menon_Junior_Python_Resume.pdf",
        "application_status": "IN_REVIEW",
        "score": 76.0,
        "score_evidence": "Foundational Python competence, active GitHub portfolio, and 1 year internship experience in backend development.",
        "location": "Thiruvananthapuram",
        "relocation_willingness": True,
        "work_mode_preference": "ONSITE",
        "availability_date": "Immediate",
    },
    {
        "candidate_id": "cand_anjali_nair",
        "name": "Anjali Nair",
        "email": "anjali.nair.analytics@example.com",
        "opening_id": "job_data_analyst",
        "skills": ["SQL", "Python", "Data Cleaning", "Tableau", "Statistics", "Power BI", "Excel"],
        "resume_text": "Data Analyst with 2 years experience performing SQL cohort analysis, designing executive Tableau dashboards, and building predictive churn models using Python Pandas and Scikit-Learn.",
        "resume_filename": "Anjali_Nair_Data_Analyst_Resume.pdf",
        "application_status": "SHORTLISTED",
        "score": 81.0,
        "score_evidence": "Proven analytics track record with complex SQL joins, automated BI reporting pipelines, and statistical modeling.",
        "location": "Bengaluru",
        "relocation_willingness": True,
        "work_mode_preference": "REMOTE",
        "availability_date": "2026-12-15",
    },
    {
        "candidate_id": "cand_vivek_raj",
        "name": "Vivek Raj",
        "email": "vivek.raj.java@example.com",
        "opening_id": "job_java_eng",
        "skills": ["Java", "Spring Boot", "OOP Principles", "Microservices", "SQL", "Kafka", "Docker"],
        "resume_text": "Enterprise Java Software Engineer with 4 years experience designing resilient Spring Boot microservices, Kafka event streaming, and Hibernate ORM data structures.",
        "resume_filename": "Vivek_Raj_Java_Microservices_Resume.pdf",
        "application_status": "INTERVIEW",
        "score": 85.0,
        "score_evidence": "Extensive experience in Java 17 enterprise architecture, Spring Cloud, microservice decomposition, and asynchronous message brokers.",
        "location": "Chennai",
        "relocation_willingness": True,
        "work_mode_preference": "HYBRID",
        "availability_date": "2026-11-30",
    },
]


def seed():
    print("=" * 70)
    print("SEEDING REALISTIC SYNTHETIC DEMO DATA FOR DAYS 45-50")
    print("=" * 70)

    # 1. Upsert Openings
    for op in OPENINGS:
        existing = database.get_opening(op["opening_id"])
        if existing:
            database.update_opening(op["opening_id"], op)
            print(f"  [UPDATED OPENING] {op['opening_id']} -> {op['title']}")
        else:
            database.create_opening(op)
            print(f"  [CREATED OPENING] {op['opening_id']} -> {op['title']}")

    # 2. Upsert Candidates
    for c in CANDIDATES:
        existing = database.get_candidate(c["candidate_id"])
        if existing:
            database.update_candidate(c["candidate_id"], c)
            print(f"  [UPDATED CANDIDATE] {c['candidate_id']} -> {c['name']} ({c['email']})")
        else:
            database.create_candidate(c)
            print(f"  [CREATED CANDIDATE] {c['candidate_id']} -> {c['name']} ({c['email']})")

    print("\nSUCCESS: All realistic synthetic demo profiles seeded cleanly into database!")


if __name__ == "__main__":
    seed()
