-- YottaFlex Database Schema
-- Generated from SQLAlchemy ORM Models


CREATE TABLE anomaly_cases (
	anomaly_id VARCHAR(30) NOT NULL, 
	source_type VARCHAR(50) NOT NULL, 
	source_id VARCHAR(60) NOT NULL, 
	anomaly_type VARCHAR(80) NOT NULL, 
	description TEXT, 
	severity VARCHAR(20), 
	detected_at DATETIME, 
	status VARCHAR(30), 
	PRIMARY KEY (anomaly_id)
)

;


CREATE TABLE channels (
	channel_id VARCHAR(30) NOT NULL, 
	channel_name VARCHAR(60) NOT NULL, 
	PRIMARY KEY (channel_id), 
	UNIQUE (channel_name)
)

;


CREATE TABLE customers (
	customer_id VARCHAR(30) NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	email VARCHAR(150), 
	country VARCHAR(60), 
	created_at DATETIME, 
	PRIMARY KEY (customer_id), 
	UNIQUE (email)
)

;


CREATE TABLE event_history (
	event_id INTEGER NOT NULL, 
	entity_type VARCHAR(50) NOT NULL, 
	entity_id VARCHAR(60) NOT NULL, 
	event_type VARCHAR(50) NOT NULL, 
	old_value TEXT, 
	new_value TEXT, 
	event_date DATETIME, 
	changed_by VARCHAR(100), 
	PRIMARY KEY (event_id)
)

;


CREATE TABLE products (
	product_id VARCHAR(30) NOT NULL, 
	product_name VARCHAR(100) NOT NULL, 
	category VARCHAR(80), 
	created_at DATETIME, 
	PRIMARY KEY (product_id)
)

;


CREATE TABLE sentiment_labels (
	sentiment_id VARCHAR(30) NOT NULL, 
	sentiment VARCHAR(20) NOT NULL, 
	description TEXT, 
	PRIMARY KEY (sentiment_id), 
	UNIQUE (sentiment)
)

;


CREATE TABLE surveys (
	survey_id VARCHAR(30) NOT NULL, 
	survey_name VARCHAR(120) NOT NULL, 
	start_date DATETIME, 
	end_date DATETIME, 
	status VARCHAR(30), 
	PRIMARY KEY (survey_id)
)

;


CREATE TABLE themes (
	theme_id VARCHAR(30) NOT NULL, 
	theme_name VARCHAR(100) NOT NULL, 
	description TEXT, 
	effective_from DATETIME, 
	effective_to DATETIME, 
	status VARCHAR(30), 
	PRIMARY KEY (theme_id), 
	UNIQUE (theme_name)
)

;


CREATE TABLE action_items (
	action_id VARCHAR(30) NOT NULL, 
	theme_id VARCHAR(30) NOT NULL, 
	title VARCHAR(200) NOT NULL, 
	description TEXT, 
	priority VARCHAR(20), 
	status VARCHAR(30), 
	created_at DATETIME, 
	due_date DATETIME, 
	completed_at DATETIME, 
	PRIMARY KEY (action_id), 
	FOREIGN KEY(theme_id) REFERENCES themes (theme_id)
)

;


CREATE TABLE reviews (
	review_id VARCHAR(30) NOT NULL, 
	customer_id VARCHAR(30) NOT NULL, 
	product_id VARCHAR(30) NOT NULL, 
	channel_id VARCHAR(30) NOT NULL, 
	sentiment_id VARCHAR(30), 
	review_text TEXT NOT NULL, 
	rating INTEGER, 
	review_date DATETIME, 
	PRIMARY KEY (review_id), 
	FOREIGN KEY(customer_id) REFERENCES customers (customer_id), 
	FOREIGN KEY(product_id) REFERENCES products (product_id), 
	FOREIGN KEY(channel_id) REFERENCES channels (channel_id), 
	FOREIGN KEY(sentiment_id) REFERENCES sentiment_labels (sentiment_id)
)

;


CREATE TABLE support_messages (
	message_id VARCHAR(60) NOT NULL, 
	ticket_id VARCHAR(40) NOT NULL, 
	customer_id VARCHAR(30) NOT NULL, 
	product_id VARCHAR(30), 
	channel_id VARCHAR(30) NOT NULL, 
	sentiment_id VARCHAR(30), 
	message_text TEXT NOT NULL, 
	message_date DATETIME, 
	status VARCHAR(30), 
	PRIMARY KEY (message_id), 
	FOREIGN KEY(customer_id) REFERENCES customers (customer_id), 
	FOREIGN KEY(product_id) REFERENCES products (product_id), 
	FOREIGN KEY(channel_id) REFERENCES channels (channel_id), 
	FOREIGN KEY(sentiment_id) REFERENCES sentiment_labels (sentiment_id)
)

;


CREATE TABLE survey_responses (
	response_id VARCHAR(60) NOT NULL, 
	survey_id VARCHAR(30) NOT NULL, 
	customer_id VARCHAR(30) NOT NULL, 
	channel_id VARCHAR(30) NOT NULL, 
	sentiment_id VARCHAR(30), 
	response_text TEXT NOT NULL, 
	rating INTEGER, 
	response_date DATETIME, 
	PRIMARY KEY (response_id), 
	FOREIGN KEY(survey_id) REFERENCES surveys (survey_id), 
	FOREIGN KEY(customer_id) REFERENCES customers (customer_id), 
	FOREIGN KEY(channel_id) REFERENCES channels (channel_id), 
	FOREIGN KEY(sentiment_id) REFERENCES sentiment_labels (sentiment_id)
)

;


CREATE TABLE feedback_theme (
	link_id INTEGER NOT NULL, 
	response_id VARCHAR(60), 
	review_id VARCHAR(30), 
	message_id VARCHAR(60), 
	theme_id VARCHAR(30) NOT NULL, 
	confidence FLOAT, 
	PRIMARY KEY (link_id), 
	UNIQUE (response_id, theme_id), 
	UNIQUE (review_id, theme_id), 
	UNIQUE (message_id, theme_id), 
	FOREIGN KEY(response_id) REFERENCES survey_responses (response_id), 
	FOREIGN KEY(review_id) REFERENCES reviews (review_id), 
	FOREIGN KEY(message_id) REFERENCES support_messages (message_id), 
	FOREIGN KEY(theme_id) REFERENCES themes (theme_id)
)

;

