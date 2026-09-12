class EligibilityDecisionEngine:

    def __init__(self, rules):
        self.rules = rules

    def evaluate_candidate(self, candidate, job_title):

        # Check whether rules exist for this job
        if job_title not in self.rules:
            return {
                "status": "REVIEW",
                "reason": "No eligibility rules configured for this job"
            }

        job_rules = self.rules[job_title]

        # --------------------------------
        # 1. ATS SCORE
        # --------------------------------

        ats_score = candidate.get("ats_score", 0)

        minimum_score = job_rules.get(
            "minimum_ats_score",
            0
        )

        if ats_score < minimum_score:

            return {
                "status": "REJECTED",
                "reason": "ATS score below minimum threshold",
                "failed_rule": "minimum_ats_score"
            }

        # --------------------------------
        # 2. MANDATORY SKILLS
        # --------------------------------

        candidate_skills = {
            skill.lower().strip()
            for skill in candidate.get("skills", [])
        }

        required_skills = {
            skill.lower().strip()
            for skill in job_rules.get(
                "mandatory_skills",
                []
            )
        }

        missing_skills = required_skills - candidate_skills

        if missing_skills:

            return {
                "status": "REVIEW",
                "reason": "Mandatory skills missing",
                "failed_rule": "mandatory_skills",
                "missing_skills": sorted(
                    list(missing_skills)
                )
            }

        # --------------------------------
        # 3. EXPERIENCE
        # --------------------------------

        experience = candidate.get(
            "experience_years",
            0
        )

        minimum_experience = job_rules.get(
            "minimum_experience",
            0
        )

        maximum_experience = job_rules.get(
            "maximum_experience"
        )

        if experience < minimum_experience:

            return {
                "status": "REJECTED",
                "reason": "Experience below minimum requirement",
                "failed_rule": "experience"
            }

        if (
            maximum_experience is not None
            and experience > maximum_experience
        ):

            return {
                "status": "REVIEW",
                "reason": "Experience above configured range",
                "failed_rule": "experience"
            }

        # --------------------------------
        # 4. LOCATION
        # --------------------------------

        location = candidate.get(
            "location",
            ""
        ).lower().strip()

        allowed_locations = [
            item.lower().strip()
            for item in job_rules.get(
                "allowed_locations",
                []
            )
        ]

        if allowed_locations:

            if location not in allowed_locations:

                return {
                    "status": "REVIEW",
                    "reason": "Location does not match configured constraints",
                    "failed_rule": "location"
                }

        # --------------------------------
        # ALL RULES PASSED
        # --------------------------------

        return {
            "status": "ELIGIBLE",
            "reason": "Candidate passed all eligibility rules"
        }