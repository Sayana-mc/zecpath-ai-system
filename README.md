# Zecpath AI System

## Project Overview

Zecpath AI System is a modular AI development repository designed to support an AI-powered recruitment and hiring ecosystem.

The repository is organized into independent modules for resume processing, ATS scoring, screening, interview intelligence, decision scoring, utilities, data, and testing.

## Project Objectives

- Build a modular AI development environment.
- Support ATS and resume analysis.
- Provide AI-based candidate screening.
- Support interview intelligence processing.
- Provide candidate scoring and decision support.
- Maintain logging and testing structures.
- Follow scalable and maintainable project organization.

## Project Structure

```text
zecpath-ai-system/
│
├── data/
│   └── Input data and sample datasets
│
├── parsers/
│   └── Resume and document parsing modules
│
├── ats_engine/
│   └── ATS scoring and resume matching logic
│
├── screening_ai/
│   └── Candidate screening AI modules
│
├── interview_ai/
│   └── Interview intelligence modules
│
├── scoring/
│   └── Candidate score aggregation and decision logic
│
├── utils/
│   └── Common utilities and logging
│
├── tests/
│   └── Automated test cases
│
├── logs/
│   └── Application log files
│
├── requirements.txt
├── pytest.ini
├── .gitignore
└── README.md