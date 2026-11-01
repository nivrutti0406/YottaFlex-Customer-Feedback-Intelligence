# YottaFlex Customer Feedback Intelligence

A reproducible synthetic-data and feedback-intelligence platform developed for the **YottaFlex.ai Round 2 Challenge**.

The platform generates synthetic customer feedback across surveys, product reviews, and support messages. It stores structured data in SQLite, validates data quality, detects injected anomalies, evaluates detection performance, and exports data in multiple formats.

## 1. Project Overview

The system processes three major feedback sources:

- Survey Responses
- Product Reviews
- Customer Support Messages

It supports structured feedback storage, theme mapping, sentiment labels, anomaly detection, validation, and traceable data exports.

## 2. Architecture

- **Data Generation:** Deterministic Python generators using a fixed random seed.
- **Storage:** SQLite database with SQLAlchemy ORM.
- **Data Modeling:** Relational schema with primary keys, foreign keys, and feedback-theme relationships.
- **Data Quality:** Duplicate, missing-value, rating, and referential-integrity checks.
- **Anomaly Detection:** Rule-based detection of sentiment contradictions, PII leakage, test-label leakage, duplicate candidates, and invalid-theme candidates.
- **Evaluation:** Precision, recall, and F1-score against separately stored injected-anomaly ground truth.
- **Exports:** CSV, JSON, and SQL database dump.
- **Reproducibility:** Source manifest, validation summary, and SHA-256 checksums.
- **CLI:** Menu-driven command-line interface to run project modules.

## 3. Technology Stack

- Python
- SQLite
- SQLAlchemy
- Pandas
- Faker
- CSV and JSON
- Regular Expressions
- SHA-256

## 4. Dataset Overview

The full dataset contains **70,000 synthetic feedback records**.

| Feedback Source | Records |
|---|---:|
| Survey Responses | 25,000 |
| Product Reviews | 25,000 |
| Support Messages | 20,000 |
| **Total** | **70,000** |

The database also contains master entities such as customers, products, channels, surveys, themes, and sentiment labels.

**Random Seed:** `20261022`

## 5. Database Schema

The project currently includes 13 database tables:

1. customers
2. products
3. channels
4. surveys
5. sentiment_labels
6. themes
7. survey_responses
8. reviews
9. support_messages
10. feedback_theme
11. action_items
12. event_history
13. anomaly_cases

The schema uses relational keys and a feedback-theme bridge table to maintain traceability between feedback records and themes.

## 6. Installation

Clone or extract the project and open its root directory.

Create a virtual environment:

```bash
python -m venv venv
```

Activate it in Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## 7. Run the Project

Initialize the database:

```bash
python -m src.init_db
```

Generate master data:

```bash
python -m src.generate_master
```

Generate feedback data:

```bash
python -m src.generate_feedback
```

Generate support messages:

```bash
python -m src.generate_support
```

## 8. Data Validation

Run:

```bash
python -m src.validate_data
```

The validation module checks:

- Duplicate record IDs
- Invalid ratings
- Missing feedback text
- Invalid customer and product references
- Invalid theme references
- Invalid feedback-theme relationships

The current full dataset passed the implemented validation checks with zero failures.

## 9. Anomaly Detection and Evaluation

Inject controlled test anomalies:

```bash
python -m src.inject_anomalies
```

Detect anomalies:

```bash
python -m src.detect_anomalies
```

Evaluate detection results:

```bash
python -m src.evaluate_anomalies
```

The detector currently checks for:

- Sentiment contradictions
- PII leakage
- Test-label leakage
- Duplicate response candidates
- Invalid theme candidates

The injected ground-truth dataset is kept separate from the detector's input.

**Evaluation note:** Current evaluation metrics are based on five injected test anomalies and should not be interpreted as real-world detection performance.

## 10. Data Export

Export database tables to CSV and JSON:

```bash
python -m src.export_data
```

Export the complete SQLite database as SQL:

```bash
python -m src.export_sql
```

Generated files are stored in the `outputs/` directory.

## 11. Reproducibility and Reports

Generate the source manifest:

```bash
python -m src.generate_manifest
```

Generate the validation summary:

```bash
python -m src.generate_validation_summary
```

Generate SHA-256 checksums:

```bash
python -m src.generate_checksums
```

These files help document dataset provenance, validation results, and export integrity.

## 12. Command-Line Interface

Launch the project menu:

```bash
python -m src.cli
```

The CLI provides options to run data generation, validation, anomaly detection, evaluation, exports, and report-generation modules.

## 13. Privacy and Data Provenance

- All generated feedback is synthetic.
- No real customer support tickets or private customer records are used.
- Ground-truth anomaly labels are maintained separately from detector inputs.
- A fixed random seed supports reproducible data generation.

## 14. Current Project Status

Implemented components include:

- Relational database and 13 tables
- Synthetic generation of 70,000 feedback records
- Data quality validation
- Controlled anomaly injection
- Rule-based anomaly detection
- Ground-truth evaluation
- CSV, JSON, and SQL exports
- Source manifest and validation summary
- SHA-256 checksums
- Command-line interface

Further improvements and challenge-specific requirements should be completed and tested before final submission.

---

**Project:** YottaFlex Customer Feedback Intelligence  
**Challenge:** YottaFlex.ai Round 2  
**Data Type:** Synthetic  
**Random Seed:** 20261022