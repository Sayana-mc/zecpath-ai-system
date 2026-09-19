import json
from pathlib import Path
from conversation_flow import ConversationFlow
from decision_tree import ConversationDecisionTree
PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
def main():
    print("Starting Day 29 AI Conversation Flow Design...")
    flow = ConversationFlow()
    decision_tree = ConversationDecisionTree()
    results = []
    # Start conversation
    start_result = flow.start()
    print("\nSTART")
    print(start_result)
    results.append({
        "input": None,
        "result": start_result
    })

    test_responses = [
        "",
        "I don't understand the question.",
        "Python development.",
        "I have two years of experience working with Python and SQL.",
        "I have two years of experience working with Python and SQL."
    ]

    for index, response in enumerate(test_responses, start=1):

        print(f"\nResponse {index}: {response}")

        decision = decision_tree.decide(response)

        result = flow.process_response(response)

        print("Decision:", decision)
        print("Flow Result:", result)

        results.append({
            "response_id": f"R{index:03d}",
            "response": response,
            "decision": decision,
            "flow_result": result
        })

    complete_result = flow.complete()

    print("\nCOMPLETION")
    print(complete_result)

    results.append({
        "result": complete_result
    })

    output_file = OUTPUT_DIR / "conversation_flow_results.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(
            results,
            file,
            indent=4
        )

    print("\nAI conversation flow completed.")
    print(f"Output: {output_file}")


if __name__ == "__main__":
    main()