"""
DLT Pipeline: Gold Feature Engineering
Lives Remaining Labs - Lab 3

Creates business-ready feature tables for churn prediction, ARPU analysis, and
player segmentation from Silver events and sessions.
"""

import dlt
from pyspark.sql import functions as F


@dlt.table(
    name="churn_features_daily",
    comment="Gold: daily player-level features and churn labels for ML",
    table_properties={
        "quality": "gold",
        "pipeline": "gold_feature_engineering",
    },
)
@dlt.expect_or_drop("valid_player_id", "player_id IS NOT NULL")
@dlt.expect_or_drop("valid_compute_date", "compute_date IS NOT NULL")
def churn_features_daily():
    events = spark.read.table("labs.silver.player_events_cleaned")
    sessions = spark.read.table("labs.silver.player_sessions")
    purchases = spark.read.table("labs.silver.player_purchase_events")

    activity = (
        events.groupBy("player_id")
        .agg(
            F.current_date().alias("compute_date"),
            F.min("event_date").alias("first_seen_date"),
            F.max(F.when(F.col("event_type_normalized") == "login", F.col("event_date"))).alias("last_login_date"),
            F.count(F.when((F.col("event_type_normalized") == "login") & (F.col("event_date") >= F.date_sub(F.current_date(), 7)), True)).alias("login_count_7d"),
            F.count(F.when((F.col("event_type_normalized") == "login") & (F.col("event_date") >= F.date_sub(F.current_date(), 30)), True)).alias("login_count_30d"),
            F.count(F.when((F.col("event_type_normalized") == "kill") & (F.col("event_date") >= F.date_sub(F.current_date(), 7)), True)).alias("kill_count_7d"),
            F.count(F.when(F.col("event_date") >= F.date_sub(F.current_date(), 7), True)).alias("event_count_7d"),
            F.first("platform", ignorenulls=True).alias("platform_primary"),
            F.first("region", ignorenulls=True).alias("region_primary"),
        )
    )

    session_features = (
        sessions.groupBy("player_id")
        .agg(
            F.count(F.when(F.col("session_date") >= F.date_sub(F.current_date(), 7), True)).alias("match_count_7d"),
            F.avg(F.when(F.col("session_date") >= F.date_sub(F.current_date(), 7), F.col("duration_min"))).alias("avg_session_duration_7d"),
            (F.sum(F.when(F.col("session_date") >= F.date_sub(F.current_date(), 7), F.col("duration_min")).otherwise(0)) / F.lit(60.0)).alias("total_playtime_7d"),
            F.avg(F.when(F.col("session_date") >= F.date_sub(F.current_date(), 7), F.col("win_rate"))).alias("win_rate_7d"),
        )
    )

    spend_features = (
        purchases.groupBy("player_id")
        .agg(
            (F.sum(F.when(F.col("event_date") >= F.date_sub(F.current_date(), 7), F.col("item_price_usd")).otherwise(0)) / F.lit(7.0)).alias("avg_spend_7d"),
            (F.sum(F.when(F.col("event_date") >= F.date_sub(F.current_date(), 30), F.col("item_price_usd")).otherwise(0)) / F.lit(30.0)).alias("avg_spend_30d"),
            F.sum(F.when(F.col("event_date") >= F.date_sub(F.current_date(), 30), F.col("item_price_usd")).otherwise(0)).alias("total_spend_30d"),
        )
    )

    return (
        activity.join(session_features, "player_id", "left")
        .join(spend_features, "player_id", "left")
        .fillna({
            "login_count_7d": 0,
            "login_count_30d": 0,
            "kill_count_7d": 0,
            "event_count_7d": 0,
            "match_count_7d": 0,
            "avg_session_duration_7d": 0.0,
            "total_playtime_7d": 0.0,
            "win_rate_7d": 0.0,
            "avg_spend_7d": 0.0,
            "avg_spend_30d": 0.0,
            "total_spend_30d": 0.0,
        })
        .withColumn("days_since_login", F.datediff(F.col("compute_date"), F.col("last_login_date")))
        .withColumn("is_new_player", F.datediff(F.col("compute_date"), F.col("first_seen_date")) < 30)
        .withColumn("churn_label", F.when(F.col("days_since_login") >= 7, 1).otherwise(0))
    )


@dlt.table(
    name="arpu_features_daily",
    comment="Gold: revenue features for ARPU and monetization analysis",
    table_properties={"quality": "gold"},
)
@dlt.expect_or_drop("valid_player_id", "player_id IS NOT NULL")
def arpu_features_daily():
    purchases = spark.read.table("labs.silver.player_purchase_events")
    events = spark.read.table("labs.silver.player_events_cleaned")

    player_first_seen = events.groupBy("player_id").agg(F.min("event_date").alias("first_seen_date"))

    return (
        purchases.groupBy("player_id")
        .agg(
            F.current_date().alias("compute_date"),
            (F.sum(F.when(F.col("event_date") >= F.date_sub(F.current_date(), 7), F.col("item_price_usd")).otherwise(0)) / F.lit(7.0)).alias("avg_spend_7d"),
            (F.sum(F.when(F.col("event_date") >= F.date_sub(F.current_date(), 30), F.col("item_price_usd")).otherwise(0)) / F.lit(30.0)).alias("avg_spend_30d"),
            F.sum(F.when(F.col("event_date") >= F.date_sub(F.current_date(), 90), F.col("item_price_usd")).otherwise(0)).alias("total_spend_90d"),
            F.avg("item_price_usd").alias("avg_spend_all_time"),
            F.count(F.when(F.col("event_date") >= F.date_sub(F.current_date(), 7), True)).alias("purchase_frequency_7d"),
            F.count(F.when(F.col("event_date") >= F.date_sub(F.current_date(), 30), True)).alias("purchase_frequency_30d"),
            F.min("event_date").alias("first_purchase_date"),
            F.max("event_date").alias("last_purchase_date"),
        )
        .join(player_first_seen, "player_id", "left")
        .withColumn("days_since_first_purchase", F.datediff(F.col("compute_date"), F.col("first_purchase_date")))
        .withColumn("days_since_last_purchase", F.datediff(F.col("compute_date"), F.col("last_purchase_date")))
        .withColumn(
            "premium_tier",
            F.when(F.col("total_spend_90d") >= 250, "platinum")
            .when(F.col("total_spend_90d") >= 100, "gold")
            .when(F.col("total_spend_90d") >= 50, "silver")
            .when(F.col("total_spend_90d") > 0, "bronze")
            .otherwise("free"),
        )
        .withColumn("is_whale", F.col("total_spend_90d") >= 250)
    )


@dlt.table(
    name="player_segments",
    comment="Gold: player engagement and monetization segments for BI",
    table_properties={"quality": "gold"},
)
def player_segments():
    churn = dlt.read("churn_features_daily")

    return (
        churn.select(
            "player_id",
            "compute_date",
            "region_primary",
            "platform_primary",
            "days_since_login",
            "login_count_7d",
            "total_spend_30d",
            "avg_session_duration_7d",
            "win_rate_7d",
        )
        .withColumn(
            "engagement_segment",
            F.when(F.col("days_since_login") >= 14, "lapsed")
            .when(F.col("login_count_7d") >= 5, "core")
            .when(F.col("login_count_7d") >= 2, "regular")
            .otherwise("casual"),
        )
        .withColumn(
            "revenue_segment",
            F.when(F.col("total_spend_30d") >= 100, "whale")
            .when(F.col("total_spend_30d") >= 20, "spender")
            .otherwise("free"),
        )
    )
