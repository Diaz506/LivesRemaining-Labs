# Lab 5: Batch Scoring & Predictions

**Goal:** Load the production churn model, score the latest features, and publish `labs.gold.player_churn_scores` for Power BI and retention workflows.

⏱️ **Time:** ~1 hr &nbsp;|&nbsp; **Prerequisites:** [Lab 4](lab-4-churn-prediction.md)

---

### 🎯 Why this lab

A registered model has no value until it produces predictions. Batch scoring runs nightly, scores every active player, and writes a Delta table the business can act on (downstream of `churn_features_daily`, upstream of dashboards).

**Artifacts:** `notebooks/jobs/05_batch_scoring.py` (interactive) and `src/jobs/batch_score_churn.py` (job).

**Output:** `labs.gold.player_churn_scores` — `player_id, compute_date, scored_at, churn_probability, risk_tier, days_since_login, login_count_7d, total_spend_30d, platform_primary, region_primary`.

---

## 🪜 Steps

### Step 1 — Confirm a Production model exists

```python
import mlflow
mlflow.spark.load_model("models:/lives_remaining_churn_model/Production")
```

If this fails, promote a version in Lab 4 Step 6.

### Step 2 — Open the scoring notebook

Open `notebooks/jobs/05_batch_scoring.py`. Confirm the config:

```python
feature_table = "labs.gold.churn_features_daily"
output_table  = "labs.gold.player_churn_scores"
model_uri     = "models:/lives_remaining_churn_model/Production"
```

### Step 3 — Score the latest snapshot

Run the notebook. It (see `src/jobs/batch_score_churn.py:31-65`):
1. Finds `MAX(compute_date)` in the feature table
2. Loads the Production model and `transform`s those features
3. Extracts `churn_probability` from the probability vector
4. Buckets `risk_tier`: `high ≥ 0.75`, `medium ≥ 0.40`, else `low`
5. Writes `labs.gold.player_churn_scores` (overwrite)

### Step 4 — Validate predictions

```sql
SELECT risk_tier, COUNT(*) AS players, ROUND(AVG(churn_probability),3) AS avg_prob
FROM labs.gold.player_churn_scores
GROUP BY risk_tier ORDER BY avg_prob DESC;

-- Top at-risk, high-value players (retention target list)
SELECT player_id, churn_probability, total_spend_30d, days_since_login
FROM labs.gold.player_churn_scores
WHERE risk_tier = 'high'
ORDER BY total_spend_30d DESC LIMIT 20;
```

### Step 5 — Schedule the job (2 AM UTC daily)

**Workflows → Jobs → Create job**:

| Setting | Value |
|---------|-------|
| Task type | Python script / Notebook |
| Script | `src/jobs/batch_score_churn.py` (or notebook `05_batch_scoring.py`) |
| Parameters | `--model-uri models:/lives_remaining_churn_model/Production` |
| Schedule | Cron `0 2 * * *` (02:00 UTC) |
| Cluster | Job cluster (cost-efficient) |

This runs *after* the Gold refresh (Lab 3, 01:00) and *before* the Power BI refresh (Lab 6, 03:00).

---

## ✅ Done when

- [ ] `labs.gold.player_churn_scores` is populated for the latest `compute_date`
- [ ] `risk_tier` distribution looks reasonable (most `low`, fewer `high`)
- [ ] A scheduled job is created (or run manually at least once)

## 🧯 Troubleshooting

| Symptom | Fix |
|---------|-----|
| `Production` model not found | Promote a version in Lab 4. |
| `churn_probability` all null | The model's `probability` vector is missing — confirm a classifier (not regressor) was registered. |
| Schema mismatch on write | The job uses `overwriteSchema=true`; drop the table if it was created with an old schema. |

**Next:** [Lab 6 — Power BI dashboards →](lab-6-powerbi-dashboards.md)
