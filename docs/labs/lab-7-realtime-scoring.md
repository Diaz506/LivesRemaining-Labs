# Lab 7: Real-Time Scoring Endpoint (Optional)

**Goal:** Deploy the registered churn model behind a Databricks Model Serving REST endpoint and test a live request.

⏱️ **Time:** ~1.5 hr &nbsp;|&nbsp; **Prerequisites:** [Lab 4](lab-4-churn-prediction.md)

---

### 🎯 Why this lab

Batch scoring (Lab 5) is daily. Some use cases need *live* risk scores: in-game churn UI, real-time retention offers, A/B intervention tests. Databricks Model Serving exposes the model as an auto-scaling REST API.

**Artifacts:** `src/jobs/create_serving_endpoint.py` (deploy helper) and `notebooks/jobs/07_realtime_scoring_endpoint.py` (walkthrough + test client).

---

## 🪜 Steps

### Step 1 — Pick the model version to serve

In **Models → `lives_remaining_churn_model`**, note the concrete **version number** you promoted in Lab 4 (endpoint configs pin an explicit version).

### Step 2 — Set credentials

Export a PAT or service-principal token with permission to manage serving endpoints:

```bash
export DATABRICKS_HOST="https://<your-workspace-host>"
export DATABRICKS_TOKEN="<token>"
```

### Step 3 — Create the endpoint

```bash
python src/jobs/create_serving_endpoint.py \
  --endpoint-name lives-remaining-churn \
  --model-name lives_remaining_churn_model \
  --model-version <version> \
  --workload-size Small \
  --scale-to-zero
```

The script creates (or updates) the endpoint, then polls until **READY** (see `create_serving_endpoint.py:63-71`):

```
Created endpoint lives-remaining-churn
Endpoint state: NOT_READY
...
Endpoint state: READY
```

### Step 4 — Build a sample request

In `notebooks/jobs/07_realtime_scoring_endpoint.py` run Part 3 to build a payload from one feature row:

```python
sample = spark.table("labs.gold.churn_features_daily").limit(1).toPandas().drop(columns=["churn_label"], errors="ignore")
sample_payload = {"dataframe_records": sample.to_dict(orient="records")}
```

### Step 5 — Call the endpoint

Run Part 4 (use a token from a **secret scope**, never hard-coded):

```python
import requests
token = dbutils.secrets.get(scope="lrl", key="serving-token")
resp = requests.post(
  f"{workspace_url}/serving-endpoints/lives-remaining-churn/invocations",
  headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
  json=sample_payload, timeout=30)
resp.raise_for_status(); resp.json()
```

Expect a JSON `predictions` array.

### Step 6 — Check latency and operate

In **Serving → lives-remaining-churn**, review request volume, latency (P50/P95), and errors. Keep **scale-to-zero** on for demos (accept cold starts); disable it if you need consistently low latency.

---

## ✅ Done when

- [ ] Endpoint `lives-remaining-churn` reaches **READY**
- [ ] A sample request returns predictions
- [ ] You've reviewed latency/throughput in the Serving UI

## 🧯 Troubleshooting

| Symptom | Fix |
|---------|-----|
| `KeyError: DATABRICKS_HOST` | Export `DATABRICKS_HOST` / `DATABRICKS_TOKEN` (Step 2). |
| `404` on invocation | Endpoint not READY yet, or wrong endpoint name. |
| `401/403` | Token lacks serving permissions; use a valid PAT / SP token. |
| High cold-start latency | Disable scale-to-zero or use a larger workload size. |

**You've completed the Lives Remaining Labs end-to-end pipeline. 🎉**
