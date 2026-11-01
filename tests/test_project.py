
from src.database import SessionLocal
from src.models import (
    Customer,
    Product,
    SurveyResponse,
    Review,
    SupportMessage,
    Theme,
    FeedbackTheme,
    AnomalyCase
)


def test_master_data_exists():
    db = SessionLocal()
    try:
        assert db.query(Customer).count() > 0
        assert db.query(Product).count() > 0
        assert db.query(Theme).count() > 0
    finally:
        db.close()


def test_feedback_record_counts():
    db = SessionLocal()
    try:
        assert db.query(SurveyResponse).count() == 25000
        assert db.query(Review).count() == 25000
        assert db.query(SupportMessage).count() == 20000
    finally:
        db.close()


def test_feedback_theme_links_exist():
    db = SessionLocal()
    try:
        assert db.query(FeedbackTheme).count() == 70000
    finally:
        db.close()


def test_injected_anomalies_exist():
    db = SessionLocal()
    try:
        assert db.query(AnomalyCase).count() == 5
    finally:
        db.close()
