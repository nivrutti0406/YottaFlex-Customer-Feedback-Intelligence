
import streamlit as st
import pandas as pd
import plotly.express as px
import uuid

from datetime import datetime, date
from sqlalchemy import inspect, text
from src.database import engine

from src.analytics import (
    load_combined_feedback,
    load_product_sentiment,
    load_channel_sentiment,
    calculate_csat
)


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="YottaFlex | Feedback Intelligence",
    page_icon="📊",
    layout="wide"
)


# ==================================================
# CUSTOM DESIGN
# ==================================================

st.markdown("""
<style>
.main {
    background-color: #f5f7fb;
}
.block-container {
    padding-top: 2rem;
}
[data-testid="stMetric"] {
    background: white;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
}
</style>
""", unsafe_allow_html=True)


# ==================================================
# DATABASE FUNCTIONS
# ==================================================

@st.cache_data(ttl=30)
def get_tables():
    return inspect(engine).get_table_names()


@st.cache_data(ttl=30)
def load_table(table_name):

    if table_name not in get_tables():
        return pd.DataFrame()

    query = text(f'SELECT * FROM "{table_name}"')

    with engine.connect() as connection:
        return pd.read_sql(query, connection)


def find_column(df, candidates):

    for column in candidates:
        if column in df.columns:
            return column

    return None


def get_count(table_name):

    if table_name not in get_tables():
        return 0

    with engine.connect() as connection:
        result = connection.execute(
            text(f'SELECT COUNT(*) FROM "{table_name}"')
        )

        return result.scalar() or 0


def log_event(
    entity_type,
    entity_id,
    event_type,
    old_value,
    new_value,
    changed_by="Reviewer"
):

    with engine.begin() as connection:

        connection.execute(
            text("""
                INSERT INTO event_history (
                    entity_type,
                    entity_id,
                    event_type,
                    old_value,
                    new_value,
                    event_date,
                    changed_by
                )
                VALUES (
                    :entity_type,
                    :entity_id,
                    :event_type,
                    :old_value,
                    :new_value,
                    :event_date,
                    :changed_by
                )
            """),
            {
                "entity_type": entity_type,
                "entity_id": str(entity_id),
                "event_type": event_type,
                "old_value": old_value,
                "new_value": new_value,
                "event_date": datetime.utcnow(),
                "changed_by": changed_by
            }
        )


# ==================================================
# HEADER
# ==================================================

st.title("📊 YottaFlex")

st.subheader(
    "Customer Feedback Intelligence Platform"
)

st.caption(
    "Transforming customer feedback into meaningful business insights."
)

st.divider()


# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.title("YottaFlex Navigation")

page = st.sidebar.radio(
    "Select Module",
    [
        "Overview",
        "Sentiment Analysis",
        "Theme Analysis",
        "Anomaly Detection",
        "Feedback Explorer",
        "Advanced Analytics",
        "Action Items"
    ]
)

if st.sidebar.button("🔄 Refresh Dashboard"):

    st.cache_data.clear()
    st.rerun()


# ==================================================
# LOAD DATA
# ==================================================

tables = get_tables()

survey_df = load_table("survey_responses")
review_df = load_table("reviews")
support_df = load_table("support_messages")
sentiment_df = load_table("sentiment_labels")
theme_df = load_table("themes")
link_df = load_table("feedback_theme")
anomaly_df = load_table("anomaly_cases")


# ==================================================
# 1. OVERVIEW
# ==================================================

