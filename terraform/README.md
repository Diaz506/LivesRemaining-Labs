# Terraform — Azure Databricks Infrastructure

> 🧭 **Advanced / optional.** This is **Path B** of setup. If you're new to the
> labs, use the UI path first — see
> [`docs/labs/prerequisites.md`](../docs/labs/prerequisites.md) (Path A) and the
> `notebooks/setup/00_unity_catalog_setup.py` bootstrap notebook. Come back here
> when you want repeatable, scripted infrastructure for dev/staging/prod.

This folder contains Terraform code to provision Azure resources for Lives Remaining Labs:
- **Azure Databricks workspace** (Premium tier with Unity Catalog)
- **Azure Data Lake Storage (ADLS Gen2)** for the data lake
- **Azure Entra (AAD) Service Principal** for job automation
- **Unity Catalog** (metastore, catalogs, schemas)
- **DLT pipelines** and **Databricks Jobs** configurations
- **Azure Key Vault** integration for secrets

## Files

- `main.tf` — Azure provider & Databricks workspace definition
- `variables.tf` — Input variables (subscription_id, resource_group, etc.)
- `terraform.tfvars` — Local configuration (create from `.example` template)
- `adls.tf` — Azure Data Lake Storage (ADLS Gen2) setup
- `uc.tf` — Unity Catalog configuration
- `dlt.tf` — DLT pipeline definitions

## Quick Start (Azure)

```bash
# 1. Set Azure subscription context
az account set --subscription <subscription-id>

# 2. Create resource group (optional)
az group create --name lrl-rg --location eastus

# 3. Initialize & deploy Terraform
cd terraform
terraform init
terraform plan
terraform apply
```

## Prerequisites

- **Azure CLI** installed and authenticated (`az login`)
- **Terraform** >= 1.0 with Azure provider
- **Azure subscription** with:
  - Databricks workspace creation permissions
  - Storage account creation permissions
  - Service principal creation permissions (for automation)
- **Databricks account** (for workspace provisioning)

## Key Variables

| Variable | Example | Description |
|----------|---------|-------------|
| `subscription_id` | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` | Azure subscription ID |
| `resource_group_name` | `lrl-rg` | Azure resource group |
| `location` | `eastus` | Azure region |
| `workspace_name` | `lrl-workspace` | Databricks workspace name |
| `storage_account_name` | `lrlstorage01` | ADLS Gen2 account name |
| `storage_container_name` | `datalake` | Blob container for Bronze/Silver/Gold |

## Unity Catalog Setup

Unity Catalog requires:
- **Metastore**: Provisioned in one Azure region (e.g., East US)
- **ADLS Gen2 storage**: Location for the metastore external location
- **Managed identity** or **service principal**: For Databricks → storage access

This Terraform creates the UC setup automatically.

## More Details

See individual `*.tf` files for resource-specific configuration.

