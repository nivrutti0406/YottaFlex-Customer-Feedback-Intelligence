
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "outputs"

CHECKSUM_FILE = OUTPUT_DIR / "checksums.json"


def calculate_checksum(file_path):
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def generate_checksums():
    files_data = []

    for file_path in sorted(OUTPUT_DIR.rglob("*")):
        if not file_path.is_file():
            continue

        if file_path == CHECKSUM_FILE:
            continue

        relative_path = file_path.relative_to(BASE_DIR)

        files_data.append({
            "file_name": str(relative_path),
            "file_size_bytes": file_path.stat().st_size,
            "sha256": calculate_checksum(file_path)
        })

    result = {
        "project": "YottaFlex Feedback Intelligence",
        "algorithm": "SHA-256",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "total_files": len(files_data),
        "files": files_data
    }

    with open(CHECKSUM_FILE, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=4)

    print("CHECKSUM GENERATION COMPLETED")
    print("Total files:", len(files_data))
    print("Checksum file:", CHECKSUM_FILE)


if __name__ == "__main__":
    generate_checksums()
