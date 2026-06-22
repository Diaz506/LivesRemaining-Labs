# Databricks notebook source
# COMMAND ----------

# MAGIC %md
# MAGIC # Lab 7: Real-Time Scoring Endpoint (Optional)
# MAGIC ## Lives Remaining Labs — Azure Databricks
# MAGIC
# MAGIC **Goal:** Deploy the registered churn model as a Databricks Model Serving endpoint and test live scoring.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 1: Confirm Registered Model Version
# MAGIC
# MAGIC In MLflow Model Registry, open `lives_remaining_churn_model` and select the version you want to serve.
# MAGIC The helper script needs a concrete model version because endpoint configs are immutable and auditable.

# COMMAND ----------

model_name = "lives_remaining_churn_model"
endpoint_name = "lives-remaining-churn"
model_version = "1"  # Replace with your promoted model version.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 2: Create the Endpoint
# MAGIC
# MAGIC Recommended for this lab:
# MAGIC - Workload size: Small
# MAGIC - Scale to zero: enabled for cost control
# MAGIC - Auth: Databricks token or service principal token stored securely
# MAGIC
# MAGIC Run as a Databricks job or local shell after setting `DATABRICKS_HOST` and `DATABRICKS_TOKEN`:
# MAGIC
# MAGIC ```bash
# MAGIC python src/jobs/create_serving_endpoint.py \
# MAGIC   --endpoint-name lives-remaining-churn \
# MAGIC   --model-name lives_remaining_churn_model \
# MAGIC   --model-version 1 \
# MAGIC   --scale-to-zero
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 3: Build a Sample Request

# COMMAND ----------

sample = (
    spark.table("labs.gold.churn_features_daily")
    .limit(1)
    .toPandas()
    .drop(columns=["churn_label"], errors="ignore")
)

sample_payload = {"dataframe_records": sample.to_dict(orient="records")}
sample_payload

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 4: Call the Endpoint
# MAGIC
# MAGIC Use a token from a secure secret scope. Do not hard-code tokens in notebooks.

# COMMAND ----------

import requests

workspace_url = "https://<your-workspace-host>"
token = dbutils.secrets.get(scope="<secret-scope>", key="<databricks-token>")

response = requests.post(
    f"{workspace_url}/serving-endpoints/{endpoint_name}/invocations",
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    json=sample_payload,
    timeout=30,
)
response.raise_for_status()
response.json()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 5: Operational Guidance
# MAGIC
# MAGIC - Use batch scoring for daily retention campaigns.
# MAGIC - Use real-time scoring only for low-latency in-game or support workflows.
# MAGIC - Monitor endpoint latency, request volume, and error rate in the Serving UI.
# MAGIC - Keep scale-to-zero enabled for demos; disable it if cold-start latency is unacceptable.
# MAGIC
# MAGIC ## Summary
# MAGIC
# MAGIC You deployed the churn model behind a REST endpoint and tested a live request.
