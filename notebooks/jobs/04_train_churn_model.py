# Databricks notebook source
# COMMAND ----------

# MAGIC %md
# MAGIC # Lab 4: Churn Prediction with MLflow
# MAGIC ## Lives Remaining Labs — Azure Databricks
# MAGIC
# MAGIC **Goal:** Train a churn classifier from Gold features, track metrics in MLflow, and register the model.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 1: Load Training Features

# COMMAND ----------

from pyspark.sql import functions as F

feature_table = "labs.gold.churn_features_daily"
model_name = "lives_remaining_churn_model"
experiment_name = "/Shared/lives-remaining/churn"

features = spark.table(feature_table)
display(features.limit(20))

# COMMAND ----------

display(
    features.groupBy("churn_label")
    .agg(
        F.count("*").alias("players"),
        F.round(F.avg("days_since_login"), 2).alias("avg_days_since_login"),
        F.round(F.avg("login_count_7d"), 2).alias("avg_logins_7d"),
    )
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 2: Train with MLflow

# COMMAND ----------

import mlflow
from pyspark.ml import Pipeline
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import BinaryClassificationEvaluator, MulticlassClassificationEvaluator
from pyspark.ml.feature import StringIndexer, VectorAssembler

feature_columns = [
    "days_since_login",
    "login_count_7d",
    "login_count_30d",
    "avg_session_duration_7d",
    "total_playtime_7d",
    "kill_count_7d",
    "match_count_7d",
    "win_rate_7d",
    "avg_spend_7d",
    "avg_spend_30d",
    "total_spend_30d",
]

training_df = (
    features.select("player_id", "churn_label", "platform_primary", "region_primary", *feature_columns)
    .fillna(0, subset=feature_columns)
    .fillna({"platform_primary": "Unknown", "region_primary": "Unknown"})
)

train_df, test_df = training_df.randomSplit([0.7, 0.3], seed=42)

pipeline = Pipeline(stages=[
    StringIndexer(inputCol="platform_primary", outputCol="platform_index", handleInvalid="keep"),
    StringIndexer(inputCol="region_primary", outputCol="region_index", handleInvalid="keep"),
    VectorAssembler(inputCols=feature_columns + ["platform_index", "region_index"], outputCol="features", handleInvalid="keep"),
    RandomForestClassifier(labelCol="churn_label", featuresCol="features", maxDepth=8, numTrees=80, seed=42),
])

mlflow.set_experiment(experiment_name)

with mlflow.start_run(run_name="random_forest_churn_notebook"):
    mlflow.log_param("feature_table", feature_table)
    mlflow.log_param("model_type", "RandomForestClassifier")
    mlflow.log_param("num_trees", 80)
    mlflow.log_param("max_depth", 8)

    model = pipeline.fit(train_df)
    predictions = model.transform(test_df)

    auc = BinaryClassificationEvaluator(labelCol="churn_label", metricName="areaUnderROC").evaluate(predictions)
    accuracy = MulticlassClassificationEvaluator(labelCol="churn_label", predictionCol="prediction", metricName="accuracy").evaluate(predictions)
    f1 = MulticlassClassificationEvaluator(labelCol="churn_label", predictionCol="prediction", metricName="f1").evaluate(predictions)

    mlflow.log_metric("auc", auc)
    mlflow.log_metric("accuracy", accuracy)
    mlflow.log_metric("f1", f1)
    mlflow.spark.log_model(model, artifact_path="model", registered_model_name=model_name)

print(f"Registered {model_name}: AUC={auc:.4f}, accuracy={accuracy:.4f}, f1={f1:.4f}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 3: Review Predictions

# COMMAND ----------

display(
    predictions.select("player_id", "churn_label", "prediction", "probability")
    .limit(20)
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 4: Productionize
# MAGIC
# MAGIC After reviewing metrics in the MLflow UI:
# MAGIC 1. Open **Experiments** > `/Shared/lives-remaining/churn`.
# MAGIC 2. Open the best run.
# MAGIC 3. Confirm model registration under `lives_remaining_churn_model`.
# MAGIC 4. Promote the desired version to **Production** or set a production alias.
# MAGIC
# MAGIC For scheduled training, create a Databricks Job that runs:
# MAGIC
# MAGIC ```bash
# MAGIC python src/jobs/train_churn_model.py --algorithm random_forest --num-trees 80 --max-depth 8
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC
# MAGIC You trained, evaluated, logged, and registered a churn model. Lab 5 loads the production model and scores active players daily.
