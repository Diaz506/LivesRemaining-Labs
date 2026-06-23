# Lab 0: Setup & Sample Data Generation

**Goal:** Generate 100,000 synthetic player events and land them in ADLS Gen2 so the DLT pipelines have data to ingest.

⏱️ **Time:** ~30 min &nbsp;|&nbsp; **Prerequisites:** [Setup / Unity Catalog bootstrap](prerequisites.md)

> 🎮 **Mission Briefing**
>
> Maya Chen, Head of Live Ops, drops a 9am message: *"Day-30 retention fell six points after the last patch and analytics is flying blind — we have no event data to work with."* Before anyone can find the churning whales, the Player Intelligence team needs a realistic stream of player telemetry to build on. Today, you generate it.

---

### 🎯 Why this lab

The pipelines in Labs 1–3 read raw CSV events from `abfss://datalake@<account>.dfs.core.windows.net/events/`. Real telemetry contains PII, so we generate realistic *synthetic* events with `faker` instead.

---

## 🪜 Steps

### Step 1 — Install local dependencies

```bash
pip install pandas faker numpy
```

### Step 2 — Generate the events CSV

From the repo root run the generator (it is already in `scripts/generate_events.py`):

```bash
python scripts/generate_events.py --output data/raw_events.csv --count 100000 --players 10000 --days 30
```

**Expected output (tail):**

```
✅ Saved 100,000 events to data/raw_events.csv

Summary:
  Total events: 100,000
  Unique players: ~10,000
  Event types: {'login': ..., 'kill': ..., 'purchase': ..., ...}
  Date range: <30 days ago> to <today>
```

> The CSV columns match the Bronze schema in [`../data-schema.md`](../data-schema.md): `event_id, player_id, event_type, timestamp, game_mode, region, platform, payload, ingest_ts, ingest_date`.

### Step 3 — Verify the file locally

```bash
python -c "import pandas as pd; df=pd.read_csv('data/raw_events.csv'); print(df.shape); print(df['event_type'].value_counts())"
```

You should see `(100000, 10)` and a distribution across the 6 event types.

### Step 4 — Create the `events/` path in ADLS Gen2

If you already created the `datalake` container during [setup](prerequisites.md) (UI Step 1 or Terraform), it exists. Otherwise create it:

```bash
az storage fs directory create \
  --account-name lrlstorage \
  --file-system datalake \
  --name events
```

### Step 5 — Upload the CSV to ADLS Gen2

```bash
az storage fs file upload \
  --account-name lrlstorage \
  --file-system datalake \
  --source data/raw_events.csv \
  --path events/raw_events.csv
```

(Or use `azcopy copy "data/raw_events.csv" "https://lrlstorage.blob.core.windows.net/datalake/events/"`.)

### Step 6 — Confirm the upload

```bash
az storage fs file list --account-name lrlstorage --file-system datalake --path events -o table
```

You should see `events/raw_events.csv`.

---

## ✅ Done when

- [ ] `data/raw_events.csv` exists locally with 100k rows
- [ ] `events/raw_events.csv` is present in the `datalake` container
- [ ] The 6 event types and 4 regions appear in the summary

## 🧯 Troubleshooting

| Symptom | Fix |
|---------|-----|
| `Install dependencies` error | Run Step 1 (`pip install pandas faker numpy`). |
| `az: command not found` | Install Azure CLI and run `az login`. |
| Upload 403 | Your identity needs **Storage Blob Data Contributor** on the storage account. |

**Next:** [Lab 1 — Bronze ingestion →](lab-1-bronze-ingestion.md)
