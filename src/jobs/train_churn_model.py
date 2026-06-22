"""
Lab 4: Train and register a churn prediction model with MLflow.

Run as a Databricks Python task after Lab 3 creates
labs.gold.churn_features_daily.
"""

import argparse

import mlflow
from pyspark.ml import Pipeline
from pyspark.ml.classification import LogisticRegression, RandomForestClassifier
from pyspark.ml.evaluation import BinaryClassificationEvaluator, MulticlassClassificationEvaluator
from pyspark.ml.feature import StringIndexer, VectorAssembler


DEFAULT_FEATURE_COLUMNS = [
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


def parse_args():
    parser = argparse.ArgumentParser(description="Train Lives Remaining Labs churn model.")
    parser.add_argument("--feature-table", default="labs.gold.churn_features_daily")
    parser.add_argument("--model-name", default="lives_remaining_churn_model")
    parser.add_argument("--experiment-name", default="/Shared/lives-remaining/churn")
    parser.add_argument("--algorithm", choices=["logistic_regression", "random_forest"], default="random_forest")
    parser.add_argument("--max-depth", type=int, default=8)
    parser.add_argument("--num-trees", type=int, default=80)
    return parser.parse_args()


def build_estimator(args):
    if args.algorithm == "logistic_regression":
        return LogisticRegression(featuresCol="features", labelCol="churn_label", maxIter=50)

    return RandomForestClassifier(
        featuresCol="features",
        labelCol="churn_label",
        maxDepth=args.max_depth,
        numTrees=args.num_trees,
        seed=42,
    )


def main():
    args = parse_args()
    mlflow.set_experiment(args.experiment_name)

    features = (
        spark.table(args.feature_table)
        .select(
            "player_id",
            "churn_label",
            "platform_primary",
            "region_primary",
            *DEFAULT_FEATURE_COLUMNS,
        )
        .fillna(0, subset=DEFAULT_FEATURE_COLUMNS)
        .fillna({"platform_primary": "Unknown", "region_primary": "Unknown"})
    )

    train_df, test_df = features.randomSplit([0.7, 0.3], seed=42)

    platform_indexer = StringIndexer(inputCol="platform_primary", outputCol="platform_index", handleInvalid="keep")
    region_indexer = StringIndexer(inputCol="region_primary", outputCol="region_index", handleInvalid="keep")
    assembler = VectorAssembler(
        inputCols=DEFAULT_FEATURE_COLUMNS + ["platform_index", "region_index"],
        outputCol="features",
        handleInvalid="keep",
    )
    estimator = build_estimator(args)
    pipeline = Pipeline(stages=[platform_indexer, region_indexer, assembler, estimator])

    with mlflow.start_run(run_name=f"{args.algorithm}_churn"):
        mlflow.log_param("algorithm", args.algorithm)
        mlflow.log_param("feature_table", args.feature_table)
        mlflow.log_param("feature_columns", ",".join(DEFAULT_FEATURE_COLUMNS))
        if args.algorithm == "random_forest":
            mlflow.log_param("max_depth", args.max_depth)
            mlflow.log_param("num_trees", args.num_trees)

        model = pipeline.fit(train_df)
        predictions = model.transform(test_df)

        auc = BinaryClassificationEvaluator(
            labelCol="churn_label",
            rawPredictionCol="rawPrediction",
            metricName="areaUnderROC",
        ).evaluate(predictions)
        accuracy = MulticlassClassificationEvaluator(
            labelCol="churn_label",
            predictionCol="prediction",
            metricName="accuracy",
        ).evaluate(predictions)
        f1 = MulticlassClassificationEvaluator(
            labelCol="churn_label",
            predictionCol="prediction",
            metricName="f1",
        ).evaluate(predictions)

        mlflow.log_metric("auc", auc)
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("f1", f1)
        mlflow.spark.log_model(model, artifact_path="model", registered_model_name=args.model_name)

        print(f"Registered model: {args.model_name}")
        print(f"AUC={auc:.4f}, accuracy={accuracy:.4f}, f1={f1:.4f}")


if __name__ == "__main__":
    main()
