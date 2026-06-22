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

## Lab 0: Setup & Sample Data Generation

**Goal**: Generate synthetic player events and upload to Azure Blob Storage.

**Topics**: Event schema design, synthetic data generation (faker library), Azure Blob upload.

**Deliverables**:
- `data/raw_events.csv` (100k sample player events)
- `data/event_schema.json` (schema documentation)
- CSV uploaded to Azure Blob Storage (`abfss://datalake@lrlstorage.dfs.core.windows.net/events/`)

**Azure tasks**:
- Create blob container `events/` in ADLS Gen2
- Use Azure CLI or azcopy to upload CSV

**Time**: ~30 min

---

## Lab 1: Bronze Ingestion via DLT Autoloader (Azure)

**Goal**: Ingest raw events from Azure Blob Storage into Delta Bronze table via DLT Autoloader.

**Topics**: DLT Autoloader, ADLS Gen2 mounting, schema inference, watermarking, error handling, service principal auth.

**Deliverables**:
- `src/dlt/bronze_pipeline.py` — raw events → `lives_remaining_raw_events`
- `notebooks/dlt/01_ingest_bronze.py` — runnable notebook
- Bronze table ingested into Unity Catalog
- Autoloader checkpoint stored in ADLS Gen2

**Azure tasks**:
- Mount ADLS Gen2 in Databricks cluster using service principal credentials
- Create external location in Unity Catalog
- Configure Autoloader with `/mnt/events/` path

**Time**: ~1 hour

**Prerequisites**: Lab 0 (sample data uploaded to Azure Blob Storage)

---

## Lab 2: Silver Transformations & Quality Checks (Azure Databricks)

**Goal**: Normalize Bronze events, compute session aggregates, apply DLT quality rules.

**Topics**: DLT expectations, PySpark transforms, SCD (Slowly Changing Dimensions), Delta features.

**Deliverables**:
- `src/dlt/silver_pipeline.py` — Bronze → Silver (player_sessions, player_events_cleaned)
- Quality metrics (rows processed, expectations passed/failed)
- Silver tables stored in Unity Catalog

**Azure tasks**:
- Use Unity Catalog for table namespace
- Monitor cluster metrics in Databricks workspace
- Check job run history in Jobs UI

**Time**: ~1.5 hours

**Prerequisites**: Lab 1

---

## Lab 3: Feature Engineering for ML (Azure Databricks)

**Goal**: Engineer Gold feature tables for churn and ARPU modeling.

**Topics**: Window functions, feature windows (7d, 30d), handling data drift, feature store (optional).

**Deliverables**:
- `src/jobs/featurize.py` — Gold feature tables (churn_features_daily, arpu_features_daily)
- `notebooks/jobs/01_featurize.py` — walkthrough
- Features computed and stored in Unity Catalog
- Databricks Job scheduled for daily runs

**Azure tasks**:
- Create job in Databricks workspace (schedule daily at 1 AM UTC)
- Use job clusters for cost efficiency
- Monitor via Azure Monitor / Databricks workspace UI

**Time**: ~1.5 hours

**Prerequisites**: Lab 2

---

## Lab 4: Churn Prediction with MLflow (Azure Databricks)

**Goal**: Train churn classification model, log experiments in MLflow, register in Model Registry.

**Topics**: sklearn, MLflow tracking, model registry, hyperparameter tuning, model versioning.

**Deliverables**:
- `src/jobs/train.py` — churn model training script
- `notebooks/jobs/02_train_model.py` — interactive training
- Registered model in MLflow registry (accuracy ~0.85+)
- Model artifacts stored in Databricks workspace

**Azure tasks**:
- View MLflow Tracking UI in Databricks workspace
- Register model in MLflow Model Registry
- Compare runs and select best model

**Time**: ~2 hours

**Prerequisites**: Lab 3

---

## Lab 5: Batch Scoring & Predictions (Azure Databricks)

**Goal**: Load trained model, score all active players daily, write predictions back to Delta.

**Topics**: Model serving via MLflow, batch inference, incremental updates, Databricks Jobs scheduling.

**Deliverables**:
- `src/jobs/score.py` — daily batch scoring job
- `player_churn_scores` table with player_id, churn_probability, risk_tier
- Scheduled Databricks Job to run daily (2 AM UTC)

**Azure tasks**:
- Create Databricks Job with schedule
- Monitor job runs in Databricks workspace
- Set up alerts for job failures (optional: via Azure Monitor)

**Time**: ~1 hour

**Prerequisites**: Lab 4

---

## Lab 6: Power BI Dashboards & Fabric Integration

**Goal**: Connect Power BI to Azure Databricks SQL, build retention + cohort drills.

**Topics**: Power BI DirectQuery to Databricks, SQL Warehouse connection, Fabric lakehouse integration, data refresh scheduling.

**Deliverables**:
- `powerbi/LivesRemaining.pbix` dashboard with:
  - Daily active players (DAU) trend
  - Churn risk segments (Low / Medium / High)
  - ARPU by cohort (whale/regular/casual)
  - Matchmaking quality heatmap
  - Player engagement metrics
- Refresh policy configured for 3 AM UTC

**Azure tasks**:
- Create Databricks SQL Warehouse (serverless or provisioned)
- Generate SQL connection string in Databricks
- Connect Power BI to SQL Warehouse via DirectQuery
- Set up Power BI scheduled refresh

**Time**: ~2 hours

**Prerequisites**: Lab 5

---

## Lab 7: Real-Time Scoring Endpoint (Optional)

**Goal**: Deploy MLflow model as REST endpoint for live player risk scoring on Azure.

**Topics**: Databricks Model Serving, REST API, latency SLAs, A/B testing.

**Deliverables**:
- Model serving endpoint via Databricks Model Serving
- Python client script to query endpoint
- Latency & throughput benchmarks
- Documentation for integration

**Azure tasks**:
- Deploy model to Databricks Model Serving
- Configure endpoint authentication (Azure Entra service principal)
- Test endpoint from local client
- Monitor via Azure Monitor / Databricks workspace

**Time**: ~1.5 hours

**Prerequisites**: Lab 4

---

## Total Time: ~10–11 hours (4–5 day workshop)

**Suggested Pacing**:
- Day 1: Labs 0–1 (Setup, Bronze ingestion)
- Day 2: Labs 2–3 (Silver, feature engineering)
- Day 3: Labs 4–5 (Training, scoring)
- Day 4: Lab 6 (Dashboards)
- Day 5 (optional): Lab 7 (Real-time serving)
