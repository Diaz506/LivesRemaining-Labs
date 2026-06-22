# PixelForge Labs — Sequence & Instructions

## Lab 0: Setup & Sample Data Generation

**Goal**: Generate synthetic player events and load into `/data`.

**Topics**: Event schema design, synthetic data generation (faker library), local testing.

**Deliverables**:
- `data/raw_events.csv` (100k sample player events)
- `data/event_schema.json` (schema documentation)
- Quick-start script to generate events locally

**Time**: ~30 min

---

## Lab 1: Bronze Ingestion via DLT Autoloader

**Goal**: Ingest raw events from cloud storage into Delta Bronze table.

**Topics**: DLT Autoloader, schema inference, watermarking, error handling.

**Deliverables**:
- `src/dlt/bronze_pipeline.py` — raw events → `pixelforge_raw_events`
- `notebooks/dlt/01_ingest_bronze.py` — runnable notebook
- Bronze table with 100k events ingested

**Time**: ~1 hour

**Prerequisites**: Lab 0 (sample data)

---

## Lab 2: Silver Transformations & Quality Checks

**Goal**: Normalize Bronze events, compute session aggregates, apply DLT quality rules.

**Topics**: DLT expectations, PySpark transforms, SCD (Slowly Changing Dimensions for player profiles).

**Deliverables**:
- `src/dlt/silver_pipeline.py` — Bronze → Silver (player_sessions, player_events_cleaned)
- Quality metrics (rows processed, expectations passed/failed)
- Silver tables ready for analytics

**Time**: ~1.5 hours

**Prerequisites**: Lab 1

---

## Lab 3: Feature Engineering for ML

**Goal**: Engineer Gold feature tables for churn and ARPU modeling.

**Topics**: Window functions, feature windows (7d, 30d), handling data drift.

**Deliverables**:
- `src/jobs/featurize.py` — Gold feature tables (churn_features_daily, arpu_features_daily)
- `notebooks/jobs/01_featurize.py` — walkthrough
- Features computed for training dataset

**Time**: ~1.5 hours

**Prerequisites**: Lab 2

---

## Lab 4: Churn Prediction with MLflow

**Goal**: Train churn classification model, log experiments in MLflow, register in Model Registry.

**Topics**: sklearn, MLflow tracking, model registry, hyperparameter tuning.

**Deliverables**:
- `src/jobs/train.py` — churn model training script
- `notebooks/jobs/02_train_model.py` — interactive training
- Registered model in MLflow registry (accuracy ~0.85+)

**Time**: ~2 hours

**Prerequisites**: Lab 3

---

## Lab 5: Batch Scoring & Predictions

**Goal**: Load trained model, score all active players daily, write predictions back to Delta.

**Topics**: Model serving via MLflow, batch inference, incremental updates.

**Deliverables**:
- `src/jobs/score.py` — daily batch scoring job
- `player_churn_scores` table with player_id, churn_probability, risk_tier
- Scheduled Databricks Job to run daily

**Time**: ~1 hour

**Prerequisites**: Lab 4

---

## Lab 6: Power BI Dashboards & Fabric Integration

**Goal**: Connect Power BI to Gold tables, build retention + cohort drills.

**Topics**: Power BI DirectQuery, Fabric lakehouse, data refresh scheduling.

**Deliverables**:
- `powerbi/PixelForge.pbix` dashboard with:
  - Daily active players (DAU) trend
  - Churn risk segments
  - ARPU by cohort (whale/regular/casual)
  - Matchmaking quality heatmap
- Refresh policy configured

**Time**: ~2 hours

**Prerequisites**: Lab 5

---

## Lab 7: Real-Time Scoring Endpoint (Optional)

**Goal**: Deploy MLflow model as REST endpoint for live player risk scoring.

**Topics**: MLflow Model Serving, A/B testing infrastructure, SLA monitoring.

**Deliverables**:
- Model serving endpoint (via MLflow or Databricks Model Serving)
- Python client script to query endpoint
- Latency & throughput benchmarks

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
