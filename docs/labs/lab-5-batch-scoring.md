# Lab 5: Batch Scoring & Predictions

### 🎯 Why This Lab?

Trained model is in registry. Now **deploy it to production** by:
- Loading model from registry
- Scoring all active players daily
- Writing predictions to Delta table
- Scheduling as automated job

Batch vs. real-time scoring:
- **Batch**: Process all players nightly (cheaper, simpler)
- **Real-time**: Score on-demand via API (Lab 7, optional)
- We use batch for daily churn predictions

### 📚 Concepts

**Model Loading from MLflow:**
```python
import mlflow
model = mlflow.pyfunc.load_model("models:/churn_model/Production")
predictions = model.predict(feature_df)
```

**Batch Predictions:**
- Load model once
- Score all rows at once (efficient)
- Write results to Delta table
- Pandas UDF for parallelization (faster)

**Databricks Jobs:**
- Scheduled tasks in Databricks workspace
- Can run notebooks or .py scripts
- Supports job parameters, email alerts, retries
- Pricing: Seconds-based (cheaper than all-purpose clusters)

**Incremental Updates:**
- Don't re-score all history daily (wasteful)
- Only score new/updated players
- Merge results into existing table

### 🔧 Goal

Create daily batch scoring job that scores all players & writes to Delta.

### 📋 Deliverables

- `src/jobs/batch_score_churn.py` — scoring script
- `notebooks/jobs/05_batch_scoring.py` — interactive scoring walkthrough
- `player_churn_scores` table (`player_id`, `churn_probability`, `risk_tier`)
- Scheduled Databricks Job (runs 2 AM UTC daily)

### ☁️ Azure Tasks

- Create Databricks Job with schedule (2 AM UTC)
- Monitor job runs in workspace UI
- (Optional) Set up alerts via Azure Monitor

### 🔑 Key Terms

- **Model promotion**: Move model from Staging → Production (in registry)
- **Batch inference**: Score many rows at once
- **Pandas UDF**: Distributed function for fast vectorized scoring
- **Incremental**: Only process new data (efficient)
- **Risk tier**: Categorize churn probability (low/med/high)

### ⏱️ Time: ~1 hour

### 📖 Reference

- MLflow model loading: [Docs](https://mlflow.org/docs/latest/python_api/mlflow.pyfunc.html)
- Databricks Jobs: [Documentation](https://docs.databricks.com/en/workflows/jobs/jobs.html)
- Pandas UDF: [Performance guide](https://docs.databricks.com/en/udf/pandas.html)

### Prerequisites: Lab 4

---
