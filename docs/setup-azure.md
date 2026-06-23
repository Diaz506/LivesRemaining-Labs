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
| Storage account (ADLS Gen2) | `lrlstorage` |
| Container | `datalake` |
| Databricks secret scope | `lrl` |
| Unity Catalog catalog | `labs` |
| ADLS mount point | `/mnt/data` |

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
  --name lrlstorage \
  --resource-group lrl-rg \
  --location eastus \
  --sku Standard_LRS \
  --kind StorageV2 \
  --hns true                       # hierarchical namespace = ADLS Gen2

az storage fs create \
  --account-name lrlstorage \
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

Open the workspace from the Portal (or `az databricks workspace show … --query workspaceUrl`).

## 4. Create an Entra service principal for automation

Jobs and the ADLS mount authenticate as a **service principal** (not a human user).

```bash
az ad sp create-for-rbac --name "lrl-sp"
# Note the output: appId (client id), password (secret), tenant
```

Grant it read access to the data lake:

```bash
SP_APP_ID="<appId>"
STORAGE_ID=$(az storage account show -n lrlstorage -g lrl-rg --query id -o tsv)

az role assignment create \
  --assignee "$SP_APP_ID" \
  --role "Storage Blob Data Contributor" \
  --scope "$STORAGE_ID"
```

> **Unity Catalog note:** for the UC external location, UC uses an **Access
> Connector** (managed identity), not this service principal. See
> [`prerequisites.md`](labs/prerequisites.md) Step 1.3. The service principal
> here is for the `/mnt/data` mount and job automation.

## 5. Store secrets in a Databricks secret scope

Never hard-code credentials in notebooks. Create a scope named `lrl` and add the
service principal credentials (using the Databricks CLI):

```bash
databricks secrets create-scope lrl
databricks secrets put-secret lrl sp-client-id   # paste appId
databricks secrets put-secret lrl sp-secret      # paste password
databricks secrets put-secret lrl sp-tenant-id   # paste tenant
```

The labs read these as `dbutils.secrets.get("lrl", "sp-client-id")`, etc.

## 6. Mount ADLS Gen2 at `/mnt/data`

`src/dlt/bronze_pipeline.py` reads `/mnt/data/events/`. Run this **once** in a
notebook attached to an all-purpose cluster:

```python
configs = {
  "fs.azure.account.auth.type": "OAuth",
  "fs.azure.account.oauth.provider.type": "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider",
  "fs.azure.account.oauth2.client.id": dbutils.secrets.get("lrl", "sp-client-id"),
  "fs.azure.account.oauth2.client.secret": dbutils.secrets.get("lrl", "sp-secret"),
  "fs.azure.account.oauth2.client.endpoint":
      f"https://login.microsoftonline.com/{dbutils.secrets.get('lrl','sp-tenant-id')}/oauth2/v2.0/token",
}

# Idempotent: unmount first if it already exists
if any(m.mountPoint == "/mnt/data" for m in dbutils.fs.mounts()):
    dbutils.fs.unmount("/mnt/data")

dbutils.fs.mount(
  source="abfss://datalake@lrlstorage.dfs.core.windows.net/",
  mount_point="/mnt/data",
  extra_configs=configs,
)

display(dbutils.fs.ls("/mnt/data"))
```

> **Mounts vs. Unity Catalog:** mounts are the simplest way to keep the lab's
> DLT code short. In production, prefer reading via a **UC external location**
> (`abfss://…`) governed by a storage credential — see `prerequisites.md`.

## 7. Bootstrap Unity Catalog

Run `notebooks/setup/00_unity_catalog_setup.py` to create the `labs` catalog, the
`bronze`/`silver`/`gold` schemas, the external location, and grants. Verify:

```sql
SHOW SCHEMAS IN labs;   -- expect bronze, silver, gold
```

---

## ✅ Setup checklist

- [ ] Resource group `lrl-rg` created
- [ ] ADLS Gen2 `lrlstorage` with container `datalake`
- [ ] Databricks **Premium** workspace running
- [ ] Service principal `lrl-sp` with **Storage Blob Data Contributor**
- [ ] Secret scope `lrl` populated (`sp-client-id`, `sp-secret`, `sp-tenant-id`)
- [ ] `/mnt/data` mounted and listing the container
- [ ] `labs` catalog + `bronze`/`silver`/`gold` schemas exist

**Next:** [Lab 0 — Sample data generation →](labs/lab-0-setup-data-generation.md)
