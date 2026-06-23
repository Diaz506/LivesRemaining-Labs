# Lives Remaining Labs — Architecture Overview

**FICTIONAL COMPANY DISCLAIMER:** This architecture is designed around a fictional game studio for educational purposes on **Azure Databricks**.

## Goals

- **Ingest** millions of player events via Azure Event Hubs or Blob Storage into DLT
- **Transform** raw events into curated Silver and Gold tables (Bronze → Silver → Gold)
- **Feature** engineering for ML: churn risk, ARPU prediction, skill tiers, matchmaking scores
- **Model** lifecycle via MLflow: experiment tracking, registry, batch/real-time serving
- **Govern** tables via Unity Catalog (access control, lineage, discovery)
- **Visualize** KPIs and cohort analysis in Power BI / Fabric (connected to Azure Databricks SQL)

## High-Level Data Flow (Azure)

```
1. Player Events (Azure Blob Storage or Event Hubs)
   ↓
2. Azure Databricks Workspace
   ├─ DLT Autoloader (reads from ADLS Gen2)
   └─ Service Principal: Storage Blob Data Reader on storage account
   ↓
3. DLT Silver Transformations (normalization, aggregation, quality checks)
   ↓
4. Feature Jobs (session metrics, player profiles, engagement windows)
   ├─ Cluster: Standard with optional GPU (for model training)
   └─ Job identity: Service principal
   ↓
5. Gold Feature Tables (churn_features, ARPU_features, skill_tiers)
   ├─ Stored in Unity Catalog (premium workspace required)
   └─ Partitioned by compute_date
   ↓
6. MLflow Training Job (train churn model, register in Model Registry)
   ├─ MLflow Tracking: Azure Databricks workspace
   └─ Model artifacts: workspace storage
   ↓
7. Batch Scoring Job (score all active players daily)
   ├─ Scheduled via Azure Databricks Jobs
   └─ Runs 2 AM UTC daily
   ↓
8. Power BI / Fabric Dashboards (retention, cohorts, server health)
   ├─ Data source: Databricks SQL Warehouse (serverless or provisioned)
   └─ Scheduled refresh: 3 AM UTC
```

## Azure Services Used

| Service | Purpose | Lab |
|---------|---------|-----|
| **Azure Databricks** | Analytics & ML platform | All |
| **Azure Data Lake Storage (ADLS Gen2)** | Data lake for Bronze/Silver/Gold | Labs 0–1 |
| **Azure Event Hubs** (optional) | Real-time event streaming ingestion | Lab 1 (optional) |
| **Azure Key Vault** | Secrets management (storage keys, PATs) | Setup |
| **Azure Entra (AAD)** | Service principal authentication | Setup |
| **Power BI Premium / Microsoft Fabric** | Dashboarding & interactive analytics | Lab 6 |

## Key Tables

### Bronze
- `lives_remaining_raw_events` — Raw event dumps (event_id, player_id, event_type, timestamp, payload JSON)

### Silver
- `player_sessions` — Session-level aggregates (session_id, player_id, start_ts, duration_min, kills, losses, spent_usd)
- `player_events_cleaned` — Normalized and quality-checked events

### Gold
- `churn_features_daily` — Churn model features (player_id, days_since_login, session_count_7d, avg_session_duration, avg_spend_30d, churn_label)
- `arpu_features_daily` — Revenue model features
- `player_segments` — Cohort/tier assignments (whale, regular, casual, lapsed)
- `player_churn_scores` — Batch prediction output for Power BI and retention workflows

## MLflow Integration

- **Experiment tracking**: Log churn model runs (accuracy, precision, recall)
- **Model Registry**: Register best churn model with staging/prod aliases
- **Batch scoring**: Daily job loads model, scores all players, writes `player_churn_scores` table
- **Real-time serving** (optional): REST endpoint for live player risk scoring

## Lab Implementation Map

| Lab | Primary artifact | Output |
|-----|------------------|--------|
| 1 | `src/dlt/bronze_pipeline.py` | Bronze raw events |
| 2 | `src/dlt/silver_pipeline.py` | Cleaned events, sessions, purchases |
| 3 | `src/dlt/gold_pipeline.py` | Churn, ARPU, and segment features |
| 4 | `src/jobs/train_churn_model.py` | Registered MLflow churn model |
| 5 | `src/jobs/batch_score_churn.py` | `player_churn_scores` |
| 6 | `notebooks/powerbi/06_powerbi_dashboard_setup.py` | SQL views for Power BI |
| 7 | `src/jobs/create_serving_endpoint.py` | Optional model serving endpoint |

## Security & Governance (Azure)

- **Unity Catalog**: The labs use a single catalog `labs` with `bronze`/`silver`/`gold` schemas (three-level names `labs.bronze.*`, etc.). For multi-environment isolation, create a catalog **per environment** (`labs_dev` / `labs_staging` / `labs_prod`) — the setup notebook's `catalog` widget and the Terraform `catalog_name` variable make this a one-line change. *(The lab code references `labs` directly for simplicity.)*
- **Service Principals**: Azure Entra (AAD) service principals for job automation
- **Azure RBAC**: Storage account roles (Storage Blob Data Reader, Contributor)
- **Azure Key Vault**: Store secrets (storage connection strings, Databricks PATs)
- **Audit logs**: Delta transaction logs + UC lineage for compliance and audit trails
- **Network Security**: Optional VNet integration for private connectivity

## Scaling Notes (Azure)

- **Streaming architecture**: Azure Event Hubs → DLT Autoloader handles backpressure & dead-letter queues
- **Databricks compute**: Auto-scaling clusters (min 2–4 workers, max 32+)
- **Partitioning**: Bronze by `ingest_date`, Silver by `player_id`, Gold by `compute_date`
- **Clustering**: Gold tables clustered on `player_id` for fast joins
- **Cost optimization**: Use Spot instances for non-critical jobs, serverless SQL warehouses for analytics
