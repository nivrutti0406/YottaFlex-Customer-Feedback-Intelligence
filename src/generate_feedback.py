
import argparse
import random
from datetime import datetime, timedelta

from faker import Faker
from sqlalchemy import or_

from src.database import SessionLocal
from src.models import (
    Customer, Product, Channel, Survey,
    Theme, SentimentLabel,
    SurveyResponse, Review, FeedbackTheme
)

SEED = 20261022

POSITIVE_TEXT = [
    "Excellent product and great experience.",
    "I am very happy with the quality.",
    "Amazing service. Everything works perfectly.",
    "Very satisfied with my purchase.",
    "Great value for money. Highly recommended."
]

NEGATIVE_TEXT = [
    "Very poor quality. I am disappointed.",
    "The product stopped working after a few days.",
    "Terrible experience. Customer service was not helpful.",
    "Not worth the money. Very frustrating.",
    "I am unhappy with this purchase."
]

NEUTRAL_TEXT = [
    "The product is okay and works as expected.",
    "Average experience. Nothing special.",
    "The product has some good and bad features.",
    "Delivery was normal and the quality is average.",
    "It meets basic expectations."
]


def generate_feedback(scale, seed):

    rng = random.Random(seed)
    fake = Faker()
    fake.seed_instance(seed)

    response_count = 50 if scale == "starter" else 25000
    review_count = 50 if scale == "starter" else 25000

    db = SessionLocal()

    try:
        customers = db.query(Customer).order_by(Customer.customer_id).all()
        products = db.query(Product).order_by(Product.product_id).all()
        channels = db.query(Channel).order_by(Channel.channel_id).all()
        surveys = db.query(Survey).order_by(Survey.survey_id).all()
        themes = db.query(Theme).order_by(Theme.theme_id).all()
        sentiments = {
            item.sentiment: item.sentiment_id
            for item in db.query(SentimentLabel).all()
        }

        if not all([customers, products, channels, surveys, themes]):
            raise ValueError("Master data is missing. Run generate_master first.")

        # Remove previous generated feedback before regeneration
        db.query(FeedbackTheme).filter(
            or_(
                FeedbackTheme.response_id.isnot(None),
                FeedbackTheme.review_id.isnot(None)
            )
        ).delete(synchronize_session=False)

        db.query(SurveyResponse).delete(synchronize_session=False)
        db.query(Review).delete(synchronize_session=False)
        db.commit()

        print("Generating survey responses and reviews...")

        response_records = []
        review_records = []
        theme_links = []

        response_sequences = {s.survey_id: 0 for s in surveys}

        sentiment_names = ["positive", "negative", "neutral"]
        sentiment_weights = [0.45, 0.30, 0.25]

        text_options = {
            "positive": POSITIVE_TEXT,
            "negative": NEGATIVE_TEXT,
            "neutral": NEUTRAL_TEXT
        }

        def make_feedback_text(sentiment):
            base = rng.choice(text_options[sentiment])
            return base + " " + fake.sentence(nb_words=5)

        # Generate Survey Responses
        for i in range(response_count):

            survey = rng.choice(surveys)
            response_sequences[survey.survey_id] += 1

            sentiment = rng.choices(
                sentiment_names,
                weights=sentiment_weights,
                k=1
            )[0]

            response_id = (
                f"RESP-{survey.survey_id}-"
                f"{response_sequences[survey.survey_id]:03d}"
            )

            theme = rng.choice(themes)

            response_records.append(
                SurveyResponse(
                    response_id=response_id,
                    survey_id=survey.survey_id,
                    customer_id=rng.choice(customers).customer_id,
                    channel_id=rng.choice(channels).channel_id,
                    sentiment_id=sentiments[sentiment],
                    response_text=make_feedback_text(sentiment),
                    rating=(
                        rng.randint(4, 5) if sentiment == "positive"
                        else rng.randint(1, 2) if sentiment == "negative"
                        else 3
                    ),
                    response_date=datetime(2026, 1, 1)
                    + timedelta(days=rng.randint(0, 300))
                )
            )

            theme_links.append(
                FeedbackTheme(
                    response_id=response_id,
                    theme_id=theme.theme_id,
                    confidence=round(rng.uniform(0.70, 1.0), 2)
                )
            )

        # Generate Product Reviews
        for i in range(1, review_count + 1):

            sentiment = rng.choices(
                sentiment_names,
                weights=sentiment_weights,
                k=1
            )[0]

            review_id = f"REV-2026-{i:06d}"
            theme = rng.choice(themes)

            review_records.append(
                Review(
                    review_id=review_id,
                    customer_id=rng.choice(customers).customer_id,
                    product_id=rng.choice(products).product_id,
                    channel_id=rng.choice(channels).channel_id,
                    sentiment_id=sentiments[sentiment],
                    review_text=make_feedback_text(sentiment),
                    rating=(
                        rng.randint(4, 5) if sentiment == "positive"
                        else rng.randint(1, 2) if sentiment == "negative"
                        else 3
                    ),
                    review_date=datetime(2026, 1, 1)
                    + timedelta(days=rng.randint(0, 300))
                )
            )

            theme_links.append(
                FeedbackTheme(
                    review_id=review_id,
                    theme_id=theme.theme_id,
                    confidence=round(rng.uniform(0.70, 1.0), 2)
                )
            )

        db.add_all(response_records)
        db.add_all(review_records)
        db.add_all(theme_links)
        db.commit()

        print("\nFeedback data generated successfully!")
        print("Survey Responses:", db.query(SurveyResponse).count())
        print("Reviews:", db.query(Review).count())
        print(
            "Total Feedback:",
            db.query(SurveyResponse).count()
            + db.query(Review).count()
        )
        print("Feedback Theme Links:", db.query(FeedbackTheme).count())

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--scale",
        choices=["starter", "full"],
        default="starter"
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=SEED
    )

    args = parser.parse_args()

    generate_feedback(args.scale, args.seed)
