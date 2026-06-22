# Lab 3: Feature Engineering for ML

### 🎯 Why This Lab?

Raw event data isn't directly usable by ML models. **Feature engineering** creates meaningful signals:
- Aggregate events into features (e.g., "kills in past 7 days")
- Handle time windows (7-day, 30-day rolling)
- Create derived features (e.g., K/D ratio)
- Prevent data leakage (use only historical data)

### 📚 Concepts

**Features vs. Raw Events:**
- Raw: Individual events (kill, death, purchase)
- Features: Aggregated signals (kill_count_7d, avg_spend_30d)
- ML models work with features, not raw events

**Time Windows:**
- 7-day window: Last 7 days of activity
- 30-day window: Last 30 days
- Rolling: Updated daily (yesterday's 7-day → today's 7-day)
- Important: Avoid leakage! Only use historical data (no future events)

**Target Variable (Label):**
- For churn model: "Did player churn in next 7 days?" (0/1)
- Churn = no login for 7+ days (business definition)
- Only available after observation period ends

**Feature Store (Optional):**
- Centralized repository of features
- Enables feature reuse across models
- Ensures consistency
- Databricks Feature Store: `databricks.feature_store`

### 🔧 Goal

Create **Gold feature tables** for ML training.

### 📋 Deliverables

- `src/dlt/gold_pipeline.py` — Gold feature engineering DLT pipeline
- `notebooks/dlt/03_feature_engineering_gold.py` — interactive walkthrough
- Gold tables:
  - `churn_features_daily` — features for churn model
  - `arpu_features_daily` — features for revenue model
  - `player_segments` — BI-ready player segments
- Scheduled daily job (runs at 1 AM UTC)

### ☁️ Azure Tasks

- Create Databricks Job (schedule daily 1 AM UTC)
- Use job clusters (cheaper than all-purpose clusters)
- Monitor via Azure Monitor / Databricks UI

### 🔑 Key Terms

- **Feature**: Aggregated signal for ML model (e.g., avg_spend_7d)
- **Time window**: Period of aggregation (7d, 30d, all-time)
- **Data leakage**: Using future data in training (prevents realistic evaluation)
- **Rolling window**: Updated periodically (e.g., daily)
- **Feature store**: Centralized repository for features

### ⏱️ Time: ~1.5 hours

### 📖 Reference

- Feature engineering: [Best practices](https://www.databricks.com/blog/2023/08/29/feature-engineering-best-practices.html)
- Databricks Feature Store: [Docs](https://docs.databricks.com/en/machine-learning/feature-store/)
- Time windows: [Window functions](https://spark.apache.org/docs/latest/sql-ref-window-functions.html)

### Prerequisites: Lab 2

---
