
import csv
from pathlib import Path

from src.database import SessionLocal
from src.models import (
    SurveyResponse,
    Review,
    SupportMessage,
    SentimentLabel
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

GROUND_TRUTH_FILE = DATA_DIR / "ground_truth_anomalies.csv"


def inject_anomalies():

    if GROUND_TRUTH_FILE.exists():
        print("Anomalies already injected!")
        print("Delete the anomaly files only if you want to reset.")
        return

    db = SessionLocal()

    try:
        DATA_DIR.mkdir(exist_ok=True)

        # Fetch records
        responses = (
            db.query(SurveyResponse)
            .order_by(SurveyResponse.response_id)
            .limit(2)
            .all()
        )

        negative_review = (
            db.query(Review)
            .join(
                SentimentLabel,
                Review.sentiment_id == SentimentLabel.sentiment_id
            )
            .filter(SentimentLabel.sentiment == "negative")
            .first()
        )

        support = (
            db.query(SupportMessage)
            .order_by(SupportMessage.message_id)
            .first()
        )

        positive = db.query(SentimentLabel).filter_by(
            sentiment="positive"
        ).first()

        if len(responses) < 2 or not negative_review or not support or not positive:
            raise ValueError("Required records are missing.")

        # 1. Sentiment contradiction
        negative_review.sentiment_id = positive.sentiment_id

        # 2. PII leakage using fictional test information
        support.message_text += (
            " Contact: test.user@example.com "
            "Phone: +91-9000000001"
        )

        # 3. Test label leakage in model input
        test_response = responses[1]
        test_response.response_text += " [TEST_LABEL=negative]"

        db.commit()

        # 4. Duplicate response candidate in raw staging file
        original = responses[0]

        duplicate_fields = [
            "response_id",
            "survey_id",
            "customer_id",
            "channel_id",
            "sentiment_id",
            "response_text",
            "rating",
            "response_date"
        ]

        duplicate_path = DATA_DIR / "duplicate_response_candidate.csv"

        with open(duplicate_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=duplicate_fields)
            writer.writeheader()
            writer.writerow({
                "response_id": original.response_id,
                "survey_id": original.survey_id,
                "customer_id": original.customer_id,
                "channel_id": original.channel_id,
                "sentiment_id": original.sentiment_id,
                "response_text": original.response_text,
                "rating": original.rating,
                "response_date": original.response_date.isoformat()
            })

        # 5. Invalid theme in raw staging file
        theme_path = DATA_DIR / "invalid_theme_candidate.csv"

        with open(theme_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=["feedback_id", "raw_theme_label"]
            )
            writer.writeheader()
            writer.writerow({
                "feedback_id": original.response_id,
                "raw_theme_label": "Unapproved_Test_Theme"
            })

        # Ground truth is kept separate from model input
        ground_truth = [
            {
                "anomaly_id": "ANOM-001",
                "source_type": "review",
                "source_id": negative_review.review_id,
                "anomaly_type": "sentiment_contradiction",
                "expected_severity": "high"
            },
            {
                "anomaly_id": "ANOM-002",
                "source_type": "support_message",
                "source_id": support.message_id,
                "anomaly_type": "pii_leakage",
                "expected_severity": "high"
            },
            {
                "anomaly_id": "ANOM-003",
                "source_type": "survey_response",
                "source_id": test_response.response_id,
                "anomaly_type": "test_label_leakage",
                "expected_severity": "high"
            },
            {
                "anomaly_id": "ANOM-004",
                "source_type": "survey_response",
                "source_id": original.response_id,
                "anomaly_type": "duplicate_response",
                "expected_severity": "medium"
            },
            {
                "anomaly_id": "ANOM-005",
                "source_type": "survey_response",
                "source_id": original.response_id,
                "anomaly_type": "invalid_theme",
                "expected_severity": "medium"
            }
        ]

        with open(
            GROUND_TRUTH_FILE,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "anomaly_id",
                    "source_type",
                    "source_id",
                    "anomaly_type",
                    "expected_severity"
                ]
            )
            writer.writeheader()
            writer.writerows(ground_truth)

        print("\nAnomalies injected successfully!")
        print("Sentiment contradiction: 1")
        print("PII leakage: 1")
        print("Test label leakage: 1")
        print("Duplicate response candidate: 1")
        print("Invalid theme candidate: 1")
        print("Ground truth labels: 5")
        print("\nGround truth saved separately.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    inject_anomalies()
