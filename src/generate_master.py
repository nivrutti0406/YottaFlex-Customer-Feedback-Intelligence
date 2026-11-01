
import random
from datetime import datetime, timedelta

from faker import Faker

from src.database import SessionLocal
from src.models import (
    Customer,
    Product,
    Channel,
    Survey,
    Theme,
    SentimentLabel
)

SEED = 20261022

random.seed(SEED)
fake = Faker()
Faker.seed(SEED)


def generate_master_data():

    db = SessionLocal()

    try:
        # Avoid duplicate master records
        existing = db.query(Customer).count()

        if existing > 0:
            print("Master data already exists!")
            print("Skipping generation to avoid duplicates.")
            return

        print("Generating master data...")

        # 1. Customers
        for i in range(1, 501):
            customer = Customer(
                customer_id=f"CUST-{i:06d}",
                name=fake.name(),
                email=f"customer{i}@example.com",
                country=random.choice([
                    "India", "USA", "UK", "Canada",
                    "Australia", "Germany"
                ])
            )
            db.add(customer)

        # 2. Products
        product_names = [
            "Smartphone X", "Laptop Pro", "Smart Watch",
            "Wireless Earbuds", "Tablet Plus",
            "Bluetooth Speaker", "Gaming Mouse",
            "Keyboard Pro", "Smart TV", "Power Bank"
        ]

        for i, name in enumerate(product_names, start=1):
            db.add(Product(
                product_id=f"PROD-{i:03d}",
                product_name=name,
                category=random.choice([
                    "Electronics", "Accessories",
                    "Computers", "Home Appliances"
                ])
            ))

        # 3. Channels
        channel_names = [
            "Website", "Mobile App", "Email",
            "Social Media", "Customer Support"
        ]

        for i, name in enumerate(channel_names, start=1):
            db.add(Channel(
                channel_id=f"CH-{i:03d}",
                channel_name=name
            ))

        # 4. Surveys
        for i in range(1, 6):
            start = datetime(2026, 1, 1) + timedelta(days=i * 30)

            db.add(Survey(
                survey_id=f"SUR-2026-{i:06d}",
                survey_name=f"Customer Feedback Survey {i}",
                start_date=start,
                end_date=start + timedelta(days=20),
                status="active"
            ))

        # 5. Themes
        theme_names = [
            "Product Quality",
            "Pricing",
            "Delivery",
            "Customer Support",
            "User Experience",
            "Performance",
            "Battery Life",
            "Payment Issues",
            "Product Features",
            "Returns and Refunds"
        ]

        for i, name in enumerate(theme_names, start=1):
            db.add(Theme(
                theme_id=f"THEME-{i:06d}",
                theme_name=name,
                description=f"Customer feedback related to {name}",
                status="active"
            ))

        # 6. Sentiment Labels
        sentiments = [
            ("SENT-001", "positive", "Positive customer feedback"),
            ("SENT-002", "negative", "Negative customer feedback"),
            ("SENT-003", "neutral", "Neutral customer feedback")
        ]

        for sid, name, description in sentiments:
            db.add(SentimentLabel(
                sentiment_id=sid,
                sentiment=name,
                description=description
            ))

        db.commit()

        print("\nMaster data generated successfully!")

        print("Customers:", db.query(Customer).count())
        print("Products:", db.query(Product).count())
        print("Channels:", db.query(Channel).count())
        print("Surveys:", db.query(Survey).count())
        print("Themes:", db.query(Theme).count())
        print("Sentiment Labels:", db.query(SentimentLabel).count())

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    generate_master_data()
