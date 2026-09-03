def test_pipeline_applies_score_normalization():
    candidates = [
        {
            "candidate_name": "Candidate A",
            "job_id": "JOB001",
            "job_title": "Data Analyst",
            "final_ats_score": 10,
            "breakdown": {
                "skill_match": 0,
            },
        },
        {
            "candidate_name": "Candidate B",
            "job_id": "JOB001",
            "job_title": "Data Analyst",
            "final_ats_score": 50,
            "breakdown": {
                "skill_match": 0,
            },
        },
        {
            "candidate_name": "Candidate C",
            "job_id": "JOB001",
            "job_title": "Data Analyst",
            "final_ats_score": 90,
            "breakdown": {
                "skill_match": 0,
            },
        },
    ]

    config = {
        "score_min": 0,
        "score_max": 100,
        "keyword_weight_limit": 0.35,
        "mask_personal_attributes": True,
        "personal_attributes": [
            "candidate_name"
        ],
    }

    results = process_candidates(
        candidates,
        config,
    )

    scores = [
        candidate["fairness_score"]
        for candidate in results
    ]

    assert scores == [0.0, 50.0, 100.0]