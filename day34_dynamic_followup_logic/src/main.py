import json
from pathlib import Path

from followup_engine import FollowUpEngine
from adaptive_questioning import AdaptiveQuestioning
from decision_tree import FollowUpDecisionTree


def main():

    print("=" * 60)
    print("DAY 34 - DYNAMIC FOLLOW-UP LOGIC")
    print("=" * 60)

    followup_engine = FollowUpEngine()
    adaptive_engine = AdaptiveQuestioning()
    decision_tree = FollowUpDecisionTree()

    conversations = [
        {
            "question_id": "Q001",
            "question": "What are your strengths?",
            "response": "I am hardworking.",
            "confidence": "normal",
            "repeated": False
        },
        {
            "question_id": "Q002",
            "question": "Tell me about a project you worked on.",
            "response": "I don't know.",
            "confidence": "low",
            "repeated": False
        },
        {
            "question_id": "Q003",
            "question": "How do you handle teamwork?",
            "response": (
                "I communicate with team members, divide tasks, "
                "track progress and help solve problems when required."
            ),
            "confidence": "high",
            "repeated": False
        },
        {
            "question_id": "Q004",
            "question": "What are your career goals?",
            "response": "I want to grow in my career.",
            "confidence": "normal",
            "repeated": False
        }
    ]

    results = []

    for item in conversations:

        quality = followup_engine.detect_response_quality(
            item["response"]
        )

        followup = followup_engine.generate_followup(
            item["question_id"],
            item["question"],
            item["response"],
            item["confidence"]
        )

        level = adaptive_engine.determine_level(
            item["response"],
            item["confidence"]
        )

        adaptive_question = adaptive_engine.create_question(
            item["question"],
            level
        )

        decision = decision_tree.decide(
            quality,
            item["confidence"],
            item["repeated"]
        )

        result = {
            "question_id": item["question_id"],
            "question": item["question"],
            "response": item["response"],
            "response_quality": quality,
            "confidence": item["confidence"],
            "follow_up": followup,
            "difficulty_level": level,
            "adaptive_question": adaptive_question,
            "decision": decision
        }

        results.append(result)

        print("\nQuestion ID:", item["question_id"])
        print("Response Quality:", quality)
        print("Follow-up Trigger:", followup["trigger"])
        print("Difficulty:", level)
        print("Decision:", decision["action"])

    output = {
        "total_conversations": len(results),
        "results": results
    }

    output_path = (
        Path(__file__).resolve().parents[1]
        / "output"
        / "followup_results.json"
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(output, file, indent=4)

    print("\n" + "=" * 60)
    print("DYNAMIC FOLLOW-UP PROCESS COMPLETED")
    print("Total conversations:", len(results))
    print("Output:", output_path)
    print("=" * 60)


if __name__ == "__main__":
    main()