
import csv
from pathlib import Path

from src.database import SessionLocal
from src.models import AnomalyCase

BASE_DIR = Path(__file__).resolve().parent.parent
GROUND_TRUTH_FILE = BASE_DIR / "data" / "ground_truth_anomalies.csv"


def evaluate_anomalies():
    db = SessionLocal()

    try:
        with open(GROUND_TRUTH_FILE, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            ground_truth = list(reader)

        detected = db.query(AnomalyCase).all()

        actual = {
            (row["source_id"], row["anomaly_type"])
            for row in ground_truth
        }

        predicted = {
            (row.source_id, row.anomaly_type)
            for row in detected
        }

        true_positive = len(actual & predicted)
        false_positive = len(predicted - actual)
        false_negative = len(actual - predicted)

        precision = (
            true_positive / (true_positive + false_positive)
            if true_positive + false_positive else 0
        )

        recall = (
            true_positive / (true_positive + false_negative)
            if true_positive + false_negative else 0
        )

        f1_score = (
            2 * precision * recall / (precision + recall)
            if precision + recall else 0
        )

        print("\nGROUND TRUTH EVALUATION")
        print("-----------------------")
        print("Actual anomalies:", len(actual))
        print("Detected anomalies:", len(predicted))
        print("True Positives:", true_positive)
        print("False Positives:", false_positive)
        print("False Negatives:", false_negative)
        print("Precision:", round(precision, 4))
        print("Recall:", round(recall, 4))
        print("F1 Score:", round(f1_score, 4))

    finally:
        db.close()


if __name__ == "__main__":
    evaluate_anomalies()
