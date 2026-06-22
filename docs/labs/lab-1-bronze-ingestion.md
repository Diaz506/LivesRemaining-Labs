# Lab 1: Bronze Ingestion via DLT Autoloader (Azure)

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

- Schema: `../data-schema.md`
- DLT docs: [Databricks DLT](https://docs.databricks.com/en/delta-live-tables/)
- Autoloader: [Cloud file ingestion](https://docs.databricks.com/en/ingestion/auto-loader/)

### Prerequisites: Lab 0

---
