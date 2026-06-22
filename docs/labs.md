# Lives Remaining Labs — Lab Sequence & Instructions

**FICTIONAL COMPANY:** Lives Remaining Labs is a fictional multiplayer game studio created for educational purposes.

**Platform:** Azure Databricks (Premium workspace with Unity Catalog)

## Prerequisites (Azure Setup)

Before starting labs, ensure you have:

1. **Azure subscription** with Databricks, Storage, and Entra permissions
2. **Azure Databricks workspace** (Premium SKU) in your resource group
3. **Azure Data Lake Storage (ADLS Gen2)** created with a blob container
4. **Service Principal** (Entra app registration) with Storage Blob roles
5. **Databricks personal access token (PAT)** for API access
6. **Python 3.9+** installed locally
7. **Azure CLI** authenticated (`az login`)

👉 **[See Azure Setup Guide →](setup-azure.md)** (coming soon)

---

## Lab 0: Setup & Sample Data Generation

### 🎯 Why This Lab?

Before we can build a data pipeline, we need realistic data. This lab generates synthetic player events that mimic real game telemetry: logins, kills, purchases, etc.

### 📚 Concepts

**Synthetic Data Generation:**
- Real production data is sensitive (contains PII)
- Synthetic data lets us practice without privacy concerns
- We use `faker` library to create realistic-looking random data
- Events must match our schema (see `docs/data-schema.md`)

**Data Lake Bronze Ingestion:**
- Raw data lands in cloud storage (unprocessed, as-is)
- Later, we'll transform it in DLT pipelines

### 🔧 Goal

Generate 100,000 synthetic player events and upload to Azure Blob Storage (raw format).

### 📋 Deliverables

- `data/raw_events.csv` (100k sample player events)
- `data/event_schema.json` (schema documentation)
- CSV uploaded to Azure Blob Storage (`abfss://datalake@lrlstorage.dfs.core.windows.net/events/`)

### ☁️ Azure Tasks

1. Create blob container `events/` in ADLS Gen2
2. Use `azcopy` or Azure CLI to upload CSV:
   ```bash
   azcopy copy "data/raw_events.csv" \
     "https://lrlstorage.blob.core.windows.net/datalake/events/" \
     --recursive
   ```

### ⏱️ Time: ~30 min

### 📖 Reference

- Schema: `docs/data-schema.md`
- Generator script: `scripts/generate_events.py`

---

## Lab 1: Bronze Ingestion via DLT Autoloader (Azure)

### 🎯 Why This Lab?

Raw data in cloud storage is hard to query. **Delta Live Tables (DLT)** is Databricks' declarative ETL framework that:
- Ingests data reliably into Delta Lake tables
- Handles late arrivals and schema changes (via **Autoloader**)
- Creates lineage & audit trails automatically
- Enables incremental processing (only new files processed)

### 📚 Concepts

**Delta Lake:**
- ACID-compliant data lake format (combines data warehouse + data lake)
- Tables stored as Parquet files + transaction log
- Supports time travel, rollback, schema enforcement
- Why use it? Reliability + performance + governance

**DLT (Delta Live Tables):**
- Declarative framework (you declare *what*, not *how*)
- Automatically handles:
  - Schema inference & evolution
  - Data quality checks (expectations)
  - Idempotent ingestion (safe to re-run)
- Why use it instead of plain PySpark?
  - No need to manage checkpoints manually
  - Lineage tracked automatically
  - Recovery from failures is built-in
  - Code is simpler and more maintainable

**Autoloader:**
- Watches a cloud storage path for new files
- Automatically ingests without manual triggering
- Uses checkpoints to track processed files
- Handles large files, late arrivals, and duplicates

**Service Principal Authentication (Azure):**
- Service principal = app identity (not a human user)
- Databricks uses it to authenticate with ADLS Gen2
- Credentials securely stored in Azure Key Vault
- Jobs can run unattended using service principal

### 🔧 Goal

Ingest raw player events from Azure Blob Storage into a **Bronze Delta table** using DLT Autoloader.

### 📋 Deliverables

