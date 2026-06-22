# Databricks notebook source
# COMMAND ----------

# MAGIC %md
# MAGIC # Lab Setup: Unity Catalog Bootstrap
# MAGIC ## Lives Remaining Labs — Azure Databricks
# MAGIC
# MAGIC **Fictional Company**: Lives Remaining Labs is a fictional multiplayer game studio.
# MAGIC
# MAGIC ### 🎯 Goal
# MAGIC Create the Unity Catalog objects every later lab assumes already exist:
# MAGIC the catalog (`labs` by default), the `bronze` / `silver` / `gold` schemas,
# MAGIC a storage credential + external location pointing at ADLS Gen2, and the
# MAGIC grants used by the job service principal.
# MAGIC
# MAGIC ### 📚 What You'll Learn
# MAGIC 1. **Three-level namespace**: `catalog.schema.table` — the foundation of governance in UC
# MAGIC 2. **Storage credentials & external locations**: how UC governs access to ADLS Gen2
# MAGIC 3. **Grants**: least-privilege access for the job service principal
# MAGIC 4. **Environment namespacing**: parameterize the catalog so dev/staging/prod stay isolated
# MAGIC
# MAGIC > Run this notebook **once per environment** on a Unity Catalog-enabled cluster
# MAGIC > (or SQL warehouse) using an identity with the `CREATE CATALOG` /
# MAGIC > `CREATE EXTERNAL LOCATION` metastore privileges. After this, run Lab 0 → Lab 7.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Prerequisites
# MAGIC - ✅ Premium workspace with a Unity Catalog metastore attached
# MAGIC - ✅ Metastore admin (or delegated `CREATE CATALOG` privilege)
# MAGIC - ✅ ADLS Gen2 account + container provisioned (see `terraform/`)
# MAGIC - ✅ An Azure Databricks Access Connector (managed identity) with
# MAGIC      **Storage Blob Data Contributor** on the storage account

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 1: Parameters
# MAGIC
# MAGIC The catalog name is a **widget** so the same notebook bootstraps any
# MAGIC environment. Pass `catalog=labs_dev` / `labs_staging` / `labs_prod` to keep
# MAGIC environments isolated, matching the namespacing described in `docs/architecture.md`.

# COMMAND ----------

dbutils.widgets.text("catalog", "labs", "Catalog name")
dbutils.widgets.text("storage_account", "lrlstorage", "ADLS Gen2 account name")
dbutils.widgets.text("container", "datalake", "ADLS Gen2 container")
dbutils.widgets.text("access_connector_id", "", "Databricks Access Connector resource ID (managed identity)")
dbutils.widgets.text("job_principal", "", "Service principal / group to grant job access (optional)")

catalog = dbutils.widgets.get("catalog").strip()
storage_account = dbutils.widgets.get("storage_account").strip()
container = dbutils.widgets.get("container").strip()
access_connector_id = dbutils.widgets.get("access_connector_id").strip()
job_principal = dbutils.widgets.get("job_principal").strip()

assert catalog, "catalog must not be empty"
assert storage_account, "storage_account must not be empty"
assert container, "container must not be empty"

container_uri = f"abfss://{container}@{storage_account}.dfs.core.windows.net"
storage_credential = f"{catalog}_storage_cred"
external_location = f"{catalog}_datalake"

print(f"Catalog:            {catalog}")
print(f"Container URI:      {container_uri}")
print(f"Storage credential: {storage_credential}")
print(f"External location:  {external_location}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 2: Storage Credential + External Location
# MAGIC
# MAGIC Unity Catalog reaches ADLS Gen2 through a **storage credential** (an Azure
# MAGIC Databricks Access Connector / managed identity) wrapped in an **external
# MAGIC location**. Lab 0 uploads CSVs here and Lab 1's Autoloader reads from it.
# MAGIC
# MAGIC > If your Terraform already created the storage credential and external
# MAGIC > location, you can skip this cell — the `CREATE ... IF NOT EXISTS`
# MAGIC > statements are idempotent and safe to re-run.

# COMMAND ----------

if access_connector_id:
    spark.sql(f"""
        CREATE STORAGE CREDENTIAL IF NOT EXISTS {storage_credential}
        WITH AZURE_MANAGED_IDENTITY (
            ACCESS_CONNECTOR_ID = '{access_connector_id}'
        )
        COMMENT 'Lives Remaining Labs — ADLS Gen2 access for {catalog}'
    """)

    spark.sql(f"""
        CREATE EXTERNAL LOCATION IF NOT EXISTS {external_location}
        URL '{container_uri}/'
        WITH (STORAGE CREDENTIAL {storage_credential})
        COMMENT 'Lives Remaining Labs data lake root for {catalog}'
    """)
    print(f"External location '{external_location}' ready -> {container_uri}/")
else:
    print("access_connector_id not provided — skipping storage credential / external location.")
    print("Provide the Access Connector resource ID widget, or create these in Terraform (uc.tf).")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 3: Catalog + Medallion Schemas
# MAGIC
# MAGIC Create the `labs` catalog and the `bronze` / `silver` / `gold` schemas that
# MAGIC every later lab writes into (`labs.bronze.*`, `labs.silver.*`, `labs.gold.*`).

# COMMAND ----------

spark.sql(f"""
    CREATE CATALOG IF NOT EXISTS {catalog}
    COMMENT 'Lives Remaining Labs — medallion catalog ({catalog})'
""")

for schema in ["bronze", "silver", "gold"]:
    spark.sql(f"""
        CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}
        COMMENT 'Lives Remaining Labs {schema} layer'
    """)
    print(f"Schema ready: {catalog}.{schema}")

spark.sql(f"USE CATALOG {catalog}")
display(spark.sql(f"SHOW SCHEMAS IN {catalog}"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Part 4: Grants (least privilege)
# MAGIC
# MAGIC Grant the job service principal (or a workspace group) just enough to run
# MAGIC the pipelines: browse the catalog, use the schemas, and read/write tables.
# MAGIC Adjust the principal to match your environment (e.g. a `data_engineers`
# MAGIC group for dev, a dedicated service principal for prod).

# COMMAND ----------

if job_principal:
    spark.sql(f"GRANT USE CATALOG ON CATALOG {catalog} TO `{job_principal}`")
    for schema in ["bronze", "silver", "gold"]:
        spark.sql(f"GRANT USE SCHEMA ON SCHEMA {catalog}.{schema} TO `{job_principal}`")
        spark.sql(f"GRANT CREATE TABLE ON SCHEMA {catalog}.{schema} TO `{job_principal}`")
        spark.sql(f"GRANT SELECT, MODIFY ON SCHEMA {catalog}.{schema} TO `{job_principal}`")

    if access_connector_id:
        spark.sql(
            f"GRANT READ FILES, WRITE FILES ON EXTERNAL LOCATION {external_location} TO `{job_principal}`"
        )
    print(f"Granted pipeline privileges on {catalog} to {job_principal}")
else:
    print("job_principal not provided — skipping grants.")
    print("Set the job_principal widget to a service principal app id or group name to apply grants.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ Done
# MAGIC
# MAGIC Unity Catalog is bootstrapped:
# MAGIC - Catalog `labs` with `bronze` / `silver` / `gold` schemas
# MAGIC - External location `labs_datalake` → ADLS Gen2 (if access connector supplied)
# MAGIC - Grants for the job principal (if supplied)
# MAGIC
# MAGIC **Next:** run **Lab 0** (generate & upload events), then **Lab 1** (Bronze ingestion).

# COMMAND ----------

print(f"Unity Catalog bootstrap complete for catalog '{catalog}'.")
