# Databricks notebook source
# COMMAND ----------

# MAGIC %md
# MAGIC # Lab 5: Batch Scoring & Predictions
# MAGIC ## Lives Remaining Labs — Azure Databricks
# MAGIC
# MAGIC **Goal:** Load the registered churn model, score the latest feature snapshot, and publish `labs.gold.player_churn_scores`.

# COMMAND ----------

import mlflow
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType

feature_table = "labs.gold.churn_features_daily"
output_table = "labs.gold.player_churn_scores"
model_uri = "models:/lives_remaining_churn_model/Production"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 1: Load Latest Features

# COMMAND ----------

latest_compute_date = spark.table(feature_table).agg(F.max("compute_date").alias("compute_date")).first()["compute_date"]
features = spark.table(feature_table).where(F.col("compute_date") == latest_compute_date)
display(features.limit(20))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 2: Score Players

# COMMAND ----------

@F.udf(DoubleType())
def churn_probability(probability):
    return float(probability[1]) if probability is not None and len(probability) > 1 else None

model = mlflow.spark.load_model(model_uri)

scored = (
    model.transform(features)
    .withColumn("churn_probability", churn_probability("probability"))
    .withColumn(
        "risk_tier",
        F.when(F.col("churn_probability") >= 0.75, "high")
        .when(F.col("churn_probability") >= 0.40, "medium")
        .otherwise("low"),
    )
    .withColumn("scored_at", F.current_timestamp())
    .select(
        "player_id",
        "compute_date",
        "scored_at",
        "churn_probability",
        "risk_tier",
        "days_since_login",
        "login_count_7d",
        "total_spend_30d",
        "platform_primary",
        "region_primary",
    )
)

display(scored.limit(20))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 3: Write Delta Output

# COMMAND ----------

(
    scored.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(output_table)
)

print(f"Wrote {scored.count():,} rows to {output_table}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 4: Operational Views

# COMMAND ----------

display(
    spark.table(output_table)
    .groupBy("risk_tier")
    .agg(
        F.count("*").alias("players"),
        F.round(F.avg("churn_probability"), 4).alias("avg_probability"),
        F.round(F.avg("total_spend_30d"), 2).alias("avg_spend_30d"),
    )
    .orderBy(F.desc("avg_probability"))
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 5: Schedule as a Databricks Job
# MAGIC
# MAGIC Create a Databricks Job:
# MAGIC - Task type: Python file
# MAGIC - Path: `/Workspace/src/jobs/batch_score_churn.py`
# MAGIC - Schedule: daily at 2 AM UTC
# MAGIC - Retries: 2
# MAGIC - Alert on failure
# MAGIC
# MAGIC ## Summary
# MAGIC
# MAGIC You created a production-style batch scoring table. Lab 6 connects Power BI to this table for retention dashboards.