- `src/dlt/bronze_pipeline.py` — DLT pipeline code
- `notebooks/dlt/01_ingest_bronze.py` — runnable notebook
- Bronze table `lives_remaining_raw_events` in Unity Catalog
- Autoloader checkpoint stored in ADLS Gen2 (tracks processed files)

### ☁️ Azure Tasks

1. Mount ADLS Gen2 in Databricks cluster using service principal:
   ```python
   dbutils.fs.mount(
     source="abfss://datalake@lrlstorage.dfs.core.windows.net/",
     mount_point="/mnt/data",
     extra_configs={
       "fs.azure.account.auth.type": "OAuth",
       "fs.azure.account.oauth.provider.type": "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider",
       "fs.azure.account.oauth2.client.id": "<service-principal-id>",
       "fs.azure.account.oauth2.client.secret": "<secret>",
       "fs.azure.account.oauth2.client.endpoint": "https://login.microsoftonline.com/<tenant-id>/oauth2/v2.0/token"
     }
   )
   ```

2. Create external location in Unity Catalog (links to ADLS)

3. Set up DLT pipeline in Databricks workspace UI

### 🔑 Key Terms

- **Checkpoint**: File tracking which data has been ingested (prevents reprocessing)
- **Schema inference**: DLT auto-detects column names & types from CSV headers
- **Idempotent**: Safe to run multiple times with same result
- **External location**: UC object pointing to cloud storage
- **Service Principal**: Non-interactive identity for automation

### ⏱️ Time: ~1 hour

### 📖 Reference

