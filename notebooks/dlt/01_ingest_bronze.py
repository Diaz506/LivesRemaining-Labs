# Databricks notebook source
# COMMAND ----------

# MAGIC %md
# MAGIC # Lab 1: Bronze Ingestion via DLT Autoloader
# MAGIC ## Lives Remaining Labs — Azure Databricks
# MAGIC
# MAGIC **Fictional Company**: Lives Remaining Labs is a fictional multiplayer game studio.
# MAGIC
# MAGIC ### 🎯 Lab Goal
# MAGIC Ingest raw player events from Azure Blob Storage (ADLS Gen2) into a Bronze Delta table using Delta Live Tables Autoloader.
# MAGIC
# MAGIC ### 📚 What You'll Learn
# MAGIC 1. **Delta Lake**: ACID-compliant data format (faster queries + reliability)
# MAGIC 2. **DLT Autoloader**: Automatic incremental ingestion (only new files processed)
# MAGIC 3. **Quality Expectations**: Data validation rules that catch schema errors
# MAGIC 4. **Unity Catalog Storage Access**: governed `abfss://` access via external locations (no mount)
# MAGIC 5. **Azure ADLS Gen2**: Hierarchical cloud data lake storage

# COMMAND ----------

# MAGIC %md
# MAGIC ## Prerequisites
# MAGIC - ✅ Lab 0 completed (raw_events.csv uploaded to Azure)
# MAGIC - ✅ Unity Catalog external location to ADLS Gen2 created (`notebooks/setup/00_unity_catalog_setup.py`)
# MAGIC - ✅ Running on **Serverless** (or any UC-enabled) compute — no mount, no cluster sizing required

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 1: Understanding the Bronze Layer
# MAGIC
# MAGIC ### Medallion Architecture (Bronze → Silver → Gold)
# MAGIC
# MAGIC ```
# MAGIC Raw Data (Cloud Storage)
# MAGIC      ↓
# MAGIC   BRONZE LAYER (this lab)
# MAGIC      ├─ As-is, no transformations
# MAGIC      ├─ Schema inferred from data
# MAGIC      └─ Used for audit trail & recovery
# MAGIC      ↓
# MAGIC   SILVER LAYER (Lab 2)
# MAGIC      ├─ Cleaned, deduplicated
# MAGIC      ├─ Business logic applied
# MAGIC      └─ Ready for analytics
# MAGIC      ↓
# MAGIC   GOLD LAYER (Lab 3)
# MAGIC      ├─ Aggregated features
# MAGIC      ├─ Ready for ML/dashboards
# MAGIC      └─ Business-aligned tables
# MAGIC ```
# MAGIC
# MAGIC **Why Bronze?**
# MAGIC - Preserve raw data for compliance/audit
# MAGIC - Easy recovery if downstream transforms have bugs
# MAGIC - Enables reprocessing with fixes

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 2: Delta Lake Basics
# MAGIC
# MAGIC **Delta Lake** = Data Lake + Data Warehouse
# MAGIC
# MAGIC | Feature | Data Lake | Data Warehouse | Delta Lake |
# MAGIC |---------|-----------|----------------|-----------|
# MAGIC | **Format** | Parquet/CSV | Optimized DB | Parquet + Transaction Log |
# MAGIC | **ACID** | ❌ | ✅ | ✅ |
# MAGIC | **Schema Enforcement** | ❌ | ✅ | ✅ |
# MAGIC | **Time Travel** | ❌ | Limited | ✅ (inspect history) |
# MAGIC | **Scalability** | ✅ | Limited | ✅ |
# MAGIC | **Cost** | 💰 Cheap | 💰💰💰 Expensive | 💰💰 Medium |
# MAGIC
# MAGIC **Example: Time Travel in Delta**
# MAGIC ```sql
# MAGIC -- See table as it was 1 hour ago
# MAGIC SELECT * FROM table_name VERSION AS OF 12345
# MAGIC
# MAGIC -- Rollback to 2 hours ago
# MAGIC RESTORE TABLE table_name TO VERSION AS OF 12340
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 3: Delta Live Tables (DLT) Fundamentals
# MAGIC
# MAGIC **DLT** = Declarative ETL Framework
# MAGIC
# MAGIC #### Traditional Spark Approach (imperative)
# MAGIC ```python
# MAGIC # You manage everything manually
# MAGIC df = spark.readStream.option("checkpointLocation", "/path").load("data")
# MAGIC df = df.select("col1", "col2").filter("col1 IS NOT NULL")
# MAGIC df.writeStream.option("checkpointLocation", "/path").mode("append").save("bronze_table")
# MAGIC ```
# MAGIC
# MAGIC #### DLT Approach (declarative)
# MAGIC ```python
# MAGIC @dlt.table
# MAGIC @dlt.expect_or_drop("valid", "col1 IS NOT NULL")
# MAGIC def bronze_table():
# MAGIC     return spark.read.load("data")
# MAGIC ```
# MAGIC
# MAGIC **DLT Handles Automatically:**
# MAGIC - ✅ Checkpoints (tracks processed files)
# MAGIC - ✅ Schema evolution (handles new columns)
# MAGIC - ✅ Idempotency (safe to re-run)
# MAGIC - ✅ Error recovery (restarts from checkpoint)
# MAGIC - ✅ Data quality tracking (expectations results)
# MAGIC - ✅ Lineage (tracks table dependencies)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 4: Autoloader (Cloud File Ingestion)
# MAGIC
# MAGIC **Autoloader** watches a cloud directory for new files.
# MAGIC
# MAGIC ### How It Works
# MAGIC
# MAGIC **Traditional streaming:** Poll storage every N seconds (expensive, slow)
# MAGIC ```
# MAGIC T=0s:  Check folder → 0 new files
# MAGIC T=10s: Check folder → 0 new files
# MAGIC T=20s: Check folder → 0 new files  ← Wasted queries!
# MAGIC T=30s: Check folder → 1 new file ✅
# MAGIC ```
# MAGIC
# MAGIC **Autoloader:** Uses cloud notifications + fallback polling (efficient)
# MAGIC ```
# MAGIC File uploaded to ADLS → Event Grid notification → DLT ingests immediately ✅
# MAGIC (Fallback: Every 15 min, scan for missed files)
# MAGIC ```
# MAGIC
# MAGIC ### Checkpoints: Never Reprocess the Same File
# MAGIC
# MAGIC Autoloader tracks which files have been processed:
# MAGIC ```
# MAGIC Checkpoint 1: Processed events_day1.csv (5000 rows)
# MAGIC Checkpoint 2: Processed events_day2.csv (5100 rows)
# MAGIC Checkpoint 3: File already in checkpoint → Skip! ✅
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 5: Unity Catalog Storage Access (Authentication)
# MAGIC
# MAGIC **Problem:** How does Databricks authenticate with ADLS Gen2?
# MAGIC
# MAGIC **Solution 1: User Auth** ❌
# MAGIC - Requires human login (not suitable for automated jobs)
# MAGIC - Scales poorly (one identity per person)
# MAGIC
# MAGIC **Solution 2: DBFS mount + service principal** ⚠️ (legacy)
# MAGIC - Works, but mounts are not supported on serverless compute
# MAGIC - Requires juggling client id / secret / tenant in a secret scope
# MAGIC
# MAGIC **Solution 3: Unity Catalog external location** ✅ (used here)
# MAGIC - A storage credential wraps an Azure Databricks **Access Connector**
# MAGIC   (managed identity) — no client secret to manage
# MAGIC - UC governs `abfss://` access with grants; works on serverless compute
# MAGIC - Created once in `notebooks/setup/00_unity_catalog_setup.py`
# MAGIC
# MAGIC ### UC Storage Access Setup Flow
# MAGIC ```
# MAGIC 1. Create an Azure Databricks Access Connector (managed identity)
# MAGIC    └─ Assign "Storage Blob Data Contributor" on the ADLS container
# MAGIC
# MAGIC 2. CREATE STORAGE CREDENTIAL (wraps the Access Connector)
# MAGIC
# MAGIC 3. CREATE EXTERNAL LOCATION 'abfss://datalake@lrlstorage01...'
# MAGIC    └─ UC now governs reads/writes via grants
# MAGIC
# MAGIC 4. DLT Autoloader reads the abfss:// path directly
# MAGIC    └─ No mount, no Spark config — serverless-friendly!
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 6: Create the DLT Pipeline
# MAGIC
# MAGIC ### Step 1: Register the pipeline (point it at the code)
# MAGIC
# MAGIC The DLT pipeline is defined in `src/dlt/bronze_pipeline.py`. **Don't run that
# MAGIC file** — register it as a pipeline so DLT runs it for you.
# MAGIC
# MAGIC In the newer Databricks UI (Lakeflow), it's a **two-phase** flow:
# MAGIC
# MAGIC **Phase 1 — create:** Click **+ New → ETL pipeline** (or **Jobs & Pipelines →
# MAGIC Create → ETL pipeline**). Choose **"Start with an empty pipeline"** (Blank, *not*
# MAGIC the sample). Set:
# MAGIC    - **Name**: `lives-remaining-bronze-ingestion`
# MAGIC    - **Default catalog**: `labs`  ·  **Default schema**: `bronze`
# MAGIC    - **Compute**: Serverless (default)
# MAGIC
# MAGIC **Phase 2 — add source:** Open the pipeline's **Settings** (gear) → **Source
# MAGIC code / Paths** → **Add**
# MAGIC `/Workspace/Users/<you>/LivesRemaining-Labs/src/dlt/bronze_pipeline.py`, remove any
# MAGIC auto-added sample path, and **Save**. (Triggered vs Continuous isn't a create-time
# MAGIC field — clicking **Run pipeline** does a triggered run.)
# MAGIC
# MAGIC ### Step 2: Define the ADLS Gen2 source path
# MAGIC
# MAGIC We read ADLS Gen2 directly through the Unity Catalog external location
# MAGIC (no mount). Verify the external location is reachable:

