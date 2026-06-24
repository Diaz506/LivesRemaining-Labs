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

### Step 1 — Make the repo available in the workspace

**What this step does and why.** Brings the pipeline code (`bronze_pipeline.py`)
and the interactive walkthrough notebook into Databricks so the DLT pipeline can
point at them. A **Git folder** keeps them in sync with `main`.

**Already added this repo as a Git folder** during the prerequisites or Lab 0?
Then you're set — just open it and click **Pull** to get the latest, and skip to
Step 2.

**First time?** Add it as a Git folder:

1. **Workspace → Create → Git folder**
2. **Git repository URL:** `https://github.com/Diaz506/LivesRemaining-Labs.git`
3. Leave provider = **GitHub**; the folder name auto-fills to `LivesRemaining-Labs`.
4. Click **Create Git folder**.

You should now see `src/dlt/bronze_pipeline.py` and `notebooks/dlt/01_ingest_bronze.py` inside the folder.

### Step 2 — How the pipeline reaches your data (no mount, no SP)

**What this step does and why.** Just context so the next step makes sense — there's
nothing to configure here. The pipeline reads
`abfss://datalake@lrlstorage01.dfs.core.windows.net/events/` **directly** through
the Unity Catalog **external location** you created in the
[prerequisites](prerequisites.md) (`notebooks/setup/00_unity_catalog_setup.py`).
There's **no mount and no service principal** — UC's Access Connector (managed
identity) handles storage auth, which is why this works on serverless.

You'll **verify** that access in Step 3 (the walkthrough notebook does it for you).
If you want a quick one-off check now, open **any notebook on Serverless**, paste
this into a cell, and run it:

```python
EVENTS_PATH = "abfss://datalake@lrlstorage01.dfs.core.windows.net/events/"
display(dbutils.fs.ls(EVENTS_PATH))   # expect to see raw_events.csv
```

> If this fails with access denied, re-run the UC setup notebook and confirm the
> Access Connector has **Storage Blob Data Contributor** on the storage account.
>
> ⚠️ This path assumes the storage account **`lrlstorage01`** and container
> **`datalake`** from the [prerequisites](prerequisites.md). If you used
> different names, update `EVENTS_PATH` here and `src/dlt/bronze_pipeline.py` to
> match.

### Step 3 — Verify data is reachable

**What this step does and why.** Before building the pipeline, you confirm
Databricks can actually *list and read* the CSV through the external location — so
if something's wrong (missing file, bad grant), you catch it here instead of in a
failed pipeline run. Open `notebooks/dlt/01_ingest_bronze.py`, attach it to
**Serverless**, and run the verification cells (Part 6, Steps 2–4). Expected:

```
✅ External location is reachable: abfss://datalake@lrlstorage01.dfs.core.windows.net/events/
✅ Found 1 files in abfss://datalake@lrlstorage01.dfs.core.windows.net/events/:
  - raw_events.csv
✅ Successfully read CSV! Shape: 100000 rows, 10 columns
```

### Step 4 — Create the DLT pipeline

> ⚠️ **Don't click *Run* on `bronze_pipeline.py`.** It's DLT source code, not a
> notebook — running it on a normal cluster fails with
> `ModuleNotFoundError: No module named 'dlt'` (the `dlt` module only exists in the
> DLT pipeline runtime). You *register* it as a pipeline below, and DLT runs it for
> you in Step 5.

**What this step does and why.** A DLT pipeline is the managed job that runs
`bronze_pipeline.py` — it handles checkpoints, schema, expectations, and lineage
for you. Here you just register it and tell it *where the code is* and *which
catalog/schema to write to*.

**Create the pipeline.** Click **+ New → ETL pipeline** (or **Jobs & Pipelines →
Create → ETL pipeline**). *DLT is now labeled "ETL pipeline" / Lakeflow Declarative
Pipelines — older docs call this "Workflows → Delta Live Tables".* The newer UI is a
**two-phase** flow:

**Phase 1 — pick a starting point.** Choose **"Start with an empty pipeline"**
(**Blank**) — *not* the sample, which generates demo tables you don't need. Set:

| Setting | Value |
|---------|-------|
| Pipeline name | `lives-remaining-bronze-ingestion` |
| Default catalog | `labs` |
| Default schema | `bronze` |
| Compute | **Serverless** (default — no cluster to size) |

**Phase 2 — point it at your code.** A blank pipeline has no source yet. Open the
pipeline's **Settings** (gear icon) → **Source code** / **Paths** → **Add** your
Git-folder file:

```
/Workspace/Users/<you>/LivesRemaining-Labs/src/dlt/bronze_pipeline.py
```

Remove any sample/transformation path it auto-added, then **Save**.

> 🏷️ **Triggered vs Continuous isn't a create-time field anymore.** Just clicking
> **Run pipeline** (Step 5) does a one-off *triggered* run, which is what we want.

### Step 5 — Run the pipeline

**What this step does and why.** Starting the pipeline executes the ingestion:
Autoloader reads the new CSV, applies the quality expectations, and writes the
Bronze Delta table. The first run is a cold start (reads everything); later runs
only pick up new files.

Click **Start** (labeled **Run pipeline** / **Run all** in the newer UI). DLT builds the graph and creates:
- `lives_remaining_raw_events` (Bronze table)
- `events_quality_metrics`, `raw_events_summary` (monitoring)

Watch the graph go green. The three expectations (`valid_event_id`, `valid_player_id`, `valid_event_type` from `bronze_pipeline.py:51-53`) report pass/drop counts on the table node.

### Step 6 — Verify the Bronze table

**What this step does and why.** Confirms the table landed with the expected row
count and event-type spread — proof the ingestion worked end to end and that the
expectations kept the good rows.

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
| `ModuleNotFoundError: No module named 'dlt'` | You ran `bronze_pipeline.py` directly. Don't — register it as a DLT pipeline (Step 4) and **Start** it (Step 5). `dlt` only exists in the pipeline runtime. |
| `Operation failed` / access denied on `abfss://…` | Re-run the [UC bootstrap](prerequisites.md); verify the Access Connector has **Storage Blob Data Contributor**. |
| `No files found in …/events/` | Re-run **Lab 0** to land `raw_events.csv` (Option A upload, or Option B notebook). |
| `catalog/schema not found` | Run the [Unity Catalog bootstrap](prerequisites.md). |
| Many rows dropped | Inspect failing expectation in the DLT UI → likely an unexpected `event_type`. |

**Next:** [Lab 2 — Silver transformations →](lab-2-silver-transformations.md)