- Schema: `docs/data-schema.md`
- DLT docs: [Databricks DLT](https://docs.databricks.com/en/delta-live-tables/)
- Autoloader: [Cloud file ingestion](https://docs.databricks.com/en/ingestion/auto-loader/)

### Prerequisites: Lab 0

---

## Lab 2: Silver Transformations & Quality Checks

### 🎯 Why This Lab?

Bronze data is messy (inconsistent formats, nulls, duplicates). **Silver layer** cleans and normalizes:
- Standardizes types (e.g., date strings → timestamp)
- Deduplicates records
- Applies business logic (e.g., compute session duration)
- Validates data quality with expectations

### 📚 Concepts

**Bronze → Silver → Gold (Medallion Architecture):**
- **Bronze**: Raw, as-is (no guarantees)
- **Silver**: Cleaned, deduplicated (trustworthy)
- **Gold**: Business-ready aggregates (for analytics/ML)
- Why this pattern? Separation of concerns, reusability, auditability

**DLT Expectations (Quality Checks):**
- Expectations are business rules (e.g., "kill_count must be ≥ 0")
- DLT tracks which records pass/fail
- Failed records can be quarantined or rejected
- Provides data quality metrics

**Slowly Changing Dimensions (SCD):**
- Tracks how entity attributes change over time
- Type 1: Overwrite old values (no history)
- Type 2: Keep history (add new rows with dates)
- Used for player profiles (level-ups, tier promotions)

**PySpark Transformations:**
- `withColumn()`: Add/modify column
- `select()`: Project specific columns
- `where()`: Filter rows
- `groupBy().agg()`: Aggregate
- Window functions: `over(Window.partitionBy(...).orderBy(...))`

### 🔧 Goal

Transform Bronze events into clean **Silver tables** with quality checks & aggregations.

### 📋 Deliverables

- `src/dlt/silver_pipeline.py` — transformation code
- Silver tables:
  - `player_sessions` — session-level aggregates
  - `player_events_cleaned` — deduplicated, normalized events
- Quality report (expectations passed/failed)

### ☁️ Azure Tasks

- Monitor cluster metrics in Databricks workspace
- Check job run history & logs
- View expectations results in DLT UI

### 🔑 Key Terms

- **Medallion Architecture**: Bronze → Silver → Gold layering
- **Expectation**: Data quality rule (DLT feature)
- **SCD (Slowly Changing Dimension)**: Temporal tracking of entities
- **Deduplication**: Removing duplicate rows (common in event streams)
- **Window function**: Compute over rows partitioned by key (e.g., avg per player)

### ⏱️ Time: ~1.5 hours

### 📖 Reference

- PySpark: [DataFrame API](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql.DataFrame.html)
- DLT Expectations: [Data quality monitoring](https://docs.databricks.com/en/delta-live-tables/expectations.html)
- Medallion Architecture: [Best practices](https://www.databricks.com/blog/2022/06/24/multi-hop-architecture-is-modular-and-scalable.html)

### Prerequisites: Lab 1

---

## Lab 3: Feature Engineering for ML

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

- `src/jobs/featurize.py` — feature engineering job
- `notebooks/jobs/01_featurize.py` — interactive walkthrough
- Gold tables:
  - `churn_features_daily` — features for churn model
  - `arpu_features_daily` — features for revenue model
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

## Lab 4: Churn Prediction with MLflow

### 🎯 Why This Lab?

Now we have features! **MLflow** is Databricks' ML lifecycle framework:
- Track experiments (hyperparameters, metrics, artifacts)
- Register models in model registry
- Version & promote models (dev → staging → prod)
- Reproducibility: Re-run exact experiments

Why MLflow instead of just sklearn?
- Experiment tracking across team
- Model reproducibility & lineage
- Easy model deployment
- Metric comparison across runs

### 📚 Concepts

**ML Workflow:**
1. Load training data (Gold features + labels)
2. Split: train (70%), test (30%)
3. Train model with hyperparameters
4. Evaluate on test set (accuracy, precision, recall, AUC)
5. Log to MLflow Tracking
6. Register best model in MLflow Model Registry

**Classification Metrics:**
- **Accuracy**: (TP + TN) / total (good overall metric)
- **Precision**: TP / (TP + FP) (when you predict churn, are you right?)
- **Recall**: TP / (TP + FN) (of actual churners, how many did you catch?)
- **F1-score**: Harmonic mean of precision & recall
- **AUC**: Area under ROC curve (0.5 = random, 1.0 = perfect)

**Hyperparameters (for sklearn RandomForest):**
- `max_depth`: How deep trees can grow (prevent overfitting)
- `n_estimators`: Number of trees
- `min_samples_split`: Min samples to split node
- Tuning: Grid search or random search

**Model Registry:**
- Central place to store trained models
- Stages: None → Staging → Production → Archived
- Enables promotion workflow

### 🔧 Goal

Train churn classification model, evaluate, and register in MLflow.

### 📋 Deliverables

- `src/jobs/train.py` — training script
- `notebooks/jobs/02_train_model.py` — interactive notebook
- Trained model registered in MLflow registry (accuracy ~0.85+)
- Experiment runs logged (try 3–5 hyperparameter configs)

### ☁️ Azure Tasks

- View MLflow Tracking UI in Databricks workspace
- Register model in MLflow Model Registry
- Compare metrics across runs

### 🔑 Key Terms

- **Experiment**: Collection of runs (different hyperparameter configs)
- **Run**: Single training job (logs metrics, params, artifacts)
- **MLflow Tracking Server**: Records experiments (default: workspace)
- **Model Registry**: Central repository for production models
- **Hyperparameter**: Tunable config (not learned from data)
- **Train/test split**: Data separation (prevent overfitting on test set)

### ⏱️ Time: ~2 hours

### 📖 Reference

- MLflow: [Documentation](https://mlflow.org/docs/latest/index.html)
- Databricks MLflow: [Workspace integration](https://docs.databricks.com/en/machine-learning/mlflow/index.html)
- Classification metrics: [Scikit-learn docs](https://scikit-learn.org/stable/modules/model_evaluation.html)
- Hyperparameter tuning: [Grid search](https://scikit-learn.org/stable/modules/grid_search.html)

### Prerequisites: Lab 3

---

## Lab 5: Batch Scoring & Predictions

### 🎯 Why This Lab?

Trained model is in registry. Now **deploy it to production** by:
- Loading model from registry
- Scoring all active players daily
- Writing predictions to Delta table
- Scheduling as automated job

Batch vs. real-time scoring:
- **Batch**: Process all players nightly (cheaper, simpler)
- **Real-time**: Score on-demand via API (Lab 7, optional)
- We use batch for daily churn predictions

### 📚 Concepts

**Model Loading from MLflow:**
```python
import mlflow
model = mlflow.pyfunc.load_model("models:/churn_model/Production")
predictions = model.predict(feature_df)
```

**Batch Predictions:**
- Load model once
- Score all rows at once (efficient)
- Write results to Delta table
- Pandas UDF for parallelization (faster)

**Databricks Jobs:**
- Scheduled tasks in Databricks workspace
- Can run notebooks or .py scripts
- Supports job parameters, email alerts, retries
- Pricing: Seconds-based (cheaper than all-purpose clusters)

**Incremental Updates:**
- Don't re-score all history daily (wasteful)
- Only score new/updated players
- Merge results into existing table

### 🔧 Goal

Create daily batch scoring job that scores all players & writes to Delta.

### 📋 Deliverables

- `src/jobs/score.py` — scoring script
- `player_churn_scores` table (player_id, churn_probability, risk_tier)
- Scheduled Databricks Job (runs 2 AM UTC daily)

### ☁️ Azure Tasks

- Create Databricks Job with schedule (2 AM UTC)
- Monitor job runs in workspace UI
- (Optional) Set up alerts via Azure Monitor

### 🔑 Key Terms

- **Model promotion**: Move model from Staging → Production (in registry)
- **Batch inference**: Score many rows at once
- **Pandas UDF**: Distributed function for fast vectorized scoring
- **Incremental**: Only process new data (efficient)
- **Risk tier**: Categorize churn probability (low/med/high)

### ⏱️ Time: ~1 hour

### 📖 Reference

- MLflow model loading: [Docs](https://mlflow.org/docs/latest/python_api/mlflow.pyfunc.html)
- Databricks Jobs: [Documentation](https://docs.databricks.com/en/workflows/jobs/jobs.html)
- Pandas UDF: [Performance guide](https://docs.databricks.com/en/udf/pandas.html)

### Prerequisites: Lab 4

---

## Lab 6: Power BI Dashboards & Fabric Integration

### 🎯 Why This Lab?

Data insights live in Delta tables, but business users need **visualizations**. Power BI / Fabric connects to Databricks SQL:
- Interactive dashboards
- Drill-downs by region, platform, cohort
- Real-time metrics (DAU, churn rate, ARPU)
- Scheduled refresh (data updates 3x daily)

### 📚 Concepts

**Databricks SQL Warehouse:**
- Serverless SQL query engine (point-and-click queries)
- Optimized for analytics (vs. DLT which is optimized for ingestion)
- Enables Power BI DirectQuery (live connection)
- Pricing: Per-second when running (cheaper than all-purpose clusters)

**Power BI DirectQuery vs. Import:**
- **Import**: Copy data into Power BI (faster, but stale)
- **DirectQuery**: Query Databricks live (slower, but real-time)
- We use DirectQuery for this lab

**Dashboard Pages:**
- **Retention**: DAU trends, retention curve, churn risk segments
- **Revenue**: ARPU by cohort (whale, regular, casual, lapsed)
- **Matchmaking**: Queue wait time, win rate by tier, skill distribution
- **Engagement**: Session duration, platform/region breakdown

**Refresh Policy:**
- Databricks jobs run 2 AM UTC
- Power BI refresh 3 AM UTC (after jobs finish)
- Dashboards updated automatically each morning

### 🔧 Goal

Build Power BI dashboard connected to Databricks Gold tables.

### 📋 Deliverables

- `powerbi/LivesRemaining.pbix` workbook with 4 pages:
  - Retention & Churn
  - Revenue & ARPU
  - Matchmaking Quality
  - Engagement Metrics
- Refresh policy configured (3 AM UTC daily)

### ☁️ Azure Tasks

1. Create Databricks SQL Warehouse (serverless or provisioned)
2. Get SQL connection string from Databricks UI
3. In Power BI Desktop:
   - "Get Data" → "Azure Databricks"
   - Enter connection string & credentials
   - Select Gold tables
   - Create visuals & publish to Power BI Service
4. Set up scheduled refresh

### 🔑 Key Terms

- **Databricks SQL Warehouse**: Serverless SQL query engine
- **DirectQuery**: Live query to data source (vs. import)
- **DAU (Daily Active Users)**: Unique players logged in per day
- **Cohort**: Group of players (by spend: whale/regular/casual)
- **Retention curve**: % of players active N days after signup

### ⏱️ Time: ~2 hours

### 📖 Reference

- Databricks SQL: [Documentation](https://docs.databricks.com/en/sql/index.html)
- Power BI + Databricks: [Connection guide](https://docs.microsoft.com/en-us/power-bi/connect-data/service-azure-databricks)
- DAX formulas: [Power BI reference](https://dax.guide/)

### Prerequisites: Lab 5

---

## Lab 7: Real-Time Scoring Endpoint (Optional)

### 🎯 Why This Lab?

Batch scoring (Lab 5) runs daily. But what if we need **live risk scores** for:
- Showing churn risk in-game UI
- Triggering retention offers in real-time
- A/B testing different interventions

**Databricks Model Serving** deploys model as REST API.

### 📚 Concepts

**Batch vs. Real-Time:**
- **Batch**: Process all players nightly (Lab 5)
- **Real-time**: Score individual players on-demand (this lab)
- Real-time: Higher latency SLA (<100ms), higher cost
- Batch: Cheaper, but stale predictions

**Model Serving Endpoint:**
- REST API that returns predictions
- Auto-scales based on load
- Integrates with feature store (optional)

**Authentication (Azure):**
- Clients authenticate via Azure Entra
- Service principal with Databricks workspace permissions
- Token-based (Bearer token in HTTP header)

**Latency SLA:**
- P50 (median): ~20–50ms
- P95: ~100–200ms
- Goal: <100ms for game UI

### 🔧 Goal

Deploy MLflow model as REST endpoint for real-time scoring.

### 📋 Deliverables

- Model endpoint deployed via Databricks Model Serving
- Python client script to call endpoint
- Latency benchmarks (P50, P95, P99)
- Documentation for integration

### ☁️ Azure Tasks

- Deploy model to Databricks Model Serving
- Configure authentication (service principal)
- Test from local client
- Monitor via Databricks UI

### 🔑 Key Terms

- **Inference endpoint**: REST API for predictions
- **Latency SLA**: Response time guarantee (P50, P95, P99)
- **Bearer token**: OAuth token in HTTP header
- **Scaling**: Auto-add replicas under high load
- **A/B testing**: Show intervention to subset, measure impact

### ⏱️ Time: ~1.5 hours

### 📖 Reference

- Databricks Model Serving: [Documentation](https://docs.databricks.com/en/machine-learning/model-serving/index.html)
- REST API design: [Best practices](https://restfulapi.net/)
- Azure Entra auth: [OAuth 2.0](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow)

### Prerequisites: Lab 4

---

## Summary: 7 Labs, ~10–11 hours

| Lab | Duration | Concept | Outcome |
|-----|----------|---------|---------|
| 0   | 30 min   | Data generation | 100k events in ADLS |
| 1   | 1 hr     | DLT Autoloader | Bronze table (raw events) |
| 2   | 1.5 hr   | Silver transforms | Silver tables (clean) |
| 3   | 1.5 hr   | Feature engineering | Gold feature tables |
| 4   | 2 hr     | MLflow churn model | Trained & registered model |
| 5   | 1 hr     | Batch scoring | Daily predictions job |
| 6   | 2 hr     | Power BI dashboards | Interactive analytics UI |
| 7   | 1.5 hr   | Real-time endpoint | Live API for predictions |

---

## Learning Path

**Beginner focus:**
- Labs 0–2: Understand data flow (events → raw → clean)
- Labs 3–4: Basics of ML (features → model)
- Lab 6: See insights in action (dashboards)

**Intermediate focus:**
- Labs 5–7: Deployment & production patterns

**Azure focus:**
- Each lab: See how Azure services integrate (ADLS, Entra, SQL Warehouse, etc)

---

## Troubleshooting

See individual lab notebooks for common errors & fixes.

💡 **Tip**: If stuck, check the Databricks workspace logs (Jobs UI → Run history → Logs)
