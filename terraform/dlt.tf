# Delta Live Tables pipelines for the medallion layers. Each pipeline publishes
# into the labs catalog created in uc.tf.

variable "pipeline_notebook_root" {
  description = "Workspace path to the src/dlt pipeline notebooks (e.g. a Databricks Repo or Workspace folder)"
  type        = string
  default     = "/Workspace/Repos/lives-remaining-labs/src/dlt"
}

locals {
  dlt_layers = {
    bronze = "bronze_pipeline"
    silver = "silver_pipeline"
    gold   = "gold_pipeline"
  }
}

resource "databricks_pipeline" "medallion" {
  provider = databricks.workspace
  for_each = local.dlt_layers

  name    = "lrl-${each.key}"
  catalog = databricks_catalog.labs.name
  target  = each.key
  serverless = true

  library {
    notebook {
      path = "${var.pipeline_notebook_root}/${each.value}"
    }
  }

  configuration = {
    "pipelines.catalog" = databricks_catalog.labs.name
    "layer"             = each.key
  }

  depends_on = [databricks_schema.medallion]
}
