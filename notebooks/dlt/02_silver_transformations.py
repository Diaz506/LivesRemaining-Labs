# Databricks notebook source
# COMMAND ----------

# MAGIC %md
# MAGIC # Lab 2: Silver Transformations & Quality Checks
# MAGIC ## Lives Remaining Labs — Azure Databricks
# MAGIC
# MAGIC **Goal:** Convert raw Bronze player telemetry into trusted Silver event and session tables.
# MAGIC
# MAGIC **You will build:**
# MAGIC - `labs.silver.player_events_cleaned`
# MAGIC - `labs.silver.player_sessions`
# MAGIC - `labs.silver.player_purchase_events`
# MAGIC - `labs.silver.silver_quality_summary`

# COMMAND ----------

# MAGIC %md
# MAGIC ## Prerequisites
# MAGIC - Lab 1 Bronze DLT pipeline has completed.
# MAGIC - `labs.bronze.lives_remaining_raw_events` exists in Unity Catalog.
# MAGIC - `src/dlt/silver_pipeline.py` is uploaded to the Databricks workspace.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 1: Inspect Bronze Quality

# COMMAND ----------

bronze = spark.table("labs.bronze.lives_remaining_raw_events")
display(bronze.limit(10))

# COMMAND ----------

from pyspark.sql import functions as F

display(
    bronze.groupBy("event_type")
    .agg(
        F.count("*").alias("events"),
        F.countDistinct("player_id").alias("players"),
        F.sum(F.when(F.col("payload").isNull(), 1).otherwise(0)).alias("missing_payloads"),
    )
    .orderBy(F.desc("events"))
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 2: What Silver Fixes
# MAGIC
# MAGIC Bronze intentionally preserves raw data. Silver makes the data safe to reuse:
# MAGIC
# MAGIC | Issue | Silver handling |
# MAGIC |---|---|
# MAGIC | String timestamps | Cast to `timestamp` and `date` |
# MAGIC | Duplicate events | Drop duplicate `event_id` values |
# MAGIC | JSON payloads | Extract common fields such as weapon and purchase amount |
# MAGIC | Bad event types | Drop records that fail DLT expectations |
# MAGIC | Session metrics hidden in payload | Publish `player_sessions` facts |

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 3: Create the Silver DLT Pipeline
# MAGIC
# MAGIC In Databricks:
# MAGIC 1. Go to **Workflows** > **Delta Live Tables** > **Create pipeline**.
# MAGIC 2. Name: `lives-remaining-silver-transformations`.
# MAGIC 3. Source path: `/Workspace/src/dlt/silver_pipeline.py`.
# MAGIC 4. Target: `labs.silver`.
# MAGIC 5. Configure the pipeline to read from the same catalog where Lab 1 created Bronze.
# MAGIC 6. Start the pipeline and watch expectation metrics in the DAG.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 4: Verify Cleaned Events

# COMMAND ----------

cleaned = spark.table("labs.silver.player_events_cleaned")
display(cleaned.limit(20))

# COMMAND ----------

display(
    cleaned.select(
        F.count("*").alias("rows"),
        F.countDistinct("event_id").alias("unique_events"),
        F.countDistinct("player_id").alias("unique_players"),
        F.min("event_ts").alias("first_event"),
        F.max("event_ts").alias("last_event"),
    )
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 5: Explore Parsed Payload Fields

# COMMAND ----------

display(
    cleaned.where("event_type_normalized = 'kill'")
    .select("player_id", "event_ts", "opponent_id", "weapon", "headshot", "experience_granted")
    .limit(20)
)

# COMMAND ----------

display(
    spark.table("labs.silver.player_purchase_events")
    .groupBy("region", "platform")
    .agg(F.count("*").alias("purchases"), F.round(F.sum("item_price_usd"), 2).alias("revenue_usd"))
    .orderBy(F.desc("revenue_usd"))
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 6: Session Analytics

# COMMAND ----------

sessions = spark.table("labs.silver.player_sessions")
display(sessions.limit(20))

# COMMAND ----------

display(
    sessions.groupBy("region", "platform")
    .agg(
        F.count("*").alias("sessions"),
        F.round(F.avg("duration_min"), 2).alias("avg_duration_min"),
        F.round(F.avg("kd_ratio"), 2).alias("avg_kd_ratio"),
        F.round(F.avg("win_rate"), 2).alias("avg_win_rate"),
    )
    .orderBy(F.desc("sessions"))
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 7: Quality Summary

# COMMAND ----------

display(spark.table("labs.silver.silver_quality_summary").orderBy("event_date", "event_type_normalized"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Troubleshooting
# MAGIC
# MAGIC - **Table not found:** Run Lab 1 and confirm the target schema is `labs.bronze`.
# MAGIC - **DLT cannot resolve Bronze table:** Put Bronze and Silver in one pipeline, or reference the fully qualified Bronze table in `silver_pipeline.py`.
# MAGIC - **Unexpected null parsed fields:** Check that `payload` contains valid JSON strings in Bronze.
# MAGIC
# MAGIC ## Summary
# MAGIC
# MAGIC You created the trusted Silver layer and are ready to build Gold ML features in Lab 3.
