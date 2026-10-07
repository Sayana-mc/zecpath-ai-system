class InterviewEvaluator:

    def evaluate_response(self, response):
        text = response.strip()

        if not text:
            return {
                "relevance": 0,
                "communication": 0,
                "confidence": 0,
                "consistency": 0
            }

        length = len(text.split())

        if length >= 15:
            relevance = 90
            communication = 90
            confidence = 88
            consistency = 90

        elif length >= 8:
            relevance = 80
            communication = 80
            confidence = 78
            consistency = 80

        else:
            relevance = 65
            communication = 65
            confidence = 60
            consistency = 65

        return {
            "relevance": relevance,
            "communication": communication,
            "confidence": confidence,
            "consistency": consistency
        }