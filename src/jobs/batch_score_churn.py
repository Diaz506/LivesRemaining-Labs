"""
Lab 5: Batch score churn risk for active players.

Loads the registered MLflow model, scores the latest Gold features, and writes
the prediction table consumed by Power BI and retention workflows.
"""

import argparse

import mlflow
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType


def parse_args():
    parser = argparse.ArgumentParser(description="Score Lives Remaining Labs churn risk.")
    parser.add_argument("--feature-table", default="labs.gold.churn_features_daily")
    parser.add_argument("--output-table", default="labs.gold.player_churn_scores")
    parser.add_argument("--model-uri", default="models:/lives_remaining_churn_model/Production")
    return parser.parse_args()


@F.udf(DoubleType())
def churn_probability(probability):
    return float(probability[1]) if probability is not None and len(probability) > 1 else None


def main():
    args = parse_args()

    latest_compute_date = spark.table(args.feature_table).agg(F.max("compute_date").alias("compute_date")).first()["compute_date"]
    features = spark.table(args.feature_table).where(F.col("compute_date") == latest_compute_date)

    model = mlflow.spark.load_model(args.model_uri)
    scored = (
        model.transform(features)
        .withColumn("churn_probability", churn_probability("probability"))
        .withColumn(
            "risk_tier",
            F.when(F.col("churn_probability") >= 0.75, "high")
            .when(F.col("churn_probability") >= 0.40, "medium")
            .otherwise("low"),
        )
        .withColumn("scored_at", F.current_timestamp())
        .select(
            "player_id",
            "compute_date",
            "scored_at",
            "churn_probability",
            "risk_tier",
            "days_since_login",
            "login_count_7d",
            "total_spend_30d",
            "platform_primary",
            "region_primary",
        )
    )

    (
        scored.write
        .format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(args.output_table)
    )

    print(f"Wrote churn scores to {args.output_table} for compute_date={latest_compute_date}")


if __name__ == "__main__":
    main()