# COMMAND ----------

EVENTS_PATH = "abfss://datalake@lrlstorage01.dfs.core.windows.net/events/"

try:
    dbutils.fs.ls(EVENTS_PATH.rsplit("/events/", 1)[0] + "/")
    print(f"✅ External location is reachable: {EVENTS_PATH}")
except Exception as e:
    print("❌ Cannot reach the external location. Run notebooks/setup/00_unity_catalog_setup.py")
    print(f"   and confirm the storage credential + external location exist. Details: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step 3: Verify Data Exists in ADLS

# COMMAND ----------

try:
    files = dbutils.fs.ls(EVENTS_PATH)
    print(f"✅ Found {len(files)} files in {EVENTS_PATH}:")
    for f in files[:5]:
        print(f"  - {f.name}")
except:
    print(f"❌ No files found in {EVENTS_PATH}. Upload raw_events.csv (see Lab 0).")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step 4: Test CSV Reading (Before DLT)
# MAGIC
# MAGIC Let's manually read the CSV to verify schema inference works:

# COMMAND ----------

# Read CSV with schema inference
df_test = spark.read.option("header", "true").option("inferSchema", "true").csv(EVENTS_PATH + "raw_events.csv")

print(f"✅ Successfully read CSV! Shape: {df_test.count()} rows, {len(df_test.columns)} columns")
print(f"\nColumns and types:")
df_test.printSchema()

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step 5: Preview Sample Data

# COMMAND ----------

display(df_test.limit(10))

# COMMAND ----------

# MAGIC %md
# MAGIC ### Step 6: Check Data Quality

# COMMAND ----------

# Event type distribution
event_dist = df_test.groupBy("event_type").count().orderBy("count", ascending=False)
display(event_dist)

# COMMAND ----------

# MAGIC %md
# MAGIC Check for nulls (missing values):

# COMMAND ----------

from pyspark.sql.functions import col, count, when

null_counts = df_test.select([
    count(when(col(c).isNull(), c)).alias(c)
    for c in df_test.columns
])
display(null_counts)

# COMMAND ----------

# MAGIC %md
# MAGIC Verify event_type values (should match our expectations):

# COMMAND ----------

df_test.select("event_type").distinct().show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 7: Run DLT Pipeline
# MAGIC
# MAGIC In Databricks UI:
# MAGIC 1. Open **Jobs & Pipelines** and select `lives-remaining-bronze-ingestion`
# MAGIC 2. Click **Start** (a.k.a. **Run pipeline** / **Run all** in the newer UI)
# MAGIC 3. Monitor progress in the DAG view:
# MAGIC    - `bronze_events` table creation
# MAGIC    - Quality expectations (passing/failing rows)
# MAGIC    - `events_quality_metrics` summary
# MAGIC
# MAGIC Expected output:
# MAGIC ```
# MAGIC live.lives_remaining_raw_events: 100000 rows
# MAGIC ├─ Expectation "valid_event_id": 100000 passed ✅
# MAGIC ├─ Expectation "valid_player_id": 100000 passed ✅
# MAGIC └─ Expectation "valid_event_type": 100000 passed ✅
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 8: Verify Bronze Table Created
# MAGIC
# MAGIC After DLT runs successfully, query the bronze table:

# COMMAND ----------

# Query Unity Catalog bronze table
df_bronze = spark.sql("SELECT * FROM labs.bronze.lives_remaining_raw_events LIMIT 10")
display(df_bronze)

# COMMAND ----------

# MAGIC %md
# MAGIC Row count and summary:

# COMMAND ----------

spark.sql("""
SELECT 
  COUNT(*) as total_rows,
  COUNT(DISTINCT player_id) as unique_players,
  MIN(timestamp) as earliest_event,
  MAX(timestamp) as latest_event
FROM labs.bronze.lives_remaining_raw_events
""").show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 9: Test Incrementality (Autoloader)
# MAGIC
# MAGIC Autoloader is designed for incremental ingestion. To test:
# MAGIC
# MAGIC 1. **First run:** Ingest all rows (cold start)
# MAGIC 2. **Upload new file** to `abfss://datalake@lrlstorage01.dfs.core.windows.net/events/new_events.csv`
# MAGIC 3. **Second run:** Only new file is processed (checkpoint prevents reprocessing)
# MAGIC
# MAGIC **Why this matters:**
# MAGIC - Day 1: 100k events ingested
# MAGIC - Day 2: 5k new events uploaded → only 5k processed ✅ (not all 105k)
# MAGIC - Saves compute, faster pipeline, lower cost

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 10: Quality Expectations Deep Dive
# MAGIC
# MAGIC Our DLT pipeline includes 3 quality checks:
# MAGIC
# MAGIC ```python
# MAGIC @dlt.expect_or_drop("valid_event_id", "event_id IS NOT NULL")
# MAGIC @dlt.expect_or_drop("valid_player_id", "player_id IS NOT NULL")
# MAGIC @dlt.expect_or_drop("valid_event_type", "event_type IN ('login', ...)")
# MAGIC ```
# MAGIC
# MAGIC **What @dlt.expect_or_drop does:**
# MAGIC - ✅ Pass: Row satisfies condition → Keep row
# MAGIC - ❌ Fail: Row violates condition → Drop row
# MAGIC
# MAGIC Alternatives:
# MAGIC - `@dlt.expect_or_fail()` — Stop pipeline if any fail
# MAGIC - `@dlt.expect()` — Track failures, keep rows anyway
# MAGIC
# MAGIC View expectations results in DLT UI:
# MAGIC 1. Click on table in DAG
# MAGIC 2. See "Expectations" tab
# MAGIC 3. % passed / failed for each rule

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 11: Troubleshooting
# MAGIC
# MAGIC ### Issue: "ModuleNotFoundError: No module named 'dlt'"
# MAGIC **Cause:** You ran `src/dlt/bronze_pipeline.py` directly on a cluster/notebook.
# MAGIC The `dlt` module only exists inside the DLT pipeline runtime.
# MAGIC **Solution:** Don't run that file directly. Register it as a DLT pipeline
# MAGIC (Part 6) and **Start** it (Part 7). This notebook (`01_ingest_bronze.py`) is the
# MAGIC only one you run interactively.
# MAGIC
# MAGIC ### Issue: "Cannot reach the external location" / access denied
# MAGIC **Solution:** Run notebooks/setup/00_unity_catalog_setup.py to create the storage
# MAGIC credential + external location, and confirm the Access Connector has
# MAGIC "Storage Blob Data Contributor" on the storage account.
# MAGIC
# MAGIC ### Issue: "No files found in .../events/"
# MAGIC **Solution:** Land `raw_events.csv` first by completing **Lab 0**:
# MAGIC - **Option A (local):** `az storage fs file upload` / `azcopy` from your machine.
# MAGIC - **Option B (notebook):** run `notebooks/setup/01_generate_events.py` on
# MAGIC   serverless — it writes straight to `events/` via Spark (no local files).
# MAGIC
# MAGIC ### Issue: DLT pipeline fails with schema mismatch
# MAGIC **Solution:** Use explicit schema (not inferSchema). See bronze_pipeline.py for schema definition.
# MAGIC
# MAGIC ### Issue: Expected data not showing up
# MAGIC **Solution:**
# MAGIC 1. Check DLT logs: Jobs & Pipelines → your pipeline → Logs / event log
# MAGIC 2. Verify checkpoint: `dbutils.fs.ls("abfss://datalake@lrlstorage01.dfs.core.windows.net/.checkpoints/")`
# MAGIC 3. Check schema location: `dbutils.fs.ls("abfss://datalake@lrlstorage01.dfs.core.windows.net/.checkpoints/events/")`

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC
# MAGIC ✅ **Learned:**
# MAGIC - Bronze layer: Raw data preservation & audit trail
# MAGIC - Delta Lake: ACID tables with time travel
# MAGIC - DLT: Declarative ETL with automatic checkpoint/schema handling
# MAGIC - Autoloader: Incremental cloud file ingestion
# MAGIC - Unity Catalog external locations: governed `abfss://` access via a managed
# MAGIC   identity (Access Connector) — no mount, no service principal, serverless-ready
# MAGIC
# MAGIC ✅ **Built:**
# MAGIC - DLT pipeline: `src/dlt/bronze_pipeline.py`
# MAGIC - Bronze table: `labs.bronze.lives_remaining_raw_events`
# MAGIC - Quality expectations: 3 data validation rules
# MAGIC
# MAGIC 📚 **Next:** Lab 2 — Silver Transformations (Lab 2: cleaning & quality checks)
# MAGIC
# MAGIC 🔗 **References:**
# MAGIC - [DLT Docs](https://docs.databricks.com/en/delta-live-tables/)
# MAGIC - [Autoloader](https://docs.databricks.com/en/ingestion/auto-loader/)
# MAGIC - [Azure Setup Guide](setup-azure.md)

# COMMAND ----------
