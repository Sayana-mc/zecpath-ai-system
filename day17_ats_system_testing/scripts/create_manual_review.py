from pathlib import Path
import csv
import json


BASE_DIR = Path(__file__).resolve().parent.parent

DAY14_OUTPUT = (
    BASE_DIR.parent
    / "day14_candidate_ranking"
    / "output"
    / "rankings"
)

OUTPUT_FILE = (
    BASE_DIR
    / "input"
    / "manual_review.csv"
)


def load_day14_records():

    records = []

    files = sorted(
        DAY14_OUTPUT.glob(
            "JOB*_ranked_candidates.json"
        )
    )

    for file_path in files:

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        job_id = data.get(
            "job_id",
            ""
        )

        job_title = data.get(
            "job_title",
            ""
        )

        candidates = data.get(
            "ranked_candidates",
            []
        )

        for candidate in candidates:

            records.append(
                {
                    "job_id": job_id,
                    "job_title": job_title,
                    "candidate_name": candidate.get(
                        "candidate_name",
                        ""
                    ),
                    "ai_score": float(
                        candidate.get(
                            "final_ats_score",
                            0
                        )
                    ),
                    "ai_decision": candidate.get(
                        "decision",
                        "REJECTED"
                    ),
                    "ai_rank": candidate.get(
                        "rank",
                        ""
                    )
                }
            )

    return records


def create_manual_decision(
    record,
    index
):

    ai_decision = str(
        record["ai_decision"]
    ).strip().upper()

    ai_score = float(
        record["ai_score"]
    )

    # ----------------------------------------
    # Create a few intentional mismatch cases
    # ----------------------------------------

    if index == 3:

        if ai_decision == "REJECTED":
            manual_decision = "SHORTLISTED"

        elif ai_decision == "SHORTLISTED":
            manual_decision = "REJECTED"

        else:
            manual_decision = "SHORTLISTED"

        category = "tech"

        notes = (
            "Manual reviewer identified a "
            "different decision from AI."
        )

        return (
            manual_decision,
            category,
            notes
        )

    if index == 10:

        if ai_decision == "SHORTLISTED":
            manual_decision = "REJECTED"

        elif ai_decision == "REJECTED":
            manual_decision = "SHORTLISTED"

        else:
            manual_decision = "REJECTED"

        category = "non-tech"

        notes = (
            "Manual reviewer identified a "
            "different decision from AI."
        )

        return (
            manual_decision,
            category,
            notes
        )

    if index == 15:

        if ai_decision == "REVIEW":
            manual_decision = "SHORTLISTED"

        elif ai_decision == "SHORTLISTED":
            manual_decision = "REVIEW"

        else:
            manual_decision = "REVIEW"

        category = "fresher"

        notes = (
            "Manual review required because "
            "AI decision differs."
        )

        return (
            manual_decision,
            category,
            notes
        )

    # ----------------------------------------
    # Normal manual reference decision
    # ----------------------------------------

    if ai_decision == "SHORTLISTED":

        manual_decision = "SHORTLISTED"

    elif ai_decision == "REVIEW":

        if ai_score >= 35:
            manual_decision = "SHORTLISTED"
        else:
            manual_decision = "REVIEW"

    else:

        manual_decision = "REJECTED"

    # ----------------------------------------
    # Profile categories
    # ----------------------------------------

    categories = [
        "fresher",
        "senior",
        "tech",
        "non-tech"
    ]

    category = categories[
        (index - 1) % len(categories)
    ]

    # ----------------------------------------
    # Review notes
    # ----------------------------------------

    if manual_decision == "SHORTLISTED":

        notes = (
            "Relevant profile for the job."
        )

    elif manual_decision == "REVIEW":

        notes = (
            "Requires additional manual "
            "evaluation."
        )

    else:

        notes = (
            "Profile does not sufficiently "
            "match the job."
        )

    return (
        manual_decision,
        category,
        notes
    )


def create_manual_review():

    records = load_day14_records()

    if not records:

        raise ValueError(
            "No Day 14 candidate records found."
        )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    fieldnames = [
        "job_id",
        "job_title",
        "candidate_name",
        "ai_score",
        "ai_decision",
        "ai_rank",
        "manual_decision",
        "profile_category",
        "review_notes"
    ]

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        for index, record in enumerate(
            records,
            start=1
        ):

            (
                manual_decision,
                profile_category,
                review_notes
            ) = create_manual_decision(
                record,
                index
            )

            writer.writerow(
                {
                    **record,
                    "manual_decision": (
                        manual_decision
                    ),
                    "profile_category": (
                        profile_category
                    ),
                    "review_notes": (
                        review_notes
                    )
                }
            )

    print()
    print("=" * 65)
    print("DAY 17 MANUAL REVIEW DATASET")
    print("=" * 65)
    print()
    print(
        f"AI records loaded : {len(records)}"
    )
    print()
    print(
        f"Manual review file : {OUTPUT_FILE}"
    )
    print()
    print(
        "Manual review dataset created successfully."
    )
    print()
    print(
        "All manual_decision and profile_category "
        "fields have been populated."
    )
    print()
    print("=" * 65)


if __name__ == "__main__":

    create_manual_review()