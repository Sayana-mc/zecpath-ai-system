class HRInterviewSimulator:
    """
    Simulates HR interview sessions for different candidate profiles.
    """

    QUESTIONS = [
        {
            "id": "Q001",
            "category": "self_introduction",
            "question": "Tell me about yourself."
        },
        {
            "id": "Q002",
            "category": "career_journey",
            "question": "Tell me about your career journey."
        },
        {
            "id": "Q003",
            "category": "strengths_weaknesses",
            "question": "What are your strengths and weaknesses?"
        },
        {
            "id": "Q004",
            "category": "teamwork",
            "question": "How do you work in a team?"
        },
        {
            "id": "Q005",
            "category": "career_goals",
            "question": "What are your career goals?"
        },
        {
            "id": "Q006",
            "category": "availability",
            "question": "When can you join?"
        }
    ]

    CANDIDATES = {
        "confident": {
            "candidate_id": "C001",
            "name": "Confident Candidate",
            "answers": [
                "I am a data science graduate with strong Python and SQL skills.",
                "I completed internships in data analysis and machine learning.",
                "My strength is problem solving. I am improving my communication skills.",
                "I communicate clearly and collaborate with team members.",
                "I want to grow as an AI and machine learning professional.",
                "I can join immediately."
            ]
        },

        "hesitant": {
            "candidate_id": "C002",
            "name": "Hesitant Candidate",
            "answers": [
                "I am a graduate and I have some technical skills.",
                "I have completed an internship, but I am still learning.",
                "I think communication is one of my strengths.",
                "I can work with a team.",
                "I am not completely sure about my long-term goal.",
                "I may be able to join soon."
            ]
        },

        "inexperienced": {
            "candidate_id": "C003",
            "name": "Inexperienced Candidate",
            "answers": [
                "I recently completed my degree.",
                "I do not have much professional experience.",
                "I am a quick learner.",
                "I have worked on college projects with classmates.",
                "I want to gain professional experience.",
                "I can join immediately."
            ]
        },

        "overqualified": {
            "candidate_id": "C004",
            "name": "Overqualified Candidate",
            "answers": [
                "I have extensive experience in data science and AI.",
                "I have worked on multiple production machine learning projects.",
                "My strengths are leadership, architecture and problem solving.",
                "I have managed cross-functional technical teams.",
                "I am looking for senior leadership opportunities.",
                "I have a short notice period."
            ]
        }
    }

    def simulate(self, candidate_type):
        candidate = self.CANDIDATES[candidate_type]

        responses = []

        for question, answer in zip(
            self.QUESTIONS,
            candidate["answers"]
        ):
            responses.append({
                "question_id": question["id"],
                "category": question["category"],
                "question": question["question"],
                "answer": answer
            })

        return {
            "candidate_id": candidate["candidate_id"],
            "candidate_type": candidate_type,
            "candidate_name": candidate["name"],
            "total_questions": len(responses),
            "responses": responses
        }

    def simulate_all(self):
        results = {}

        for candidate_type in self.CANDIDATES:
            results[candidate_type] = self.simulate(
                candidate_type
            )

        return results