
import re
import csv
from pathlib import Path

from src.database import SessionLocal
from src.models import (
    SurveyResponse,
    Review,
    SupportMessage,
    AnomalyCase,
    SentimentLabel,
    Theme
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

DUPLICATE_FILE = DATA_DIR / "duplicate_response_candidate.csv"
INVALID_THEME_FILE = DATA_DIR / "invalid_theme_candidate.csv"


def detect_anomalies():
    db = SessionLocal()
    detected = []

    try:
                # 1. Sentiment contradiction
        positive = db.query(SentimentLabel).filter_by(
            sentiment="positive"
        ).first()

        reviews = db.query(Review).all()

        negative_phrases = [
            "terrible experience",
            "poor service",
            "bad experience",
            "not helpful",
            "disappointed with",
            "waste of money",
            "worst experience"
        ]

        for review in reviews:
            text = (review.review_text or "").lower()
            first_sentence = text.split(".")[0]

            if positive and review.sentiment_id == positive.sentiment_id:
                if any(phrase in first_sentence for phrase in negative_phrases):
                    detected.append({
                        "feedback_id": review.review_id,
                        "feedback_type": "review",
                        "anomaly_type": "sentiment_contradiction",
                        "severity": "high",
                        "description": "Negative review text has positive sentiment label."
                    })

        # 2. PII leakage
        messages = db.query(SupportMessage).all()

        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
        phone_pattern = r"\b(?:\+91[- ]?)?[6-9]\d{9}\b"

        for message in messages:
            content = message.message_text or ""

            if re.search(email_pattern, content) or re.search(phone_pattern, content):
                detected.append({
                    "feedback_id": message.message_id,
                    "feedback_type": "support_message",
                    "anomaly_type": "pii_leakage",
                    "severity": "high",
                    "description": "Possible email or phone number found."
                })

        # 3. Test label leakage
        responses = db.query(SurveyResponse).all()

        for response in responses:
            content = response.response_text or ""

            if re.search(r"\[TEST_LABEL\s*=", content, re.IGNORECASE):
                detected.append({
                    "feedback_id": response.response_id,
                    "feedback_type": "survey_response",
                    "anomaly_type": "test_label_leakage",
                    "severity": "high",
                    "description": "Test label found inside feedback text."
                })

        # 4. Duplicate response candidate
        if DUPLICATE_FILE.exists():
            with open(DUPLICATE_FILE, "r", encoding="utf-8") as file:
                reader = csv.DictReader(file)

                for row in reader:
                    detected.append({
                        "feedback_id": row.get("response_id", "UNKNOWN"),
                        "feedback_type": "survey_response",
                        "anomaly_type": "duplicate_response",
                        "severity": "medium",
                        "description": "Duplicate response candidate found in staging file."
                    })

        # 5. Invalid theme candidate
        if INVALID_THEME_FILE.exists():
            allowed_themes = {
                theme.theme_name for theme in db.query(Theme).all()
            }

            with open(INVALID_THEME_FILE, "r", encoding="utf-8") as file:
                reader = csv.DictReader(file)

                for row in reader:
                    raw_theme = row.get("raw_theme_label", "")

                    if raw_theme not in allowed_themes:
                        detected.append({
                            "feedback_id": row.get("feedback_id", "UNKNOWN"),
                            "feedback_type": "survey_response",
                            "anomaly_type": "invalid_theme",
                            "severity": "medium",
                            "description": "Theme is outside the approved taxonomy."
                        })

        # 6. Save detected anomalies
        existing = {
            (item.source_id, item.anomaly_type)
            for item in db.query(AnomalyCase).all()
        }

        last_case = (
            db.query(AnomalyCase)
            .order_by(AnomalyCase.anomaly_id.desc())
            .first()
        )

        if last_case and last_case.anomaly_id.startswith("ANOM-"):
            last_number = int(last_case.anomaly_id.split("-")[1])
        else:
            last_number = 0

        saved_count = 0

        for item in detected:
            key = (item["feedback_id"], item["anomaly_type"])

            if key in existing:
                continue

            last_number += 1
            anomaly_id = f"ANOM-{last_number:06d}"

            case = AnomalyCase(
                anomaly_id=anomaly_id,
                source_id=item["feedback_id"],
                source_type=item["feedback_type"],
                anomaly_type=item["anomaly_type"],
                severity=item["severity"],
                description=item["description"],
                status="open"
            )

            db.add(case)
            existing.add(key)
            saved_count += 1

        db.commit()

        print("\nANOMALY DETECTION COMPLETED")
        print("Total detected anomalies:", len(detected))
        print("New anomaly cases saved:", saved_count)

        print("\nDetected anomaly types:")
        for item in detected:
            print("-", item["anomaly_type"], "|", item["feedback_id"])

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    detect_anomalies()
