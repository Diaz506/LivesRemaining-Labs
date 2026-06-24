# Prerequisites & Setup (Azure)

Before Lab 0, you need an Azure Databricks workspace with Unity Catalog and the
`labs` catalog/schemas the labs read and write.

There are **two ways** to set this up. Start with **Path A (UI)** — it's the
default for the labs and teaches the Unity Catalog concepts as you click. Use
**Path B (Terraform)** later if you want repeatable, scripted infrastructure.

> ⚠️ Every lab uses three-level Unity Catalog names (`labs.bronze.*`,
> `labs.silver.*`, `labs.gold.*`). You **must** finish one of the two paths
> below before Lab 0, or the pipelines fail with "catalog/schema not found".

---

## What you need first

| Requirement | Notes |
|-------------|-------|
| **Azure subscription** | With permission to create Databricks, Storage, and Entra resources |
| **Python 3.9+** locally | For Lab 0's event generator |
| **Azure CLI** (`az login`) | For uploading sample data (Lab 0) |
| **Terraform ≥ 1.0** | **Only** for Path B (advanced) |

---

## 📛 Names used throughout these labs

Use these names when you create resources so the notebook widgets and pipeline
code work without edits. Change them only if you update every reference
consistently.

| Resource | Name used in the labs |
|----------|-----------------------|
| Resource group | `lrl-rg` |
| Region | `eastus` |
| Storage account (ADLS Gen2) | `lrlstorage` |
| Container | `datalake` |
| Access Connector (managed identity) | `lrl-connector` |
| Unity Catalog catalog | `labs` |

> ⚠️ **Storage names are baked into the pipeline.**
> `src/dlt/bronze_pipeline.py` reads
> `abfss://datalake@lrlstorage.dfs.core.windows.net/events/`. If you pick a
> different **storage account** or **container** name, update that path in
> `bronze_pipeline.py` **and** the matching widgets in
> `notebooks/dlt/01_ingest_bronze.py` / `notebooks/setup/00_unity_catalog_setup.py`.
> Storage account names must be globally unique and lowercase — if `lrlstorage`
> is taken, choose another and update the path.

---

## 🅰️ Path A — Set up via the UI (default)

### Step 1 — Create the workspace & storage (Azure Portal)

1. **Azure Databricks workspace** — Portal → *Create resource* → **Azure
   Databricks** → pricing tier **Premium** (required for Unity Catalog).
   - **Workspace type → leave the default `Serverless`.** These labs read/write
     **your own ADLS Gen2** through Unity Catalog **external locations**
     (`abfss://…`, governed by the Access Connector below) and run on
     **serverless compute / serverless DLT** — no DBFS mounts, custom clusters,
     or service-principal Spark configs. Serverless *"uses Databricks-managed
     default storage and serverless compute"* and lets you *"connect to your
     cloud storage at any time"*, which is exactly the UC external-location
     pattern these labs use. Pick **Hybrid** only if you later need custom
     clusters, GPUs, or init scripts.
2. **ADLS Gen2 storage** — Portal → *Create resource* → **Storage account**,
   name it **`lrlstorage`** (must be globally unique — pick another lowercase
   name if taken, and update the pipeline path accordingly) → enable
   **Hierarchical namespace** (this makes it ADLS Gen2). Create a container named
   **`datalake`**.
3. **Access Connector for Azure Databricks** — Portal → *Create resource* →
   **Access Connector for Azure Databricks** (a managed identity), name it
   **`lrl-connector`**. Then on the storage account → **Access Control (IAM)** →
   assign **Storage Blob Data Contributor** to that Access Connector.

### Step 2 — Attach a Unity Catalog metastore

In the **Databricks Account console** (accounts.azuredatabricks.net) →
**Catalog / Metastores**, create or attach a metastore in your region and assign
it to your workspace. (Most new workspaces already have one.)

### Step 3 — Bootstrap the catalog (run the setup notebook)

Import this repo into the workspace (**Workspace → Create → Git folder**) and
run **`notebooks/setup/00_unity_catalog_setup.py`** on **serverless** (or any
UC-enabled cluster). Set the widgets:

| Widget | Example |
|--------|---------|
| `catalog` | `labs` |
| `storage_account` | `lrlstorage` |
| `container` | `datalake` |
| `access_connector_id` | `/subscriptions/.../accessConnectors/<name>` |
| `job_principal` | (optional) a group/SP to grant access |

The notebook creates the **storage credential**, **external location**, the
`labs` **catalog**, the `bronze`/`silver`/`gold` **schemas**, and the **grants**
— all idempotent (`CREATE ... IF NOT EXISTS`), so it's safe to re-run.

> Prefer pure click-ops? You can do the same in **Catalog Explorer**: create a
> storage credential → external location → catalog `labs` → schemas
> `bronze`/`silver`/`gold`. The notebook just scripts those clicks.

### Step 4 — Verify

```sql
SHOW SCHEMAS IN labs;   -- expect bronze, silver, gold
```

✅ You're ready for [Lab 0](lab-0-setup-data-generation.md).

---

## 🅱️ Path B — Provision via Terraform (advanced, optional)

Once you're comfortable with the concepts, the [`terraform/`](../../terraform/)
folder provisions the **same** setup as repeatable infrastructure-as-code:
workspace, ADLS Gen2 + Access Connector, the storage credential/external
location, and the `labs` catalog/schemas/grants.

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars   # fill in your values
terraform init
terraform plan
terraform apply
```

Use this for dev/staging/prod environments (pass a different `catalog_name`).
See [`terraform/README.md`](../../terraform/README.md) for variables and details.

> You only need **one** path. If you ran Terraform, skip Path A; the setup
> notebook is still handy for re-applying grants interactively.

---

👉 **[Detailed Azure Setup Guide →](../setup-azure.md)**

**Next:** [Lab 0 — Sample data generation →](lab-0-setup-data-generation.md)
