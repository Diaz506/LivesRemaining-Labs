# Databricks notebook source
# COMMAND ----------

# MAGIC %md
# MAGIC # Lab 3: Feature Engineering for ML
# MAGIC ## Lives Remaining Labs — Azure Databricks
# MAGIC
# MAGIC **Goal:** Build Gold feature tables from Silver events and sessions.
# MAGIC
# MAGIC **Outputs:**
# MAGIC - `labs.gold.churn_features_daily`
# MAGIC - `labs.gold.arpu_features_daily`
# MAGIC - `labs.gold.player_segments`

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 1: Feature Design
# MAGIC
# MAGIC Churn features answer: **"What did the player do before today?"**
# MAGIC
# MAGIC | Feature family | Examples |
# MAGIC |---|---|
# MAGIC | Recency | `days_since_login` |
# MAGIC | Frequency | `login_count_7d`, `login_count_30d` |
# MAGIC | Engagement | `avg_session_duration_7d`, `total_playtime_7d` |
# MAGIC | Skill/activity | `kill_count_7d`, `match_count_7d`, `win_rate_7d` |
# MAGIC | Monetization | `avg_spend_7d`, `total_spend_30d` |
# MAGIC | Context | `platform_primary`, `region_primary` |

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 2: Run the Gold DLT Pipeline
# MAGIC
# MAGIC 1. Upload `src/dlt/gold_pipeline.py` to Databricks.
# MAGIC 2. Create DLT pipeline `lives-remaining-gold-features`.
# MAGIC 3. Target schema: `labs.gold`.
# MAGIC 4. Start the pipeline after Lab 2 has created Silver tables.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 3: Validate Churn Features

# COMMAND ----------

from pyspark.sql import functions as F

churn = spark.table("labs.gold.churn_features_daily")
display(churn.limit(20))

# COMMAND ----------

display(
    churn.select(
        F.count("*").alias("players"),
        F.round(F.avg("days_since_login"), 2).alias("avg_days_since_login"),
        F.round(F.avg("login_count_7d"), 2).alias("avg_logins_7d"),
        F.round(F.avg("total_playtime_7d"), 2).alias("avg_playtime_hours_7d"),
        F.round(F.avg("total_spend_30d"), 2).alias("avg_spend_30d"),
        F.round(F.avg("churn_label"), 4).alias("churn_rate"),
    )
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 4: Check for Leakage
# MAGIC
# MAGIC A feature table is safe for ML only when features are computed from activity before the label window.
# MAGIC This training lab uses a simplified label (`days_since_login >= 7`) so learners can focus on the end-to-end workflow.
# MAGIC For production, create historical snapshots with a `feature_window_end` and label the next 7 days separately.

# COMMAND ----------

display(
    churn.groupBy("churn_label")
    .agg(
        F.count("*").alias("players"),
        F.round(F.avg("login_count_7d"), 2).alias("avg_login_count_7d"),
        F.round(F.avg("avg_session_duration_7d"), 2).alias("avg_session_duration_7d"),
        F.round(F.avg("total_spend_30d"), 2).alias("avg_total_spend_30d"),
    )
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 5: Revenue Features

# COMMAND ----------

arpu = spark.table("labs.gold.arpu_features_daily")
display(arpu.limit(20))

# COMMAND ----------

display(
    arpu.groupBy("premium_tier")
    .agg(
        F.count("*").alias("players"),
        F.round(F.avg("total_spend_90d"), 2).alias("avg_spend_90d"),
        F.round(F.avg("purchase_frequency_30d"), 2).alias("avg_purchases_30d"),
    )
    .orderBy(F.desc("avg_spend_90d"))
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 6: Player Segments for BI

# COMMAND ----------

segments = spark.table("labs.gold.player_segments")
display(
    segments.groupBy("engagement_segment", "revenue_segment")
    .agg(F.count("*").alias("players"))
    .orderBy("engagement_segment", "revenue_segment")
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC
# MAGIC You created reusable Gold feature tables. Lab 4 uses `churn_features_daily` to train and register a churn model with MLflow.
