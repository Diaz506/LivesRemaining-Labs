# Lab 4: Churn Prediction with MLflow

### 🎯 Why This Lab?

Now we have features! **MLflow** is Databricks' ML lifecycle framework:
- Track experiments (hyperparameters, metrics, artifacts)
- Register models in model registry
- Version & promote models (dev → staging → prod)
- Reproducibility: Re-run exact experiments

Why MLflow instead of just sklearn?
- Experiment tracking across team
- Model reproducibility & lineage
- Easy model deployment
- Metric comparison across runs

### 📚 Concepts

**ML Workflow:**
1. Load training data (Gold features + labels)
2. Split: train (70%), test (30%)
3. Train model with hyperparameters
4. Evaluate on test set (accuracy, precision, recall, AUC)
5. Log to MLflow Tracking
6. Register best model in MLflow Model Registry

**Classification Metrics:**
- **Accuracy**: (TP + TN) / total (good overall metric)
- **Precision**: TP / (TP + FP) (when you predict churn, are you right?)
- **Recall**: TP / (TP + FN) (of actual churners, how many did you catch?)
- **F1-score**: Harmonic mean of precision & recall
- **AUC**: Area under ROC curve (0.5 = random, 1.0 = perfect)

**Hyperparameters (for sklearn RandomForest):**
- `max_depth`: How deep trees can grow (prevent overfitting)
- `n_estimators`: Number of trees
- `min_samples_split`: Min samples to split node
- Tuning: Grid search or random search

**Model Registry:**
- Central place to store trained models
- Stages: None → Staging → Production → Archived
- Enables promotion workflow

### 🔧 Goal

Train churn classification model, evaluate, and register in MLflow.

### 📋 Deliverables

- `src/jobs/train_churn_model.py` — training script
- `notebooks/jobs/04_train_churn_model.py` — interactive notebook
- Trained model registered in MLflow registry (accuracy ~0.85+)
- Experiment runs logged (try 3–5 hyperparameter configs)

### ☁️ Azure Tasks

- View MLflow Tracking UI in Databricks workspace
- Register model in MLflow Model Registry
- Compare metrics across runs

### 🔑 Key Terms

- **Experiment**: Collection of runs (different hyperparameter configs)
- **Run**: Single training job (logs metrics, params, artifacts)
- **MLflow Tracking Server**: Records experiments (default: workspace)
- **Model Registry**: Central repository for production models
- **Hyperparameter**: Tunable config (not learned from data)
- **Train/test split**: Data separation (prevent overfitting on test set)

### ⏱️ Time: ~2 hours

### 📖 Reference

- MLflow: [Documentation](https://mlflow.org/docs/latest/index.html)
- Databricks MLflow: [Workspace integration](https://docs.databricks.com/en/machine-learning/mlflow/index.html)
- Classification metrics: [Scikit-learn docs](https://scikit-learn.org/stable/modules/model_evaluation.html)
- Hyperparameter tuning: [Grid search](https://scikit-learn.org/stable/modules/grid_search.html)

### Prerequisites: Lab 3

---
