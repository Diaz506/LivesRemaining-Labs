variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
}

variable "databricks_account_id" {
  description = "Databricks account ID (for account-level Unity Catalog operations)"
  type        = string
}

variable "resource_group_name" {
  description = "Azure resource group name"
  type        = string
  default     = "lrl-rg"
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "eastus"
}

variable "workspace_name" {
  description = "Azure Databricks workspace name"
  type        = string
  default     = "lrl-workspace"
}

variable "storage_account_name" {
  description = "ADLS Gen2 storage account name (3-24 lowercase alphanumeric chars)"
  type        = string
  default     = "lrlstorage01"
}

variable "storage_container_name" {
  description = "ADLS Gen2 container for Bronze/Silver/Gold data"
  type        = string
  default     = "datalake"
}

variable "catalog_name" {
  description = "Unity Catalog catalog name for the labs (use labs_dev / labs_prod for env isolation)"
  type        = string
  default     = "labs"
}

variable "metastore_id" {
  description = "Existing Unity Catalog metastore ID to attach the catalog to"
  type        = string
}

variable "job_principal" {
  description = "Service principal app ID or group name granted access to the labs catalog"
  type        = string
  default     = ""
}

variable "tags" {
  description = "Tags applied to all resources"
  type        = map(string)
  default = {
    project = "lives-remaining-labs"
    env     = "dev"
  }
}
