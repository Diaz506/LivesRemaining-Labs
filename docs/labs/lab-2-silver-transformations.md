# Lab 2: Silver Transformations & Quality Checks

### 🎯 Why This Lab?

Bronze data is messy (inconsistent formats, nulls, duplicates). **Silver layer** cleans and normalizes:
- Standardizes types (e.g., date strings → timestamp)
- Deduplicates records
- Applies business logic (e.g., compute session duration)
- Validates data quality with expectations

### 📚 Concepts

**Bronze → Silver → Gold (Medallion Architecture):**
- **Bronze**: Raw, as-is (no guarantees)
- **Silver**: Cleaned, deduplicated (trustworthy)
- **Gold**: Business-ready aggregates (for analytics/ML)
- Why this pattern? Separation of concerns, reusability, auditability

**DLT Expectations (Quality Checks):**
- Expectations are business rules (e.g., "kill_count must be ≥ 0")
- DLT tracks which records pass/fail
- Failed records can be quarantined or rejected
- Provides data quality metrics

**Slowly Changing Dimensions (SCD):**
- Tracks how entity attributes change over time
- Type 1: Overwrite old values (no history)
- Type 2: Keep history (add new rows with dates)
- Used for player profiles (level-ups, tier promotions)

**PySpark Transformations:**
- `withColumn()`: Add/modify column
- `select()`: Project specific columns
- `where()`: Filter rows
- `groupBy().agg()`: Aggregate
- Window functions: `over(Window.partitionBy(...).orderBy(...))`

### 🔧 Goal

Transform Bronze events into clean **Silver tables** with quality checks & aggregations.

### 📋 Deliverables

- `src/dlt/silver_pipeline.py` — transformation code
- Silver tables:
  - `player_sessions` — session-level aggregates
  - `player_events_cleaned` — deduplicated, normalized events
- Quality report (expectations passed/failed)

### ☁️ Azure Tasks

- Monitor cluster metrics in Databricks workspace
- Check job run history & logs
- View expectations results in DLT UI

### 🔑 Key Terms

- **Medallion Architecture**: Bronze → Silver → Gold layering
- **Expectation**: Data quality rule (DLT feature)
- **SCD (Slowly Changing Dimension)**: Temporal tracking of entities
- **Deduplication**: Removing duplicate rows (common in event streams)
- **Window function**: Compute over rows partitioned by key (e.g., avg per player)

### ⏱️ Time: ~1.5 hours

### 📖 Reference

- PySpark: [DataFrame API](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql.DataFrame.html)
- DLT Expectations: [Data quality monitoring](https://docs.databricks.com/en/delta-live-tables/expectations.html)
- Medallion Architecture: [Best practices](https://www.databricks.com/blog/2022/06/24/multi-hop-architecture-is-modular-and-scalable.html)

### Prerequisites: Lab 1

---
