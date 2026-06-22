"""
DLT Pipeline: Silver Transformations and Quality Checks
Lives Remaining Labs - Lab 2

Transforms raw Bronze game telemetry into cleaned event and session-level
Silver tables. The tables created here are the trusted source for Gold
feature engineering, ML training, and BI analytics.
"""

import dlt
from pyspark.sql import functions as F


VALID_EVENT_TYPES = "'login', 'logout', 'kill', 'death', 'purchase', 'session_end'"
VALID_GAME_MODES = "'deathmatch', 'capture_flag', 'ranked', 'casual'"
VALID_REGIONS = "'NA', 'EU', 'APAC', 'LATAM'"
VALID_PLATFORMS = "'PC', 'Console', 'Mobile'"


@dlt.table(
    name="player_events_cleaned",
    comment="Silver: deduplicated, typed, and payload-enriched player events",
    table_properties={
        "quality": "silver",
        "source": "labs.bronze.lives_remaining_raw_events",
        "pipeline": "silver_transformations",
    },
)
@dlt.expect_or_drop("valid_event_id", "event_id IS NOT NULL")
@dlt.expect_or_drop("valid_player_id", "player_id IS NOT NULL")
@dlt.expect_or_drop("valid_event_type", f"event_type_normalized IN ({VALID_EVENT_TYPES})")
@dlt.expect("known_game_mode", f"game_mode IS NULL OR game_mode IN ({VALID_GAME_MODES})")
@dlt.expect("known_region", f"region IS NULL OR region IN ({VALID_REGIONS})")
@dlt.expect("known_platform", f"platform IS NULL OR platform IN ({VALID_PLATFORMS})")
def player_events_cleaned():
    """
    Clean Bronze events:
    - Cast string timestamps to timestamp/date types.
    - Normalize event type casing and whitespace.
    - Deduplicate by event_id.
    - Parse commonly used JSON payload attributes into first-class columns.
    """

    bronze = spark.readStream.table("labs.bronze.lives_remaining_raw_events")

    return (
        bronze.select(
            "event_id",
            "player_id",
            F.lower(F.trim(F.col("event_type"))).alias("event_type_normalized"),
            F.to_timestamp("timestamp").alias("event_ts"),
            F.to_timestamp("ingest_ts").alias("ingest_ts"),
            F.to_date("ingest_date").alias("ingest_date"),
            F.trim(F.col("game_mode")).alias("game_mode"),
            F.upper(F.trim(F.col("region"))).alias("region"),
            F.initcap(F.trim(F.col("platform"))).alias("platform"),
            F.col("payload"),
        )
        .dropDuplicates(["event_id"])
        .withColumn("event_date", F.to_date("event_ts"))
        .withColumn("opponent_id", F.coalesce(
            F.get_json_object("payload", "$.opponent_id"),
            F.get_json_object("payload", "$.killed_by"),
        ))
        .withColumn("weapon", F.get_json_object("payload", "$.weapon"))
        .withColumn("headshot", F.get_json_object("payload", "$.headshot").cast("boolean"))
        .withColumn("item_id", F.get_json_object("payload", "$.item_id"))
        .withColumn("item_name", F.get_json_object("payload", "$.item_name"))
        .withColumn("item_price_usd", F.get_json_object("payload", "$.item_price_usd").cast("double"))
        .withColumn("payment_method", F.get_json_object("payload", "$.payment_method"))
        .withColumn("experience_granted", F.get_json_object("payload", "$.experience_granted").cast("int"))
        .withColumn("session_duration_seconds", F.get_json_object("payload", "$.duration_seconds").cast("int"))
        .withColumn("session_kills", F.get_json_object("payload", "$.total_kills").cast("int"))
        .withColumn("session_deaths", F.get_json_object("payload", "$.total_deaths").cast("int"))
        .withColumn("session_xp", F.get_json_object("payload", "$.total_earned_xp").cast("int"))
        .withColumn("session_items_purchased", F.get_json_object("payload", "$.items_purchased").cast("int"))
    )


@dlt.table(
    name="player_sessions",
    comment="Silver: one row per completed player session derived from session_end events",
    table_properties={
        "quality": "silver",
        "pipeline": "silver_transformations",
    },
)
@dlt.expect_or_drop("valid_session_id", "session_id IS NOT NULL")
@dlt.expect_or_drop("valid_player_id", "player_id IS NOT NULL")
@dlt.expect_or_drop("positive_duration", "duration_min > 0")
@dlt.expect("non_negative_kills", "kills >= 0")
@dlt.expect("non_negative_deaths", "deaths >= 0")
def player_sessions():
    """
    Build session facts from the synthetic session_end payloads.

    A production game telemetry stream would normally include a stable session_id
    on every event. This lab derives a deterministic session_id from player_id
    and session end timestamp so the downstream labs can focus on DLT and ML.
    """

    events = dlt.read("player_events_cleaned")

    return (
        events.where(F.col("event_type_normalized") == "session_end")
        .select(
            F.sha2(F.concat_ws(":", F.col("player_id"), F.col("event_ts").cast("string"), F.col("event_id")), 256).alias("session_id"),
            "player_id",
            F.col("event_ts").alias("session_end_ts"),
            F.from_unixtime(F.unix_timestamp("event_ts") - F.col("session_duration_seconds")).cast("timestamp").alias("session_start_ts"),
            (F.col("session_duration_seconds") / F.lit(60.0)).alias("duration_min"),
            "game_mode",
            "region",
            "platform",
            F.coalesce(F.col("session_kills"), F.lit(0)).alias("kills"),
            F.coalesce(F.col("session_deaths"), F.lit(0)).alias("deaths"),
            (F.coalesce(F.col("session_kills"), F.lit(0)) / (F.coalesce(F.col("session_deaths"), F.lit(0)) + F.lit(1))).alias("kd_ratio"),
            F.lit(1).alias("matches_played"),
            F.when(F.coalesce(F.col("session_kills"), F.lit(0)) >= F.coalesce(F.col("session_deaths"), F.lit(0)), 1).otherwise(0).alias("matches_won"),
            F.coalesce(F.col("session_items_purchased"), F.lit(0)).alias("items_purchased"),
            F.coalesce(F.col("session_xp"), F.lit(0)).alias("experience_gain"),
            F.col("event_date").alias("session_date"),
        )
        .withColumn("win_rate", F.col("matches_won") / F.col("matches_played"))
    )


@dlt.table(
    name="player_purchase_events",
    comment="Silver: clean purchase events used for ARPU and revenue analytics",
    table_properties={"quality": "silver"},
)
@dlt.expect_or_drop("valid_purchase_amount", "item_price_usd IS NOT NULL AND item_price_usd >= 0")
def player_purchase_events():
    return (
        dlt.read("player_events_cleaned")
        .where(F.col("event_type_normalized") == "purchase")
        .select(
            "event_id",
            "player_id",
            "event_ts",
            "event_date",
            "region",
            "platform",
            "item_id",
            "item_name",
            "item_price_usd",
            "payment_method",
        )
    )


@dlt.table(
    name="silver_quality_summary",
    comment="Silver: operational quality summary by event date and type",
    table_properties={"quality": "silver"},
)
def silver_quality_summary():
    return (
        dlt.read("player_events_cleaned")
        .groupBy("event_date", "event_type_normalized")
        .agg(
            F.count("*").alias("event_count"),
            F.countDistinct("player_id").alias("unique_players"),
            F.sum(F.when(F.col("payload").isNull(), 1).otherwise(0)).alias("missing_payload_count"),
        )
    )