if page == "Overview":

    st.header("Business Overview")

    total_surveys = len(survey_df)
    total_reviews = len(review_df)
    total_support = len(support_df)

    total_feedback = (
        total_surveys +
        total_reviews +
        total_support
    )

    total_customers = get_count("customers")
    total_products = get_count("products")
    total_anomalies = len(anomaly_df)

    c1, c2, c3 = st.columns(3)

    c1.metric("Total Feedback", f"{total_feedback:,}")
    c2.metric("Total Customers", f"{total_customers:,}")
    c3.metric("Total Products", f"{total_products:,}")

    c4, c5, c6 = st.columns(3)

    c4.metric("Survey Responses", f"{total_surveys:,}")
    c5.metric("Product Reviews", f"{total_reviews:,}")
    c6.metric("Support Messages", f"{total_support:,}")

    st.divider()

    st.subheader("Feedback Source Distribution")

    source_df = pd.DataFrame({
        "Source": [
            "Survey Responses",
            "Product Reviews",
            "Support Messages"
        ],
        "Records": [
            total_surveys,
            total_reviews,
            total_support
        ]
    })

    fig = px.pie(
        source_df,
        names="Source",
        values="Records",
        hole=0.45,
        title="Feedback by Source"
    )

    st.plotly_chart(fig, width="stretch")

    st.subheader("Anomaly Summary")

    st.metric(
        "Detected Anomalies",
        total_anomalies
    )

    if not anomaly_df.empty:

        st.dataframe(
            anomaly_df,
            width="stretch"
        )

    else:

        st.info("No anomaly records available.")


# ==================================================
# 2. SENTIMENT ANALYSIS
# ==================================================

elif page == "Sentiment Analysis":

    st.header("😊 Sentiment Analysis")

    feedback_frames = []

    for source, df in [
        ("Survey", survey_df),
        ("Review", review_df),
        ("Support", support_df)
    ]:

        if "sentiment_id" in df.columns:

            temp = df[["sentiment_id"]].copy()
            temp["Source"] = source

            feedback_frames.append(temp)

    if feedback_frames and not sentiment_df.empty:

        feedback = pd.concat(
            feedback_frames,
            ignore_index=True
        )

        label_col = find_column(
            sentiment_df,
            [
                "sentiment_name",
                "label",
                "name",
                "sentiment"
            ]
        )

        if "sentiment_id" in sentiment_df.columns and label_col:

            merged = feedback.merge(
                sentiment_df[
                    ["sentiment_id", label_col]
                ],
                on="sentiment_id",
                how="left"
            )

            merged.rename(
                columns={
                    label_col: "Sentiment"
                },
                inplace=True
            )

            counts = (
                merged["Sentiment"]
                .fillna("Unknown")
                .value_counts()
                .reset_index()
            )

            counts.columns = [
                "Sentiment",
                "Records"
            ]

            fig = px.pie(
                counts,
                names="Sentiment",
                values="Records",
                hole=0.4,
                title="Overall Sentiment Distribution"
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )

            st.subheader("Sentiment by Source")

            source_counts = (
                merged.groupby(
                    ["Source", "Sentiment"]
                )
                .size()
                .reset_index(name="Records")
            )

            fig2 = px.bar(
                source_counts,
                x="Source",
                y="Records",
                color="Sentiment",
                barmode="group",
                title="Sentiment Across Feedback Sources"
            )

            st.plotly_chart(
                fig2,
                width="stretch"
            )

            st.dataframe(
                counts,
                width="stretch"
            )

        else:

            st.warning(
                "Could not identify sentiment label columns."
            )

    else:

        st.warning(
            "Sentiment data is not available."
        )


# ==================================================
# 3. THEME ANALYSIS
# ==================================================

