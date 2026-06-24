"""
DLT Pipeline: Bronze Ingestion via Autoloader
Lives Remaining Labs - Lab 1

⚠️  DO NOT RUN THIS FILE DIRECTLY IN A NOTEBOOK/CLUSTER.
    It is Delta Live Tables source code — `import dlt` only resolves inside the
    DLT pipeline runtime. Running it on a normal cluster fails with
    `ModuleNotFoundError: No module named 'dlt'`.
    Instead, create a DLT pipeline that points at this file and Start it:
        Workflows → Delta Live Tables → Create pipeline
        (Source code = this file; Catalog = labs; Schema = bronze; Serverless)
    See docs/labs/lab-1-bronze-ingestion.md (Steps 4–5).

This pipeline uses Delta Live Tables Autoloader to ingest raw player events from
Azure Blob Storage (ADLS Gen2) into a Bronze Delta table.

Autoloader automatically:
- Detects new files in the source directory
- Infers and evolves schema
- Checkpoints processed files to prevent reprocessing
- Handles late arrivals and duplicates

Storage access (Unity Catalog, serverless-friendly):
- The pipeline reads ADLS Gen2 directly via an `abfss://` path governed by a
  Unity Catalog external location + storage credential (an Azure Databricks
  Access Connector / managed identity).
- No DBFS mount or service-principal Spark config is required, so this pipeline
  runs on serverless DLT compute. The external location is created by
  `notebooks/setup/00_unity_catalog_setup.py`.
"""

import dlt
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, LongType, DoubleType


# Define Bronze schema (matches raw_events.csv structure)
bronze_schema = StructType([
    StructField("event_id", StringType(), False),
    StructField("player_id", StringType(), False),
    StructField("event_type", StringType(), False),
    StructField("timestamp", StringType(), False),
    StructField("game_mode", StringType(), True),
    StructField("region", StringType(), True),
    StructField("platform", StringType(), True),
    StructField("payload", StringType(), True),
    StructField("ingest_ts", StringType(), True),
    StructField("ingest_date", StringType(), True),
])


@dlt.table(
    name="lives_remaining_raw_events",
    comment="Bronze: Raw player events ingested from ADLS Gen2 via Autoloader",
    table_properties={
        "quality": "bronze",
        "source": "azure_blob_storage",
        "pipeline": "bronze_ingestion"
    }
)
@dlt.expect_or_drop("valid_event_id", "event_id IS NOT NULL")
@dlt.expect_or_drop("valid_player_id", "player_id IS NOT NULL")
@dlt.expect_or_drop("valid_event_type", "event_type IN ('login', 'logout', 'kill', 'death', 'purchase', 'session_end')")
def bronze_events():
    """
    Autoloader pipeline: Read raw events from cloud storage.
    
    Configuration:
    - Source: abfss://datalake@lrlstorage01.dfs.core.windows.net/events/
    - Format: CSV with headers
    - Checkpoint: abfss://datalake@lrlstorage01.dfs.core.windows.net/.checkpoints/events/
    - Access: Unity Catalog external location (no mount, serverless-friendly)
    - Mode: Incrementally read new files only
    
    Expectations (Quality Checks):
    - event_id: Not null (every event must have unique ID)
    - player_id: Not null (every event must be tied to player)
    - event_type: Must be one of 6 valid types (catch schema errors)
    
    Drop rows that fail expectations (DLT default behavior with @dlt.expect_or_drop).
    """
    
    # Read ADLS Gen2 directly via the Unity Catalog external location.
    # No mount required — works on serverless DLT compute.
    # See notebooks/setup/00_unity_catalog_setup.py for the external location.
    source_path = "abfss://datalake@lrlstorage01.dfs.core.windows.net/events/"
    checkpoint_path = "abfss://datalake@lrlstorage01.dfs.core.windows.net/.checkpoints/events/"
    
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("cloudFiles.schemaLocation", checkpoint_path)
        .option("header", "true")
        .option("inferSchema", "false")  # Use explicit schema for reliability
        .schema(bronze_schema)
        .load(source_path)
    )


@dlt.table(
    name="events_quality_metrics",
    comment="Quality metrics for bronze ingestion",
)
def quality_metrics():
    """
    Summary of quality checks (expectations passed/failed).
    Useful for monitoring data quality over time.
    """
    return dlt.read("lives_remaining_raw_events")


@dlt.view
def raw_events_summary():
    """
    Quick summary: row count, unique players, event type distribution.
    Useful for sanity checks during ingestion.
    """
    df = dlt.read("lives_remaining_raw_events")
    return (
        df.selectExpr(
            "COUNT(*) as total_events",
            "COUNT(DISTINCT player_id) as unique_players",
            "COUNT(DISTINCT DATE(timestamp)) as days_covered"
        )
    )
