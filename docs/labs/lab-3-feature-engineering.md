# Lab 3: Feature Engineering for ML (Gold)

**Goal:** Build the Gold feature tables (`labs.gold.*`) that power the churn model, ARPU analysis, and BI segments.

⏱️ **Time:** ~1.5 hr &nbsp;|&nbsp; **Prerequisites:** [Lab 2](lab-2-silver-transformations.md)

---

### 🎯 Why this lab

ML models consume *features* (aggregated signals like `login_count_7d`, `avg_spend_30d`), not raw events. `src/dlt/gold_pipeline.py` rolls Silver data into per-player daily features and a **churn label**.

**Artifacts:** `src/dlt/gold_pipeline.py` (pipeline), `notebooks/dlt/03_feature_engineering_gold.py` (walkthrough).

**Outputs:**

| Table | Purpose |
|-------|---------|
| `labs.gold.churn_features_daily` | Features + `churn_label` (target) for Lab 4 |
| `labs.gold.arpu_features_daily` | Revenue / monetization features |
| `labs.gold.player_segments` | Engagement & revenue cohorts for BI |

---

## 🪜 Steps

### Step 1 — Confirm Silver exists

```sql
SELECT COUNT(*) FROM labs.silver.player_events_cleaned;
SELECT COUNT(*) FROM labs.silver.player_sessions;
```

### Step 2 — Understand the feature logic

Open `src/dlt/gold_pipeline.py`:
- `churn_features_daily` (lines 13–81): 7d/30d windows via `date_sub(current_date(), N)`, left-joins activity + session + spend features, then derives `days_since_login`, `is_new_player`, and `churn_label = 1 when days_since_login >= 7`.
- `arpu_features_daily` (lines 84–121): spend windows (7/30/90d), `premium_tier`, `is_whale` (≥ $250 in 90d).
- `player_segments` (lines 124–157): `engagement_segment` (core/regular/casual/lapsed) and `revenue_segment` (whale/spender/free).

> **Note on the label:** because the synthetic data spans a fixed 30-day window, `churn_label` is computed from recency. In production you would label against a *future* observation window to avoid leakage.

### Step 3 — Create the Gold DLT pipeline

**Workflows → Delta Live Tables → Create pipeline**:

| Setting | Value |
|---------|-------|
| Pipeline name | `lives-remaining-gold` |
| Source code | `…/src/dlt/gold_pipeline.py` |
| Destination | Catalog `labs`, Target schema `gold` |
| Pipeline mode | **Triggered** |

### Step 4 — Run it

Click **Start**. Confirm `churn_features_daily`, `arpu_features_daily`, and `player_segments` build green.

### Step 5 — Validate features and label balance

```sql
-- Label balance (need both classes for Lab 4)
SELECT churn_label, COUNT(*) AS players
FROM labs.gold.churn_features_daily GROUP BY churn_label;

-- Feature sanity
SELECT ROUND(AVG(login_count_7d),2) avg_logins_7d,
       ROUND(AVG(days_since_login),1) avg_recency,
       ROUND(AVG(avg_spend_30d),2) avg_spend_30d
FROM labs.gold.churn_features_daily;

-- Segments
SELECT engagement_segment, revenue_segment, COUNT(*)
FROM labs.gold.player_segments GROUP BY engagement_segment, revenue_segment ORDER BY 3 DESC;
```

Run the equivalent cells in `notebooks/dlt/03_feature_engineering_gold.py`.

### Step 6 (optional) — Schedule daily refresh

Create a **Workflow** that triggers this pipeline daily at **01:00 UTC** (before Lab 5's 02:00 scoring job). Use a job cluster for cost.

---

## ✅ Done when

- [ ] All three `labs.gold.*` tables are populated
- [ ] `churn_label` has **both** 0 and 1 classes (required to train)
- [ ] Segment counts look reasonable across cohorts

## 🧯 Troubleshooting

| Symptom | Fix |
|---------|-----|
| Only one `churn_label` class | Regenerate Lab 0 data with a wider `--days` span so some players lapse. |
| All spend features 0 | Confirm `labs.silver.player_purchase_events` has rows (Lab 2). |
| `Table not found: labs.silver...` | Re-run Lab 2. |

**Next:** [Lab 4 — Churn prediction with MLflow →](lab-4-churn-prediction.md)
