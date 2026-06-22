# Unity Catalog: storage credential, external location, catalog, schemas, grants.
# This is the IaC equivalent of notebooks/setup/00_unity_catalog_setup.py — use
# whichever fits your workflow (Terraform for repeatable environments, the
# notebook for interactive/lab use).

locals {
  container_uri = "abfss://${var.storage_container_name}@${var.storage_account_name}.dfs.core.windows.net"
}

# Storage credential backed by the Access Connector managed identity (adls.tf).
resource "databricks_storage_credential" "this" {
  provider = databricks.workspace
  name     = "${var.catalog_name}_storage_cred"

  azure_managed_identity {
    access_connector_id = azurerm_databricks_access_connector.this.id
  }

  comment = "Lives Remaining Labs — ADLS Gen2 access for ${var.catalog_name}"
}

resource "databricks_external_location" "datalake" {
  provider        = databricks.workspace
  name            = "${var.catalog_name}_datalake"
  url             = "${local.container_uri}/"
  credential_name = databricks_storage_credential.this.name
  comment         = "Lives Remaining Labs data lake root for ${var.catalog_name}"

  depends_on = [azurerm_role_assignment.ac_storage]
}

# Catalog + medallion schemas every lab writes into (labs.bronze/silver/gold).
resource "databricks_catalog" "labs" {
  provider     = databricks.workspace
  metastore_id = var.metastore_id
  name         = var.catalog_name
  comment      = "Lives Remaining Labs — medallion catalog"

  depends_on = [databricks_external_location.datalake]
}

resource "databricks_schema" "medallion" {
  provider     = databricks.workspace
  for_each     = toset(["bronze", "silver", "gold"])
  catalog_name = databricks_catalog.labs.name
  name         = each.key
  comment      = "Lives Remaining Labs ${each.key} layer"
}

# Least-privilege grants for the job service principal / group (optional).
resource "databricks_grants" "catalog" {
  provider = databricks.workspace
  count    = var.job_principal == "" ? 0 : 1
  catalog  = databricks_catalog.labs.name

  grant {
    principal  = var.job_principal
    privileges = ["USE_CATALOG"]
  }
}

resource "databricks_grants" "schemas" {
  provider = databricks.workspace
  for_each = var.job_principal == "" ? toset([]) : toset(["bronze", "silver", "gold"])
  schema   = "${databricks_catalog.labs.name}.${databricks_schema.medallion[each.key].name}"

  grant {
    principal  = var.job_principal
    privileges = ["USE_SCHEMA", "CREATE_TABLE", "SELECT", "MODIFY"]
  }
}

resource "databricks_grants" "external_location" {
  provider          = databricks.workspace
  count             = var.job_principal == "" ? 0 : 1
  external_location = databricks_external_location.datalake.name

  grant {
    principal  = var.job_principal
    privileges = ["READ_FILES", "WRITE_FILES"]
  }
}
