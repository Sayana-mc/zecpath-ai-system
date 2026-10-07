from pathlib import Path

from .demo_engine import HRInterviewDemo


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "demo_candidates.json"
OUTPUT_FILE = BASE_DIR / "output" / "final_hr_interview_demo.json"


def main():

    print("=" * 60)
    print("DAY 45 - HR INTERVIEW DEMO & FINALIZATION")
    print("=" * 60)

    demo = HRInterviewDemo()

    result = demo.run(
        INPUT_FILE,
        OUTPUT_FILE
    )

    print()
    print(f"Candidates processed : {result['candidate_count']}")
    print("Interview simulation : Completed")
    print("Scoring breakdown     : Generated")
    print("Unified scoring       : Completed")
    print("Hiring recommendation : Generated")
    print("Human review          : Enabled")

    print()
    print("Candidate Results")
    print("-" * 60)

    for candidate in result["results"]:
        print(
            f"{candidate['candidate_id']} | "
            f"{candidate['role']} | "
            f"HR Score: {candidate['interview']['hr_interview_score']} | "
            f"Final Score: {candidate['final_unified_score']} | "
            f"{candidate['final_recommendation']}"
        )

    print()
    print(f"Output: {OUTPUT_FILE}")
    print("Status: DEMO COMPLETED")


if __name__ == "__main__":
    main()