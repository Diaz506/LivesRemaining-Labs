# Azure Setup Guide

This guide provisions the Azure + Databricks resources the labs need, using the
**Azure CLI** and the **Databricks UI**. It is the detailed companion to
[`docs/labs/prerequisites.md`](labs/prerequisites.md) **Path A (UI)**.

> Prefer scripted infrastructure? Use the optional
> [Terraform path](../terraform/README.md) instead — it provisions everything
> below in one `terraform apply`.

Throughout, the labs assume these names (change them consistently if you differ):

| Thing | Value used in the labs |
|-------|------------------------|
| Resource group | `lrl-rg` |
| Region | `eastus` |
| Databricks workspace | `lrl-workspace` |
| Storage account (ADLS Gen2) | `lrlstorage01` |
| Container | `datalake` |
| Databricks Access Connector | `lrl-connector` (managed identity) |
| Unity Catalog catalog | `labs` |
| Unity Catalog external location | `abfss://datalake@lrlstorage01.dfs.core.windows.net/` |

---

## 1. Sign in and set the subscription

```bash
az login
az account set --subscription "<subscription-id>"
az group create --name lrl-rg --location eastus
```

## 2. Create the ADLS Gen2 storage account + container

```bash
az storage account create \
  --name lrlstorage01 \
  --resource-group lrl-rg \
  --location eastus \
  --sku Standard_LRS \
  --kind StorageV2 \
  --hns true                       # hierarchical namespace = ADLS Gen2

az storage fs create \
  --account-name lrlstorage01 \
  --name datalake
```

## 3. Create the Databricks workspace (Premium)

Premium tier is required for Unity Catalog.

```bash
az databricks workspace create \
  --name lrl-workspace \
  --resource-group lrl-rg \
  --location eastus \
  --sku premium
```

> **Creating via the Portal?** On the workspace creation blade you'll see a
> **Workspace type** choice that defaults to **Serverless** — that's the
> recommended choice for these labs. They read/write your own ADLS Gen2 through
> **Unity Catalog external locations** (`abfss://…`) and run on **serverless
> compute / serverless DLT**, so no custom clusters or DBFS mounts are needed.
> (The legacy `/mnt/data` mount + service-principal approach is gone — UC's
> Access Connector handles storage auth.) Pick **Hybrid** only if you later need
> custom clusters, GPUs, or init scripts.

Open the workspace from the Portal (or `az databricks workspace show … --query workspaceUrl`).

## 4. Create an Access Connector for Unity Catalog

Unity Catalog reaches ADLS Gen2 through an **Azure Databricks Access Connector**
(a managed identity) — **not** a service principal with a client secret. This is
the only storage-auth identity you need; it works on serverless compute.

```bash
az databricks access-connector create \
  --name lrl-connector \
  --resource-group lrl-rg \
  --location eastus

# Grant it access to the data lake
CONNECTOR_ID=$(az databricks access-connector show -n lrl-connector -g lrl-rg --query id -o tsv)
PRINCIPAL_ID=$(az databricks access-connector show -n lrl-connector -g lrl-rg --query identity.principalId -o tsv)
STORAGE_ID=$(az storage account show -n lrlstorage01 -g lrl-rg --query id -o tsv)

az role assignment create \
  --assignee-object-id "$PRINCIPAL_ID" \
  --assignee-principal-type ServicePrincipal \
  --role "Storage Blob Data Contributor" \
  --scope "$STORAGE_ID"

echo "Access Connector resource ID (use as access_connector_id widget): $CONNECTOR_ID"
```

> No secret scope, no `sp-client-id`/`sp-secret`/`sp-tenant-id`, no mount. The
> setup notebook in the next step wraps this connector in a UC **storage
> credential** + **external location**, and the pipelines read `abfss://…`
> directly.

## 5. Bootstrap Unity Catalog

Run `notebooks/setup/00_unity_catalog_setup.py` to create the `labs` catalog, the
`bronze`/`silver`/`gold` schemas, the **storage credential + external location**
(pass the Access Connector resource ID from step 4 as the `access_connector_id`
widget), and grants. Verify:

```sql
SHOW SCHEMAS IN labs;   -- expect bronze, silver, gold
```

---

## ✅ Setup checklist

- [ ] Resource group `lrl-rg` created
- [ ] ADLS Gen2 `lrlstorage01` with container `datalake`
- [ ] Databricks **Premium** workspace running (Serverless workspace type)
- [ ] Access Connector `lrl-connector` with **Storage Blob Data Contributor**
- [ ] UC storage credential + external location (`abfss://datalake@lrlstorage01…`) created
- [ ] `labs` catalog + `bronze`/`silver`/`gold` schemas exist

**Next:** [Lab 0 — Sample data generation →](labs/lab-0-setup-data-generation.md)
