# Databricks notebook source
# COMMAND ----------

# MAGIC %md
# MAGIC # Lab 6: Power BI Dashboards & Fabric Integration
# MAGIC ## Lives Remaining Labs — Azure Databricks
# MAGIC
# MAGIC **Goal:** Prepare SQL views and dashboard specs for Power BI/Fabric dashboards over Gold tables.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 1: Create BI-Friendly Views
# MAGIC
# MAGIC These views keep Power BI models simple and stable. Run them in a Databricks SQL warehouse or notebook attached to a cluster.

# COMMAND ----------

spark.sql("""
CREATE OR REPLACE VIEW labs.gold.vw_retention_churn AS
SELECT
  compute_date,
  region_primary AS region,
  platform_primary AS platform,
  risk_tier,
  COUNT(*) AS players,
  AVG(churn_probability) AS avg_churn_probability,
  AVG(days_since_login) AS avg_days_since_login,
  AVG(total_spend_30d) AS avg_spend_30d
FROM labs.gold.player_churn_scores
GROUP BY compute_date, region_primary, platform_primary, risk_tier
""")

spark.sql("""
CREATE OR REPLACE VIEW labs.gold.vw_player_segments AS
SELECT
  compute_date,
  region_primary AS region,
  platform_primary AS platform,
  engagement_segment,
  revenue_segment,
  COUNT(*) AS players,
  AVG(avg_session_duration_7d) AS avg_session_duration_7d,
  AVG(win_rate_7d) AS avg_win_rate_7d
FROM labs.gold.player_segments
GROUP BY compute_date, region_primary, platform_primary, engagement_segment, revenue_segment
""")

spark.sql("""
CREATE OR REPLACE VIEW labs.gold.vw_arpu_summary AS
SELECT
  compute_date,
  premium_tier,
  COUNT(*) AS paying_players,
  AVG(avg_spend_7d) AS avg_spend_7d,
  AVG(avg_spend_30d) AS avg_spend_30d,
  SUM(total_spend_90d) AS total_spend_90d,
  AVG(purchase_frequency_30d) AS avg_purchase_frequency_30d
FROM labs.gold.arpu_features_daily
GROUP BY compute_date, premium_tier
""")

print("Created Power BI views in labs.gold")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 2: Validate Views

# COMMAND ----------

display(spark.table("labs.gold.vw_retention_churn"))

# COMMAND ----------

display(spark.table("labs.gold.vw_arpu_summary"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 3: Power BI Model
# MAGIC
# MAGIC Connect Power BI Desktop:
# MAGIC 1. **Get Data** > **Azure Databricks**.
# MAGIC 2. Enter the Databricks SQL warehouse server hostname and HTTP path.
# MAGIC 3. Choose **DirectQuery** for fresh operational views, or **Import** for faster demos.
# MAGIC 4. Select:
# MAGIC    - `labs.gold.vw_retention_churn`
# MAGIC    - `labs.gold.vw_player_segments`
# MAGIC    - `labs.gold.vw_arpu_summary`
# MAGIC    - `labs.gold.player_churn_scores`

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 4: Suggested Measures
# MAGIC
# MAGIC ```DAX
# MAGIC Players = SUM(vw_retention_churn[players])
# MAGIC Avg Churn Probability = AVERAGE(vw_retention_churn[avg_churn_probability])
# MAGIC High Risk Players = CALCULATE([Players], vw_retention_churn[risk_tier] = "high")
# MAGIC High Risk Share = DIVIDE([High Risk Players], [Players])
# MAGIC ARPU 30D = AVERAGE(vw_arpu_summary[avg_spend_30d])
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 5: Dashboard Pages
# MAGIC
# MAGIC | Page | Visuals | Primary table/view |
# MAGIC |---|---|---|
# MAGIC | Retention & Churn | KPI cards, risk tier stacked bar, region heatmap | `vw_retention_churn` |
# MAGIC | Revenue & ARPU | Premium tier bar, revenue trend, whale count | `vw_arpu_summary` |
# MAGIC | Engagement | Session duration and win-rate by segment | `vw_player_segments` |
# MAGIC | Player Drillthrough | Player-level score and recommended action | `player_churn_scores` |
# MAGIC
# MAGIC ## Summary
# MAGIC
# MAGIC You created stable BI views and a dashboard design. Publish the report to Power BI Service and schedule refresh after the Databricks scoring job.
