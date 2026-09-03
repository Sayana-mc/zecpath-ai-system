import json
from pathlib import Path

from pipeline import process_resume


INPUT_DIR = Path("../input")
OUTPUT_DIR = Path("../output")


def process_all_resumes():

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    files = list(INPUT_DIR.glob("*.pdf"))
    files += list(INPUT_DIR.glob("*.docx"))

    results = []

    for file_path in files:

        print(f"Processing: {file_path.name}")

        try:

            result = process_resume(str(file_path))

            output_data = {
                "source_file": file_path.name,
                "file_type": file_path.suffix.lower(),
                "status": "success",
                "raw_text": result["raw_text"],
                "cleaned_text": result["cleaned_text"]
            }

            output_file = OUTPUT_DIR / f"{file_path.stem}.json"

            with open(
                output_file,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    output_data,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

            results.append(output_data)

            print("  SUCCESS")

        except Exception as error:

            print(f"  ERROR: {error}")

            results.append({
                "source_file": file_path.name,
                "status": "failed",
                "error": str(error)
            })

    return results


if __name__ == "__main__":
    process_all_resumes()