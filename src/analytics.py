
import pandas as pd
from sqlalchemy import text

from src.database import engine


def load_combined_feedback():

    query = text("""
        SELECT
            sr.response_id AS feedback_id,
            'Survey' AS source,
            sr.response_text AS feedback_text,
            sr.rating AS rating,
            sr.response_date AS feedback_date,
            c.channel_name AS channel,
            sl.sentiment AS sentiment,
            NULL AS product_name
        FROM survey_responses sr
        LEFT JOIN channels c
            ON sr.channel_id = c.channel_id
        LEFT JOIN sentiment_labels sl
            ON sr.sentiment_id = sl.sentiment_id

        UNION ALL

        SELECT
            r.review_id AS feedback_id,
            'Review' AS source,
            r.review_text AS feedback_text,
            r.rating AS rating,
            r.review_date AS feedback_date,
            c.channel_name AS channel,
            sl.sentiment AS sentiment,
            p.product_name AS product_name
        FROM reviews r
        LEFT JOIN channels c
            ON r.channel_id = c.channel_id
        LEFT JOIN sentiment_labels sl
            ON r.sentiment_id = sl.sentiment_id
        LEFT JOIN products p
            ON r.product_id = p.product_id

        UNION ALL

        SELECT
            sm.message_id AS feedback_id,
            'Support' AS source,
            sm.message_text AS feedback_text,
            NULL AS rating,
            sm.message_date AS feedback_date,
            c.channel_name AS channel,
            sl.sentiment AS sentiment,
            p.product_name AS product_name
        FROM support_messages sm
        LEFT JOIN channels c
            ON sm.channel_id = c.channel_id
        LEFT JOIN sentiment_labels sl
            ON sm.sentiment_id = sl.sentiment_id
        LEFT JOIN products p
            ON sm.product_id = p.product_id
    """)

    with engine.connect() as connection:
        df = pd.read_sql(query, connection)

    return df


def load_product_sentiment():

    query = text("""
        SELECT
            p.product_name,
            sl.sentiment,
            COUNT(*) AS feedback_count
        FROM (
            SELECT product_id, sentiment_id FROM reviews
            UNION ALL
            SELECT product_id, sentiment_id FROM support_messages
        ) f
        LEFT JOIN products p
            ON f.product_id = p.product_id
        LEFT JOIN sentiment_labels sl
            ON f.sentiment_id = sl.sentiment_id
        GROUP BY p.product_name, sl.sentiment
        ORDER BY p.product_name
    """)

    with engine.connect() as connection:
        return pd.read_sql(query, connection)


def load_channel_sentiment():

    query = text("""
        SELECT channel, sentiment, COUNT(*) AS feedback_count
        FROM (
            SELECT
                c.channel_name AS channel,
                sl.sentiment AS sentiment
            FROM survey_responses sr
            LEFT JOIN channels c
                ON sr.channel_id = c.channel_id
            LEFT JOIN sentiment_labels sl
                ON sr.sentiment_id = sl.sentiment_id

            UNION ALL

            SELECT
                c.channel_name,
                sl.sentiment
            FROM reviews r
            LEFT JOIN channels c
                ON r.channel_id = c.channel_id
            LEFT JOIN sentiment_labels sl
                ON r.sentiment_id = sl.sentiment_id

            UNION ALL

            SELECT
                c.channel_name,
                sl.sentiment
            FROM support_messages sm
            LEFT JOIN channels c
                ON sm.channel_id = c.channel_id
            LEFT JOIN sentiment_labels sl
                ON sm.sentiment_id = sl.sentiment_id
        )
        GROUP BY channel, sentiment
        ORDER BY channel
    """)

    with engine.connect() as connection:
        return pd.read_sql(query, connection)


def calculate_csat():

    query = text("""
        SELECT AVG(rating) AS average_rating,
               COUNT(rating) AS rated_feedback
        FROM (
            SELECT rating FROM survey_responses
            UNION ALL
            SELECT rating FROM reviews
        )
    """)

    with engine.connect() as connection:
        result = pd.read_sql(query, connection)

    average = result.loc[0, "average_rating"]
    total = result.loc[0, "rated_feedback"]

    return average, total