elif page == "Theme Analysis":

    st.header("🎯 Customer Feedback Themes")

    theme_id_col = find_column(
        theme_df,
        ["theme_id"]
    )

    theme_name_col = find_column(
        theme_df,
        ["theme_name", "name", "theme"]
    )

    if (
        not link_df.empty
        and not theme_df.empty
        and theme_id_col
        and theme_name_col
        and "theme_id" in link_df.columns
    ):

        merged = link_df.merge(
            theme_df[
                [theme_id_col, theme_name_col]
            ],
            on=theme_id_col,
            how="left"
        )

        counts = (
            merged[theme_name_col]
            .fillna("Unknown")
            .value_counts()
            .reset_index()
        )

        counts.columns = [
            "Theme",
            "Feedback Count"
        ]

        fig = px.bar(
            counts,
            x="Feedback Count",
            y="Theme",
            orientation="h",
            title="Feedback by Theme"
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

        st.dataframe(
            counts,
            width="stretch"
        )

    else:

        st.warning(
            "Theme data could not be mapped."
        )


# ==================================================
# 4. ANOMALY DETECTION
# ==================================================

elif page == "Anomaly Detection":

    st.header("🚨 Anomaly Detection Center")

    st.metric(
        "Total Detected Anomalies",
        len(anomaly_df)
    )

    if not anomaly_df.empty:

        severity_col = find_column(
            anomaly_df,
            ["severity"]
        )

        type_col = find_column(
            anomaly_df,
            ["anomaly_type"]
        )

        if severity_col:

            st.subheader("Anomalies by Severity")

            severity_counts = (
                anomaly_df[severity_col]
                .fillna("Unknown")
                .value_counts()
                .reset_index()
            )

            severity_counts.columns = [
                "Severity",
                "Count"
            ]

            fig = px.bar(
                severity_counts,
                x="Severity",
                y="Count",
                title="Severity Distribution"
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )

        if type_col:

            st.subheader("Anomaly Types")

            st.bar_chart(
                anomaly_df[type_col].value_counts()
            )

        st.divider()

        # HUMAN REVIEW

        st.subheader("📝 Human Review Workflow")

        anomaly_ids = (
            anomaly_df["anomaly_id"]
            .astype(str)
            .tolist()
        )

        selected_id = st.selectbox(
            "Select Anomaly to Review",
            anomaly_ids
        )

        selected = anomaly_df[
            anomaly_df["anomaly_id"].astype(str)
            == selected_id
        ].iloc[0]

        st.write("**Anomaly Details**")

        st.write("Source:", selected["source_type"])
        st.write("Source ID:", selected["source_id"])
        st.write("Anomaly Type:", selected["anomaly_type"])
        st.write("Description:", selected["description"])
        st.write("Severity:", selected["severity"])

        status_options = [
            "open",
            "in_review",
            "resolved"
        ]

        current_status = str(
            selected["status"]
        ).lower()

        if current_status not in status_options:
            current_status = "open"

        new_status = st.selectbox(
            "Review Status",
            status_options,
            index=status_options.index(current_status)
        )

        reviewer_notes = st.text_area(
            "Reviewer Notes",
            placeholder="Write your review observations here..."
        )

        if st.button("Save Review"):

            with engine.begin() as connection:

                connection.execute(
                    text("""
                        UPDATE anomaly_cases
                        SET status = :status
                        WHERE anomaly_id = :anomaly_id
                    """),
                    {
                        "status": new_status,
                        "anomaly_id": selected_id
                    }
                )

                connection.execute(
                    text("""
                        INSERT INTO event_history (
                            entity_type,
                            entity_id,
                            event_type,
                            old_value,
                            new_value,
                            event_date,
                            changed_by
                        )
                        VALUES (
                            :entity_type,
                            :entity_id,
                            :event_type,
                            :old_value,
                            :new_value,
                            :event_date,
                            :changed_by
                        )
                    """),
                    {
                        "entity_type": "anomaly",
                        "entity_id": selected_id,
                        "event_type": "review_update",
                        "old_value": str(selected["status"]),
                        "new_value": (
                            f"status={new_status}\n"
                            f"reviewer_notes={reviewer_notes}"
                        ),
                        "event_date": datetime.utcnow(),
                        "changed_by": "Reviewer"
                    }
                )

            st.success("Review saved successfully!")

            st.cache_data.clear()
            st.rerun()

        st.divider()

        # REVIEW HISTORY

        st.subheader("📜 Review History")

        history_df = load_table("event_history")

        if not history_df.empty:

            history_df = history_df[
                history_df["entity_type"] == "anomaly"
            ]

            if not history_df.empty:

                st.dataframe(
                    history_df.sort_values(
                        "event_id",
                        ascending=False
                    ),
                    width="stretch"
                )

            else:

                st.info(
                    "No anomaly review history available."
                )

        else:

            st.info(
                "No review history available yet."
            )

        st.divider()

        st.subheader("Anomaly Records")

        st.dataframe(
            anomaly_df,
            width="stretch"
        )

        st.download_button(
            "Download Anomaly Report",
            data=anomaly_df.to_csv(index=False),
            file_name="yottaflex_anomaly_report.csv",
            mime="text/csv"
        )

    else:

        st.success("No anomalies detected.")


# ==================================================
# 5. FEEDBACK EXPLORER
# ==================================================

elif page == "Feedback Explorer":

    st.header("🔍 Feedback Explorer")

    source_option = st.selectbox(
        "Select Feedback Source",
        [
            "Survey Responses",
            "Reviews",
            "Support Messages"
        ]
    )

    source_mapping = {
        "Survey Responses": survey_df,
        "Reviews": review_df,
        "Support Messages": support_df
    }

    selected_df = source_mapping[source_option]

    st.write(
        f"Total records: {len(selected_df):,}"
    )

    if not selected_df.empty:

        search_text = st.text_input(
            "Search feedback text"
        )

        text_col = find_column(
            selected_df,
            [
                "response_text",
                "review_text",
                "message_text",
                "feedback_text",
                "comment",
                "text"
            ]
        )

        filtered_df = selected_df.copy()

        if search_text and text_col:

            filtered_df = filtered_df[
                filtered_df[text_col]
                .astype(str)
                .str.contains(
                    search_text,
                    case=False,
                    na=False
                )
            ]

        st.dataframe(
            filtered_df.head(1000),
            width="stretch"
        )

        st.caption(
            "Showing up to 1,000 matching records."
        )

        st.download_button(
            "Download Filtered Feedback",
            data=filtered_df.to_csv(index=False),
            file_name="yottaflex_feedback.csv",
            mime="text/csv"
        )

    else:

        st.info("No feedback records found.")


# ==================================================
# 6. ADVANCED ANALYTICS
# ==================================================

elif page == "Advanced Analytics":

    st.title("Advanced Analytics")

    st.write(
        "Detailed insights from all 70,000 feedback records."
    )

    df = load_combined_feedback()

    product_df = load_product_sentiment()

    channel_df = load_channel_sentiment()

    avg_rating, total_rated = calculate_csat()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Feedback",
        f"{len(df):,}"
    )

    col2.metric(
        "Average Customer Rating",
        f"{avg_rating:.2f}/5"
    )

    col3.metric(
        "Rated Feedback",
        f"{total_rated:,}"
    )

    st.divider()

    # PRODUCT SENTIMENT

    st.subheader(
        "Product-wise Sentiment Analysis"
    )

    if not product_df.empty:

        product_pivot = product_df.pivot(
            index="product_name",
            columns="sentiment",
            values="feedback_count"
        ).fillna(0)

        st.bar_chart(product_pivot)

    else:

        st.info(
            "No product analytics data available."
        )

    st.divider()

    # CHANNEL SENTIMENT

    st.subheader(
        "Channel-wise Sentiment Analysis"
    )

    if not channel_df.empty:

        channel_pivot = channel_df.pivot(
            index="channel",
            columns="sentiment",
            values="feedback_count"
        ).fillna(0)

        st.bar_chart(channel_pivot)

    else:

        st.info(
            "No channel analytics data available."
        )

    st.divider()

    # MONTHLY TREND

    st.subheader(
        "Monthly Feedback Trend"
    )

    if not df.empty:

        df["feedback_date"] = pd.to_datetime(
            df["feedback_date"]
        )

        df["month"] = (
            df["feedback_date"]
            .dt.to_period("M")
            .astype(str)
        )

        monthly_data = (
            df.groupby(
                ["month", "sentiment"]
            )
            .size()
            .reset_index(name="count")
        )

        monthly_pivot = monthly_data.pivot(
            index="month",
            columns="sentiment",
            values="count"
        ).fillna(0)

        st.line_chart(monthly_pivot)

    else:

        st.info(
            "No monthly trend data available."
        )

    st.divider()

    # DOWNLOAD

    st.subheader(
        "Download Analytics Data"
    )

    csv_data = df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Download All Feedback CSV",
        data=csv_data,
        file_name="yottaflex_all_feedback.csv",
        mime="text/csv"
    )


