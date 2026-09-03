import json
from pathlib import Path

from jd_parser import create_ai_jd_profile


BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "input" / "job_descriptions.json"
OUTPUT_DIR = BASE_DIR / "output"


def load_job_descriptions():

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    return data.get("job_descriptions", [])


def save_profile(profile):

    job_id = profile["job_id"]

    title = profile["role"]["title"]

    safe_title = (
        title
        .lower()
        .replace("/", "_")
        .replace(" ", "_")
    )

    output_file = (
        OUTPUT_DIR /
        f"{job_id}_{safe_title}.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            profile,
            file,
            indent=4,
            ensure_ascii=False
        )

    return output_file


def process_all_jds():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    job_descriptions = load_job_descriptions()

    results = []

    print(
        f"Found {len(job_descriptions)} job descriptions."
    )

    for jd in job_descriptions:

        print(
            f"Processing: "
            f"{jd.get('job_id')} - "
            f"{jd.get('job_title')}"
        )

        try:

            profile = create_ai_jd_profile(jd)

            output_file = save_profile(profile)

            results.append(profile)

            print(
                f"  SUCCESS -> {output_file.name}"
            )

        except Exception as error:

            print(
                f"  ERROR -> {error}"
            )

    return results


if __name__ == "__main__":

    process_all_jds()