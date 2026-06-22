# Lab 0: Setup & Sample Data Generation

### 🎯 Why This Lab?

Before we can build a data pipeline, we need realistic data. This lab generates synthetic player events that mimic real game telemetry: logins, kills, purchases, etc.

### 📚 Concepts

**Synthetic Data Generation:**
- Real production data is sensitive (contains PII)
- Synthetic data lets us practice without privacy concerns
- We use `faker` library to create realistic-looking random data
- Events must match our schema (see `../data-schema.md`)

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

- Schema: `../data-schema.md`
- Generator script: `scripts/generate_events.py`

---
