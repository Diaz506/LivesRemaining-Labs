# Lab 1: Bronze Ingestion via DLT Autoloader

**Goal:** Ingest the raw CSV events from ADLS Gen2 into the Bronze Delta table `labs.bronze.lives_remaining_raw_events` using a Delta Live Tables (DLT) Autoloader pipeline.

⏱️ **Time:** ~1 hr &nbsp;|&nbsp; **Prerequisites:** [Lab 0](lab-0-setup-data-generation.md)

> 🎮 **Mission Briefing**
>
> "Raw events are landing in the lake, but they're just CSV files nobody can trust yet," Dev Rao says, pulling up the storage browser. Your job: get them into a **Bronze** Delta table — reliably, incrementally, with quality checks — so the rest of the pipeline has solid ground to stand on.

---

### 🎯 Why this lab

The Bronze layer stores raw events *as-is* for audit and replay. DLT + Autoloader gives us incremental ingestion (only new files), schema enforcement, quality expectations, and automatic lineage — without managing checkpoints by hand.

**Artifacts you'll use:** `src/dlt/bronze_pipeline.py` (pipeline) and `notebooks/dlt/01_ingest_bronze.py` (interactive walkthrough).

---

## 🪜 Steps

### Step 1 — Import the repo into the workspace

In the Databricks workspace: **Workspace → (your folder) → Create → Git folder**, point it at this repo. You should see `src/dlt/bronze_pipeline.py` and `notebooks/dlt/01_ingest_bronze.py`.

### Step 2 — Give the cluster access to ADLS Gen2

The pipeline reads `/mnt/data/events/`. Mount ADLS Gen2 with the service principal **once** (run in a notebook attached to an all-purpose cluster):

```python
configs = {
  "fs.azure.account.auth.type": "OAuth",
  "fs.azure.account.oauth.provider.type": "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider",
  "fs.azure.account.oauth2.client.id": dbutils.secrets.get("lrl", "sp-client-id"),
  "fs.azure.account.oauth2.client.secret": dbutils.secrets.get("lrl", "sp-secret"),
  "fs.azure.account.oauth2.client.endpoint": "https://login.microsoftonline.com/<tenant-id>/oauth2/v2.0/token",
}
dbutils.fs.mount(
  source="abfss://datalake@lrlstorage.dfs.core.windows.net/",
  mount_point="/mnt/data",
  extra_configs=configs,
)
```

> Prefer Unity Catalog external locations over mounts in production. For this lab the mount keeps `src/dlt/bronze_pipeline.py` simple (it reads `/mnt/data/events/`).

### Step 3 — Verify data is reachable

Open `notebooks/dlt/01_ingest_bronze.py` and run the verification cells (Part 6, Steps 2–6). Expected:

```
✅ Mount /mnt/data is ready!
✅ Found 1 files in /mnt/data/events/:
  - raw_events.csv
✅ Successfully read CSV! Shape: 100000 rows, 10 columns
```

### Step 4 — Create the DLT pipeline

**Workflows → Delta Live Tables → Create pipeline**:

| Setting | Value |
|---------|-------|
| Pipeline name | `lives-remaining-bronze-ingestion` |
| Source code | `…/src/dlt/bronze_pipeline.py` |
| Destination | **Unity Catalog** → Catalog `labs`, Target schema `bronze` |
| Pipeline mode | **Triggered** |
| Cluster | Default job cluster (autoscale 1–2) |

### Step 5 — Run the pipeline

Click **Start**. DLT builds the graph and creates:
- `lives_remaining_raw_events` (Bronze table)
- `events_quality_metrics`, `raw_events_summary` (monitoring)

Watch the graph go green. The three expectations (`valid_event_id`, `valid_player_id`, `valid_event_type` from `bronze_pipeline.py:47-49`) report pass/drop counts on the table node.

### Step 6 — Verify the Bronze table

In a SQL cell or notebook:

```sql
SELECT COUNT(*) AS rows, COUNT(DISTINCT player_id) AS players
FROM labs.bronze.lives_remaining_raw_events;

SELECT event_type, COUNT(*) FROM labs.bronze.lives_remaining_raw_events GROUP BY event_type;
```

Expect ~100k rows (minus any dropped by expectations) across all 6 event types.

---

## ✅ Done when

- [ ] DLT pipeline `lives-remaining-bronze-ingestion` ran successfully (all nodes green)
- [ ] `labs.bronze.lives_remaining_raw_events` exists and is queryable
- [ ] Expectation metrics show valid rows kept, invalid rows dropped

## 🧯 Troubleshooting

| Symptom | Fix |
|---------|-----|
| `Mount /mnt/data not found` | Re-run Step 2; verify the service principal secret scope. |
| `No files found in /mnt/data/events/` | Re-run Lab 0 Step 5 (upload). |
| `catalog/schema not found` | Run the [Unity Catalog bootstrap](prerequisites.md#provision--bootstrap). |
| Many rows dropped | Inspect failing expectation in the DLT UI → likely an unexpected `event_type`. |

**Next:** [Lab 2 — Silver transformations →](lab-2-silver-transformations.md)
