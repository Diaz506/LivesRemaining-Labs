# Terraform — Databricks Infrastructure

This folder contains Terraform code to provision:
- Databricks workspace (or connect to existing)
- Unity Catalog (metastore, catalogs, schemas)
- DLT pipelines and Databricks Jobs
- Service principals for job automation

## Files

- `main.tf` — Databricks provider and resource definitions
- `variables.tf` — Input variables (workspace URL, token, UC catalog name)
- `terraform.tfvars` — Local configuration (create from `.example` template)

## Quick Start

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

## Prerequisites

- Terraform >= 1.0
- Databricks account and workspace created
- Service principal or personal access token (PAT) for Databricks API

## Key Resources

- **Databricks workspace** — compute and collaboration hub
- **Unity Catalog** — gov namespace (database → schema → table)
- **DLT pipelines** — automated ETL orchestration
- **Databricks Jobs** — scheduled training & scoring

More details in individual `*.tf` files.
