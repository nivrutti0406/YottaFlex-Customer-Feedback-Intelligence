
from sqlalchemy import text
from src.database import engine


def validate_data():

    checks = {
        "Survey Responses": """
            SELECT COUNT(*) FROM survey_responses
        """,
        "Reviews": """
            SELECT COUNT(*) FROM reviews
        """,
        "Support Messages": """
            SELECT COUNT(*) FROM support_messages
        """,
        "Duplicate Response IDs": """
            SELECT COUNT(*) FROM (
                SELECT response_id
                FROM survey_responses
                GROUP BY response_id
                HAVING COUNT(*) > 1
            )
        """,
        "Duplicate Review IDs": """
            SELECT COUNT(*) FROM (
                SELECT review_id
                FROM reviews
                GROUP BY review_id
                HAVING COUNT(*) > 1
            )
        """,
        "Duplicate Message IDs": """
            SELECT COUNT(*) FROM (
                SELECT message_id
                FROM support_messages
                GROUP BY message_id
                HAVING COUNT(*) > 1
            )
        """,
        "Invalid Ratings": """
            SELECT
                (SELECT COUNT(*) FROM survey_responses
                 WHERE rating IS NULL OR rating < 1 OR rating > 5)
                +
                (SELECT COUNT(*) FROM reviews
                 WHERE rating IS NULL OR rating < 1 OR rating > 5)
        """,
        "Missing Feedback Text": """
            SELECT
                (SELECT COUNT(*) FROM survey_responses
                 WHERE response_text IS NULL OR TRIM(response_text) = '')
                +
                (SELECT COUNT(*) FROM reviews
                 WHERE review_text IS NULL OR TRIM(review_text) = '')
                +
                (SELECT COUNT(*) FROM support_messages
                 WHERE message_text IS NULL OR TRIM(message_text) = '')
        """,
        "Invalid Survey Customer References": """
            SELECT COUNT(*)
            FROM survey_responses s
            LEFT JOIN customers c ON s.customer_id = c.customer_id
            WHERE c.customer_id IS NULL
        """,
        "Invalid Review Product References": """
            SELECT COUNT(*)
            FROM reviews r
            LEFT JOIN products p ON r.product_id = p.product_id
            WHERE p.product_id IS NULL
        """,
        "Invalid Support Customer References": """
            SELECT COUNT(*)
            FROM support_messages m
            LEFT JOIN customers c ON m.customer_id = c.customer_id
            WHERE c.customer_id IS NULL
        """,
        "Invalid Theme References": """
            SELECT COUNT(*)
            FROM feedback_theme f
            LEFT JOIN themes t ON f.theme_id = t.theme_id
            WHERE t.theme_id IS NULL
        """,
        "Invalid Feedback Theme Links": """
            SELECT COUNT(*)
            FROM feedback_theme
            WHERE
                (CASE WHEN response_id IS NOT NULL THEN 1 ELSE 0 END
                + CASE WHEN review_id IS NOT NULL THEN 1 ELSE 0 END
                + CASE WHEN message_id IS NOT NULL THEN 1 ELSE 0 END) != 1
        """
    }

    total_feedback = 0
    failed_checks = 0

    print("\nYOTTAFLEX DATA QUALITY REPORT")
    print("=" * 55)

    with engine.connect() as connection:

        for name, query in checks.items():

            result = connection.execute(text(query)).scalar()

            print(f"{name}: {result}")

            if name in [
                "Survey Responses",
                "Reviews",
                "Support Messages"
            ]:
                total_feedback += result

            elif result != 0:
                failed_checks += 1

    print("=" * 55)
    print("Total Feedback Records:", total_feedback)
    print("Failed Validation Checks:", failed_checks)

    if failed_checks == 0:
        print("DATA QUALITY VALIDATION PASSED!")
    else:
        print("DATA QUALITY VALIDATION FAILED!")


if __name__ == "__main__":
    validate_data()
