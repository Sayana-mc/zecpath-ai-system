TEST_CASES = [
    {
        "id": "TC001",
        "question_id": "Q_SKILLS",
        "question": "What technical skills do you have?",
        "answer": "I have experience with Python, SQL, Excel and Power BI.",
        "expected_intent": "skills",
        "human_expected_status": "valid"
    },
    {
        "id": "TC002",
        "question_id": "Q_EXPERIENCE",
        "question": "Tell me about your experience.",
        "answer": "I have 1 year of experience including a 6 month data analyst internship.",
        "expected_intent": "experience",
        "human_expected_status": "valid"
    },
    {
        "id": "TC003",
        "question_id": "Q_AVAILABILITY",
        "question": "When can you join?",
        "answer": "I am available to join immediately.",
        "expected_intent": "availability",
        "human_expected_status": "valid"
    },
    {
        "id": "TC004",
        "question_id": "Q_SALARY",
        "question": "What is your salary expectation?",
        "answer": "I am expecting around 4 LPA.",
        "expected_intent": "salary_expectation",
        "human_expected_status": "valid"
    },
    {
        "id": "TC005",
        "question_id": "Q_SKILLS",
        "question": "What technical skills do you have?",
        "answer": "I don't know.",
        "expected_intent": "skills",
        "human_expected_status": "vague"
    },
    {
        "id": "TC006",
        "question_id": "Q_EXPERIENCE",
        "question": "Tell me about your experience.",
        "answer": "I like watching movies and playing games.",
        "expected_intent": "experience",
        "human_expected_status": "off_topic"
    }
]