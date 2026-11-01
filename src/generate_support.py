
import argparse
import random
from datetime import datetime, timedelta

from faker import Faker

from src.database import SessionLocal
from src.models import (
    Customer, Product, Channel, Theme,
    SentimentLabel, SupportMessage, FeedbackTheme
)

SEED = 20261022

POSITIVE_MESSAGES = [
    "Thank you for resolving my issue quickly.",
    "The support team was very helpful.",
    "I am satisfied with the assistance.",
    "My problem is solved. Great service!"
]

NEGATIVE_MESSAGES = [
    "My issue is still not resolved.",
    "I have contacted support multiple times.",
    "The response was very slow.",
    "I am disappointed with customer support."
]

NEUTRAL_MESSAGES = [
    "I need help understanding this feature.",
    "Please provide more information.",
    "I want an update about my request.",
    "I have a question about my product."
]


def generate_support(scale, seed):

    rng = random.Random(seed)
    fake = Faker()
    fake.seed_instance(seed)

    count = 100 if scale == "starter" else 20000

    db = SessionLocal()

    try:
        customers = db.query(Customer).order_by(Customer.customer_id).all()
        products = db.query(Product).order_by(Product.product_id).all()
        channels = db.query(Channel).order_by(Channel.channel_id).all()
        themes = db.query(Theme).order_by(Theme.theme_id).all()

        sentiments = {
            item.sentiment: item.sentiment_id
            for item in db.query(SentimentLabel).all()
        }

        if not all([customers, products, channels, themes]):
            raise ValueError("Master data missing. Run generate_master first.")

        # Remove old support messages and their theme mappings
        db.query(FeedbackTheme).filter(
            FeedbackTheme.message_id.isnot(None)
        ).delete(synchronize_session=False)

        db.query(SupportMessage).delete(synchronize_session=False)
        db.commit()

        print("Generating support messages...")

        records = []
        theme_links = []

        sentiment_names = ["positive", "negative", "neutral"]
        weights = [0.45, 0.30, 0.25]

        message_options = {
            "positive": POSITIVE_MESSAGES,
            "negative": NEGATIVE_MESSAGES,
            "neutral": NEUTRAL_MESSAGES
        }

        for i in range(1, count + 1):

            ticket_id = f"TKT-2026-{i:06d}"
            message_id = f"MSG-{ticket_id}-001"

            sentiment = rng.choices(
                sentiment_names,
                weights=weights,
                k=1
            )[0]

            message = rng.choice(message_options[sentiment])
            message += " " + fake.sentence(nb_words=5)

            theme = rng.choice(themes)

            records.append(
                SupportMessage(
                    message_id=message_id,
                    ticket_id=ticket_id,
                    customer_id=rng.choice(customers).customer_id,
                    product_id=rng.choice(products).product_id,
                    channel_id=rng.choice(channels).channel_id,
                    sentiment_id=sentiments[sentiment],
                    message_text=message,
                    message_date=datetime(2026, 1, 1)
                    + timedelta(days=rng.randint(0, 300)),
                    status=rng.choice(["open", "in_progress", "resolved"])
                )
            )

            theme_links.append(
                FeedbackTheme(
                    message_id=message_id,
                    theme_id=theme.theme_id,
                    confidence=round(rng.uniform(0.70, 1.0), 2)
                )
            )

        db.add_all(records)
        db.add_all(theme_links)
        db.commit()

        print("\nSupport messages generated successfully!")
        print("Support Messages:", db.query(SupportMessage).count())
        print("Unique Tickets:", db.query(
            SupportMessage.ticket_id
        ).distinct().count())
        print("Support Theme Links:", db.query(
            FeedbackTheme
        ).filter(FeedbackTheme.message_id.isnot(None)).count())

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

    generate_support(args.scale, args.seed)
