from __future__ import annotations

import hashlib
import json
from pathlib import Path


class ResumeCache:

    def __init__(self, cache_dir="output/cache"):
        self.cache_dir = Path(cache_dir)

        self.cache_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _cache_key(self, file_path: Path) -> str:

        content = file_path.read_bytes()

        return hashlib.sha256(
            content
        ).hexdigest()

    def get(self, file_path):

        file_path = Path(file_path)

        key = self._cache_key(file_path)

        cache_file = self.cache_dir / f"{key}.json"

        if not cache_file.exists():
            return None

        with open(
            cache_file,
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        return data

    def set(self, file_path, text):

        file_path = Path(file_path)

        key = self._cache_key(file_path)

        cache_file = self.cache_dir / f"{key}.json"

        data = {
            "file": file_path.name,
            "text": text,
        }

        with open(
            cache_file,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                indent=2,
                ensure_ascii=False,
            )


if __name__ == "__main__":

    print("=" * 65)
    print("RESUME CACHE")
    print("=" * 65)

    print("\nCache mechanism initialized.")

    print("Repeated resume processing can now use cached text.")

    print("=" * 65)