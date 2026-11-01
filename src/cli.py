
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

COMMANDS = {
    "1": ("Generate Master Data", "src.generate_master"),
    "2": ("Generate Feedback Data", "src.generate_feedback"),
    "3": ("Generate Support Messages", "src.generate_support"),
    "4": ("Validate Data", "src.validate_data"),
    "5": ("Detect Anomalies", "src.detect_anomalies"),
    "6": ("Evaluate Anomalies", "src.evaluate_anomalies"),
    "7": ("Export CSV and JSON", "src.export_data"),
    "8": ("Export SQL", "src.export_sql"),
    "9": ("Generate Source Manifest", "src.generate_manifest"),
    "10": ("Generate Validation Summary", "src.generate_validation_summary"),
    "11": ("Generate Checksums", "src.generate_checksums"),
}


def show_menu():
    print("\n" + "=" * 45)
    print("   YOTTAFLEX FEEDBACK INTELLIGENCE CLI")
    print("=" * 45)

    for number, (label, _) in COMMANDS.items():
        print(f"{number}. {label}")

    print("0. Exit")
    print("=" * 45)


def main():
    while True:
        show_menu()
        choice = input("Enter your choice: ").strip()

        if choice == "0":
            print("Exiting CLI. Goodbye!")
            break

        if choice not in COMMANDS:
            print("Invalid choice. Please try again.")
            continue

        label, module = COMMANDS[choice]

        print(f"\nRunning: {label}")
        result = subprocess.run(
            [sys.executable, "-m", module],
            cwd=BASE_DIR
        )

        if result.returncode == 0:
            print(f"\n{label} completed successfully!")
        else:
            print(f"\n{label} failed. Check the error above.")


if __name__ == "__main__":
    main()
