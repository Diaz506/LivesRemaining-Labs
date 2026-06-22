# Lives Remaining Labs — Architecture Overview

**FICTIONAL COMPANY DISCLAIMER:** This architecture is designed around a fictional multiplayer game studio for educational purposes.

## Goals

- **Ingest** millions of player events in real-time (DLT Autoloader)
- **Transform** raw events into curated Silver and Gold tables (Bronze → Silver → Gold)
- **Feature** engineering for ML: churn risk, ARPU prediction, skill tiers, matchmaking scores
- **Model** lifecycle via MLflow: experiment tracking, registry, batch/real-time serving
- **Govern** tables via Unity Catalog (access control, lineage, discovery)
- **Visualize** KPIs and cohort analysis in Power BI / Fabric

## High-Level Data Flow

```
1. Player Events (Kafka/Kinesis/Cloud Storage)
   ↓
2. DLT Autoloader (Raw → Bronze ingestion)
   ↓
3. DLT Silver Transformations (normalization, aggregation, quality checks)
   ↓
4. Feature Jobs (session metrics, player profiles, engagement windows)
   ↓
5. Gold Feature Tables (churn_features, ARPU_features, skill_tiers)
   ↓
6. MLflow Training Job (train churn model, register in Model Registry)
   ↓
7. Batch Scoring Job (score all active players daily)
   ↓
8. Power BI Dashboards (retention, cohorts, server health)
```

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

## MLflow Integration

- **Experiment tracking**: Log churn model runs (accuracy, precision, recall)
- **Model Registry**: Register best churn model with staging/prod aliases
- **Batch scoring**: Daily job loads model, scores all players, writes `player_churn_scores` table
- **Real-time serving** (optional): REST endpoint for live player risk scoring

## Security & Governance

- **Unity Catalog**: Namespace tables by environment (dev, staging, prod)
- **Service principals**: Automation identities for jobs
- **Audit logs**: Delta transaction logs + UC lineage for compliance
- **Row-level filters** (optional): Restrict data by region/game-mode

## Scaling Notes

- **Streaming architecture**: Kafka/Event Hub → Autoloader handles backpressure
- **Partitioning**: Bronze by `ingest_date`, Silver by `player_id`, Gold by `compute_date`
- **Clustering**: Gold tables clustered on `player_id` for fast joins
