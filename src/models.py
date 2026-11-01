
from datetime import datetime

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text,
    ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship

from src.database import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(String(30), primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True)
    country = Column(String(60))
    created_at = Column(DateTime, default=datetime.utcnow)

    survey_responses = relationship("SurveyResponse", back_populates="customer")
    reviews = relationship("Review", back_populates="customer")
    support_messages = relationship("SupportMessage", back_populates="customer")


class Product(Base):
    __tablename__ = "products"

    product_id = Column(String(30), primary_key=True)
    product_name = Column(String(100), nullable=False)
    category = Column(String(80))
    created_at = Column(DateTime, default=datetime.utcnow)

    reviews = relationship("Review", back_populates="product")
    support_messages = relationship("SupportMessage", back_populates="product")


class Channel(Base):
    __tablename__ = "channels"

    channel_id = Column(String(30), primary_key=True)
    channel_name = Column(String(60), unique=True, nullable=False)

    survey_responses = relationship("SurveyResponse", back_populates="channel")
    reviews = relationship("Review", back_populates="channel")
    support_messages = relationship("SupportMessage", back_populates="channel")


class Survey(Base):
    __tablename__ = "surveys"

    survey_id = Column(String(30), primary_key=True)
    survey_name = Column(String(120), nullable=False)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String(30), default="active")

    responses = relationship("SurveyResponse", back_populates="survey")


class SentimentLabel(Base):
    __tablename__ = "sentiment_labels"

    sentiment_id = Column(String(30), primary_key=True)
    sentiment = Column(String(20), unique=True, nullable=False)
    description = Column(Text)

    survey_responses = relationship("SurveyResponse", back_populates="sentiment_label")
    reviews = relationship("Review", back_populates="sentiment_label")
    support_messages = relationship("SupportMessage", back_populates="sentiment_label")


class Theme(Base):
    __tablename__ = "themes"

    theme_id = Column(String(30), primary_key=True)
    theme_name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    effective_from = Column(DateTime, default=datetime.utcnow)
    effective_to = Column(DateTime)
    status = Column(String(30), default="active")

    feedback_links = relationship("FeedbackTheme", back_populates="theme")
    action_items = relationship("ActionItem", back_populates="theme")


class SurveyResponse(Base):
    __tablename__ = "survey_responses"

    response_id = Column(String(60), primary_key=True)
    survey_id = Column(String(30), ForeignKey("surveys.survey_id"), nullable=False)
    customer_id = Column(String(30), ForeignKey("customers.customer_id"), nullable=False)
    channel_id = Column(String(30), ForeignKey("channels.channel_id"), nullable=False)
    sentiment_id = Column(String(30), ForeignKey("sentiment_labels.sentiment_id"))
    response_text = Column(Text, nullable=False)
    rating = Column(Integer)
    response_date = Column(DateTime, default=datetime.utcnow)

    survey = relationship("Survey", back_populates="responses")
    customer = relationship("Customer", back_populates="survey_responses")
    channel = relationship("Channel", back_populates="survey_responses")
    sentiment_label = relationship("SentimentLabel", back_populates="survey_responses")
    theme_links = relationship("FeedbackTheme", back_populates="survey_response")


class Review(Base):
    __tablename__ = "reviews"

    review_id = Column(String(30), primary_key=True)
    customer_id = Column(String(30), ForeignKey("customers.customer_id"), nullable=False)
    product_id = Column(String(30), ForeignKey("products.product_id"), nullable=False)
    channel_id = Column(String(30), ForeignKey("channels.channel_id"), nullable=False)
    sentiment_id = Column(String(30), ForeignKey("sentiment_labels.sentiment_id"))
    review_text = Column(Text, nullable=False)
    rating = Column(Integer)
    review_date = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")
    channel = relationship("Channel", back_populates="reviews")
    sentiment_label = relationship("SentimentLabel", back_populates="reviews")
    theme_links = relationship("FeedbackTheme", back_populates="review")


class SupportMessage(Base):
    __tablename__ = "support_messages"

    message_id = Column(String(60), primary_key=True)
    ticket_id = Column(String(40), nullable=False)
    customer_id = Column(String(30), ForeignKey("customers.customer_id"), nullable=False)
    product_id = Column(String(30), ForeignKey("products.product_id"))
    channel_id = Column(String(30), ForeignKey("channels.channel_id"), nullable=False)
    sentiment_id = Column(String(30), ForeignKey("sentiment_labels.sentiment_id"))
    message_text = Column(Text, nullable=False)
    message_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(30), default="open")

    customer = relationship("Customer", back_populates="support_messages")
    product = relationship("Product", back_populates="support_messages")
    channel = relationship("Channel", back_populates="support_messages")
    sentiment_label = relationship("SentimentLabel", back_populates="support_messages")
    theme_links = relationship("FeedbackTheme", back_populates="support_message")


class FeedbackTheme(Base):
    __tablename__ = "feedback_theme"

    link_id = Column(Integer, primary_key=True, autoincrement=True)
    response_id = Column(String(60), ForeignKey("survey_responses.response_id"))
    review_id = Column(String(30), ForeignKey("reviews.review_id"))
    message_id = Column(String(60), ForeignKey("support_messages.message_id"))
    theme_id = Column(String(30), ForeignKey("themes.theme_id"), nullable=False)
    confidence = Column(Float, default=1.0)

    __table_args__ = (
        UniqueConstraint("response_id", "theme_id"),
        UniqueConstraint("review_id", "theme_id"),
        UniqueConstraint("message_id", "theme_id"),
    )

    survey_response = relationship("SurveyResponse", back_populates="theme_links")
    review = relationship("Review", back_populates="theme_links")
    support_message = relationship("SupportMessage", back_populates="theme_links")
    theme = relationship("Theme", back_populates="feedback_links")


class ActionItem(Base):
    __tablename__ = "action_items"

    action_id = Column(String(30), primary_key=True)
    theme_id = Column(String(30), ForeignKey("themes.theme_id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    priority = Column(String(20), default="medium")
    status = Column(String(30), default="open")
    created_at = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime)
    completed_at = Column(DateTime)

    theme = relationship("Theme", back_populates="action_items")


class EventHistory(Base):
    __tablename__ = "event_history"

    event_id = Column(Integer, primary_key=True, autoincrement=True)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(60), nullable=False)
    event_type = Column(String(50), nullable=False)
    old_value = Column(Text)
    new_value = Column(Text)
    event_date = Column(DateTime, default=datetime.utcnow)
    changed_by = Column(String(100))


class AnomalyCase(Base):
    __tablename__ = "anomaly_cases"

    anomaly_id = Column(String(30), primary_key=True)
    source_type = Column(String(50), nullable=False)
    source_id = Column(String(60), nullable=False)
    anomaly_type = Column(String(80), nullable=False)
    description = Column(Text)
    severity = Column(String(20), default="medium")
    detected_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(30), default="open")
