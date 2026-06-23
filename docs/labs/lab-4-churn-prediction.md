# Lab 4: Churn Prediction with MLflow

**Goal:** Train a churn classifier on `labs.gold.churn_features_daily`, track it in MLflow, and register `lives_remaining_churn_model`.

⏱️ **Time:** ~2 hr &nbsp;|&nbsp; **Prerequisites:** [Lab 3](lab-3-feature-engineering.md)

> 🎮 **Mission Briefing**
>
> The retention team wants a churn early-warning system before the next content drop. Using the Gold features, you'll train and register a churn model in MLflow — and prove it actually separates the players who stay from the ones who leave.

---

### 🎯 Why this lab

MLflow gives you experiment tracking, metric comparison, model versioning, and a registry for promotion (dev → staging → prod). We train a Spark ML `RandomForestClassifier` pipeline and log everything to MLflow.

**Artifacts:** `notebooks/jobs/04_train_churn_model.py` (interactive) and `src/jobs/train_churn_model.py` (parameterized job).

---

## 🪜 Steps

### Step 1 — Open the training notebook

Open `notebooks/jobs/04_train_churn_model.py` on a cluster with **Databricks Runtime ML**. Confirm the constants in Part 1:

```python
feature_table   = "labs.gold.churn_features_daily"
model_name      = "lives_remaining_churn_model"
experiment_name = "/Shared/lives-remaining/churn"
```

### Step 2 — Inspect the features and label balance

Run Part 1's cells. The label summary should show both classes:

```sql
SELECT churn_label, COUNT(*) FROM labs.gold.churn_features_daily GROUP BY churn_label;
```

If only one class appears, fix Lab 3 before continuing (the model can't learn from one class).

### Step 3 — Train and log the model

Run Part 2. This builds the pipeline (`StringIndexer` × 2 → `VectorAssembler` → `RandomForestClassifier`, `maxDepth=8, numTrees=80`), does a 70/30 split, and inside an `mlflow.start_run`:
- logs params (`num_trees`, `max_depth`, `feature_table`)
- logs metrics (`auc`, `accuracy`, `f1`)
- registers the model as `lives_remaining_churn_model`

**Expected:**

```
Registered lives_remaining_churn_model: AUC=0.9x, accuracy=0.8x, f1=0.8x
```

### Step 4 — Review runs in the MLflow UI

Open **Experiments → `/Shared/lives-remaining/churn`**. Confirm your run with its metrics and the logged `model` artifact.

### Step 5 — Try a few configurations (experiment tracking in action)

Re-run Part 2 changing `maxDepth`/`numTrees` (e.g. 5/50, 10/120), or run the script with different args:

```bash
python src/jobs/train_churn_model.py --algorithm random_forest --num-trees 120 --max-depth 10
python src/jobs/train_churn_model.py --algorithm logistic_regression
```

Compare AUC/F1 across runs in the Experiments UI and pick the best.

### Step 6 — Promote the best version to Production

In **Models → `lives_remaining_churn_model`**, open the best version and set its stage/alias to **Production** (Lab 5 loads `models:/lives_remaining_churn_model/Production`).

---

## ✅ Done when

- [ ] At least one run logged to `/Shared/lives-remaining/churn` with AUC/accuracy/F1
- [ ] `lives_remaining_churn_model` registered with ≥ 1 version
- [ ] Best version promoted to **Production**

## 🧯 Troubleshooting

| Symptom | Fix |
|---------|-----|
| `Only one class present` / training fails | Fix label balance in Lab 3. |
| `Table not found: labs.gold...` | Run Lab 3. |
| `mlflow.spark` import error | Attach a **Databricks Runtime ML** cluster. |
| Accuracy ~1.0 / AUC = 1.0 | Synthetic data can be separable; treat metrics as illustrative, not production-grade. |

**Next:** [Lab 5 — Batch scoring →](lab-5-batch-scoring.md)
