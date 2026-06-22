# Prerequisites (Azure Setup)

Before starting labs, ensure you have:

1. **Azure subscription** with Databricks, Storage, and Entra permissions
2. **Azure Databricks workspace** (Premium SKU) in your resource group
3. **Azure Data Lake Storage (ADLS Gen2)** created with a blob container
4. **Service Principal** (Entra app registration) with Storage Blob roles
5. **Databricks personal access token (PAT)** for API access
6. **Python 3.9+** installed locally
7. **Azure CLI** authenticated (`az login`)

## Provision & bootstrap

1. **Provision infrastructure** with Terraform (`terraform/`) — creates the
   Databricks Premium workspace, ADLS Gen2 account/container, the Access
   Connector managed identity, and the Unity Catalog catalog/schemas. Either:
   - `cd terraform && terraform init && terraform apply`, **or**
2. **Bootstrap Unity Catalog interactively** by running
   `notebooks/setup/00_unity_catalog_setup.py` once per environment. It creates
   the `labs` catalog, the `bronze`/`silver`/`gold` schemas, the external
   location over ADLS Gen2, and the job grants that every later lab assumes
   already exist.

> ⚠️ The labs read/write three-level Unity Catalog names (`labs.bronze.*`,
> `labs.silver.*`, `labs.gold.*`). You **must** complete the Terraform apply or
> the setup notebook before Lab 0, or the pipelines will fail with
> "catalog/schema not found".

👉 **[See Azure Setup Guide →](../setup-azure.md)** (coming soon)

---