# ==================================================
# 7. ACTION ITEMS
# ==================================================

elif page == "Action Items":

    st.header("📌 Action Items Management")

    action_df = load_table("action_items")

    theme_df = load_table("themes")

    # ----------------------------------------------
    # METRICS
    # ----------------------------------------------

    total_actions = len(action_df)

    if not action_df.empty:

        completed_actions = (
            action_df["status"].astype(str).str.lower()
            == "completed"
        ).sum()

        open_actions = (
            action_df["status"].astype(str).str.lower()
            == "open"
        ).sum()

        in_progress_actions = (
            action_df["status"].astype(str).str.lower()
            == "in_progress"
        ).sum()

    else:

        completed_actions = 0
        open_actions = 0
        in_progress_actions = 0

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Actions", total_actions)
    c2.metric("Open", int(open_actions))
    c3.metric("In Progress", int(in_progress_actions))
    c4.metric("Completed", int(completed_actions))

    st.divider()

    # ----------------------------------------------
    # CREATE ACTION ITEM
    # ----------------------------------------------

    st.subheader("➕ Create New Action Item")

    theme_id_col = find_column(
        theme_df,
        ["theme_id"]
    )

    theme_name_col = find_column(
        theme_df,
        ["theme_name", "name", "theme"]
    )

    if (
        not theme_df.empty
        and theme_id_col
        and theme_name_col
    ):

        theme_options = {}

        for _, row in theme_df.iterrows():

            label = (
                f"{row[theme_name_col]} "
                f"({row[theme_id_col]})"
            )

            theme_options[label] = row[theme_id_col]

        with st.form("create_action_form"):

            selected_theme = st.selectbox(
                "Select Theme",
                list(theme_options.keys())
            )

            action_title = st.text_input(
                "Action Title",
                placeholder="Improve Customer Support"
            )

            action_description = st.text_area(
                "Action Description",
                placeholder="Describe the required improvement..."
            )

            priority = st.selectbox(
                "Priority",
                ["Low", "Medium", "High"]
            )

            due_date = st.date_input(
                "Due Date",
                value=date.today()
            )

            submitted = st.form_submit_button(
                "Create Action Item"
            )

            if submitted:

                if not action_title.strip():

                    st.error(
                        "Action title is required."
                    )

                else:

                    # STRING PRIMARY KEY
                    action_id = (
                        "ACT-" +
                        uuid.uuid4().hex[:12].upper()
                    )

                    selected_theme_id = theme_options[
                        selected_theme
                    ]

                    with engine.begin() as connection:

                        connection.execute(
                            text("""
                                INSERT INTO action_items (
                                    action_id,
                                    theme_id,
                                    title,
                                    description,
                                    priority,
                                    status,
                                    created_at,
                                    due_date,
                                    completed_at
                                )
                                VALUES (
                                    :action_id,
                                    :theme_id,
                                    :title,
                                    :description,
                                    :priority,
                                    :status,
                                    :created_at,
                                    :due_date,
                                    NULL
                                )
                            """),
                            {
                                "action_id": action_id,
                                "theme_id": selected_theme_id,
                                "title": action_title.strip(),
                                "description": action_description.strip(),
                                "priority": priority.lower(),
                                "status": "open",
                                "created_at": datetime.utcnow(),
                                "due_date": datetime.combine(
                                    due_date,
                                    datetime.min.time()
                                )
                            }
                        )

                        connection.execute(
                            text("""
                                INSERT INTO event_history (
                                    entity_type,
                                    entity_id,
                                    event_type,
                                    old_value,
                                    new_value,
                                    event_date,
                                    changed_by
                                )
                                VALUES (
                                    'action_item',
                                    :entity_id,
                                    'created',
                                    NULL,
                                    :new_value,
                                    :event_date,
                                    'Reviewer'
                                )
                            """),
                            {
                                "entity_id": action_id,
                                "new_value": (
                                    f"title={action_title.strip()}; "
                                    f"priority={priority.lower()}; "
                                    "status=open"
                                ),
                                "event_date": datetime.utcnow()
                            }
                        )

                    st.success(
                        f"Action Item {action_id} created successfully!"
                    )

                    st.cache_data.clear()
                    st.rerun()

    else:

        st.warning(
            "Theme data is unavailable or theme columns are missing."
        )

    st.divider()

    # ----------------------------------------------
    # EXISTING ACTION ITEMS
    # ----------------------------------------------

    st.subheader("📋 Existing Action Items")

    action_df = load_table("action_items")

    if not action_df.empty:

        st.dataframe(
            action_df,
            width="stretch"
        )

        selected_action_id = st.selectbox(
            "Select Action Item to Update",
            action_df["action_id"].tolist()
        )

        selected_action = action_df[
            action_df["action_id"] == selected_action_id
        ].iloc[0]

        st.write("**Action Details**")

        st.write(
            "Title:",
            selected_action["title"]
        )

        st.write(
            "Description:",
            selected_action["description"]
        )

        st.write(
            "Priority:",
            selected_action["priority"]
        )

        st.write(
            "Current Status:",
            selected_action["status"]
        )

        status_options = [
            "open",
            "in_progress",
            "completed"
        ]

        current_status = str(
            selected_action["status"]
        ).lower()

        if current_status not in status_options:
            current_status = "open"

        new_status = st.selectbox(
            "Update Status",
            status_options,
            index=status_options.index(current_status)
        )

        if st.button("Save Action Status"):

            old_status = str(
                selected_action["status"]
            )

            completed_at = (
                datetime.utcnow()
                if new_status == "completed"
                else None
            )

            with engine.begin() as connection:

                connection.execute(
                    text("""
                        UPDATE action_items
                        SET status = :status,
                            completed_at = :completed_at
                        WHERE action_id = :action_id
                    """),
                    {
                        "status": new_status,
                        "completed_at": completed_at,
                        "action_id": selected_action_id
                    }
                )

                connection.execute(
                    text("""
                        INSERT INTO event_history (
                            entity_type,
                            entity_id,
                            event_type,
                            old_value,
                            new_value,
                            event_date,
                            changed_by
                        )
                        VALUES (
                            'action_item',
                            :entity_id,
                            'status_updated',
                            :old_value,
                            :new_value,
                            :event_date,
                            'Reviewer'
                        )
                    """),
                    {
                        "entity_id": str(selected_action_id),
                        "old_value": old_status,
                        "new_value": new_status,
                        "event_date": datetime.utcnow()
                    }
                )

            st.success(
                "Action Item status updated!"
            )

            st.cache_data.clear()
            st.rerun()

        st.divider()

        # ------------------------------------------
        # ACTION ITEM HISTORY
        # ------------------------------------------

        st.subheader("📜 Action Item History")

        history_df = load_table("event_history")

        if not history_df.empty:

            action_history = history_df[
                history_df["entity_type"] == "action_item"
            ]

            if not action_history.empty:

                st.dataframe(
                    action_history.sort_values(
                        "event_id",
                        ascending=False
                    ),
                    width="stretch"
                )

            else:

                st.info(
                    "No action item history available."
                )

        else:

            st.info(
                "No event history available."
            )

        st.download_button(
            "Download Action Items CSV",
            data=action_df.to_csv(index=False),
            file_name="yottaflex_action_items.csv",
            mime="text/csv"
        )

    else:

        st.info(
            "No action items created yet. "
            "Create your first action item above."
        )


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "YottaFlex Customer Feedback Intelligence | "
    "Synthetic Dataset | Built with Python, SQLAlchemy, "
    "Streamlit and Plotly"
)
