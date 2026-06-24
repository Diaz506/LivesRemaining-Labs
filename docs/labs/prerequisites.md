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
| Databricks workspace | `lrl-workspace` (free to choose — no code references it) |
| Storage account (ADLS Gen2) | `lrlstorage01` |
| Container | `datalake` |
| Access Connector (managed identity) | `lrl-connector` |
| Unity Catalog catalog | `labs` |

> ⚠️ **Storage names are baked into the pipeline.**
> `src/dlt/bronze_pipeline.py` reads
> `abfss://datalake@lrlstorage01.dfs.core.windows.net/events/`. If you pick a
> different **storage account** or **container** name, update that path in
> `bronze_pipeline.py` **and** the matching widgets in
> `notebooks/dlt/01_ingest_bronze.py` / `notebooks/setup/00_unity_catalog_setup.py`.
> Storage account names must be globally unique and lowercase — if `lrlstorage01`
> is taken, choose another and update the path.

---

## 🅰️ Path A — Set up via the UI (default)

### Step 1 — Create the workspace & storage (Azure Portal)

1. **Resource group** — Portal → *Resource groups* → **Create**, name it
   **`lrl-rg`** in your chosen region. Create everything below inside it so the
   lab resources stay together and are easy to clean up afterward.
2. **Azure Databricks workspace** — Portal → *Create resource* → **Azure
   Databricks**, name it **`lrl-workspace`** (any name works — no code depends on
   it) → pricing tier **Premium** (required for Unity Catalog).
   - **Workspace type → leave the default `Serverless`.** These labs read/write
     **your own ADLS Gen2** through Unity Catalog **external locations**
     (`abfss://…`, governed by the Access Connector below) and run on
     **serverless compute / serverless DLT** — no DBFS mounts, custom clusters,
     or service-principal Spark configs. Serverless *"uses Databricks-managed
     default storage and serverless compute"* and lets you *"connect to your
     cloud storage at any time"*, which is exactly the UC external-location
     pattern these labs use. Pick **Hybrid** only if you later need custom
     clusters, GPUs, or init scripts.
3. **ADLS Gen2 storage** — Portal → *Create resource* → **Storage account**,
   name it **`lrlstorage01`** (must be globally unique — pick another lowercase
   name if taken, and update the pipeline path accordingly).
   - **Basics tab:** Resource group `lrl-rg`; **Performance → Standard**;
     **Redundancy → LRS** (cheapest, fine for a lab — GRS also works). Put it in
     the **same region as your Databricks workspace**.
   - **Advanced tab → check ✅ “Enable hierarchical namespace.”** This is what
     turns the account into **ADLS Gen2** — without it the `abfss://` paths the
     pipeline uses won't work.
   - After the account is created, open it → **Containers → + Container** and
     create one named **`datalake`**.
4. **Access Connector for Azure Databricks** — Portal → *Create resource* →
   **Access Connector for Azure Databricks** (a managed identity), name it
   **`lrl-connector`**. Then on the storage account → **Access Control (IAM)** →
   assign **Storage Blob Data Contributor** to that Access Connector.

### Step 2 — Open the workspace & confirm a Unity Catalog metastore

**What this step does and why.** Unity Catalog (UC) is the governance layer that
holds **catalogs → schemas → tables** and controls who can access them. Before
you can create the `labs` catalog in Step 3, your workspace must be attached to a
UC **metastore** — the top-level container (one per region) that UC catalogs live
in. This step is just to **confirm** that attachment exists; you usually don't
have to create anything.

1. Azure Portal → your **`lrl-workspace`** resource → click **Launch Workspace**.
2. In the workspace left nav, click **Catalog** to open Catalog Explorer.
3. If you see catalogs listed (e.g. `<workspace-name>`, `system`, `samples`),
   a metastore **is attached** — you're done with this step. Modern Azure
   Databricks **auto-creates and attaches a metastore per region** for you.

> You won't see a `labs` catalog yet — that's what Step 3 creates. Seeing the
> built-in catalogs is enough to confirm the metastore is in place.

> **Only if Catalog reports no metastore:** go to the **Databricks Account
> console** (accounts.azuredatabricks.net) → **Catalog / Metastores**, create or
> attach a metastore in your region, and assign it to `lrl-workspace`. (This
> requires account-admin rights.)

### Step 3 — Bootstrap the catalog

**What this step does and why.** So far you have a workspace, an empty ADLS Gen2
account, and an Access Connector — but Unity Catalog doesn't yet know how to
reach your storage, and there's no place to put tables. You'll create four
things:

| Object | What it is / why you need it |
|--------|------------------------------|
| **Storage credential** | Wraps your **Access Connector** (managed identity) so UC can authenticate to ADLS Gen2 — **no keys or secrets** stored anywhere. |
| **External location** | Registers the path `abfss://datalake@lrlstorage01…` and says *"use that credential to read/write here."* This replaces the old mount. |
| **Catalog `labs` + schemas** | The `labs` catalog with `bronze` / `silver` / `gold` schemas — the medallion namespaces every later lab writes to (`labs.bronze.*`, etc.). |
| **Grants** | Least-privilege permissions so the pipelines can use the catalog/schemas and read/write the external location. |

The first two (storage credential + external location) are created in the
**Catalog Explorer UI**; the catalog/schemas/grants are created by the **setup
notebook**.

> 💡 **Why the UI for the first two?** The SQL admin DDL
> (`CREATE STORAGE CREDENTIAL` / `CREATE EXTERNAL LOCATION`) is **not parseable on
> all compute** — on serverless you'll often hit
> `PARSE_SYNTAX_ERROR near 'STORAGE'`. The Catalog Explorer UI is the reliable
> path and is what the official Databricks docs use. (You also need the
> **`CREATE STORAGE CREDENTIAL`** privilege — account/metastore admin has it.)

**Before you start — grab the Access Connector resource ID.** Azure Portal → your
**`lrl-connector`** Access Connector → **Overview** / **Properties** → copy the
**Resource ID**:

```
/subscriptions/<sub-id>/resourceGroups/lrl-rg/providers/Microsoft.Databricks/accessConnectors/lrl-connector
```

#### 3a — Create the storage credential + external location (Catalog Explorer UI)

In the workspace, open **Catalog** (left nav) → **+ Add**:

1. **Add a storage credential**
   - Credential type: **Azure Managed Identity**
   - Name: **`labs_storage_cred`**
   - Access Connector ID: the Resource ID you copied above
2. **Add an external location**
   - Name: **`labs_datalake`**
   - URL: **`abfss://datalake@lrlstorage01.dfs.core.windows.net/`**
   - Storage credential: **`labs_storage_cred`**
   - Click **Test connection** — **Read / List / Write / Delete / Path Exists /
     Hierarchical Namespace** should all pass. The **File Events** checks may show
     **Failed** — that's **expected and safe to ignore**; file events are an
     optional Autoloader optimization needing extra roles you don't need for this
     lab. Click **Force create** (Autoloader falls back to directory listing,
     which is fine at lab scale).

#### 3b — Create the catalog, schemas & grants (setup notebook)

1. Import this repo into the workspace: **Workspace → Create → Git folder**,
   paste the repo URL.
2. Open **`notebooks/setup/00_unity_catalog_setup.py`**. Opening it only shows
   the code — attach compute: **top-right corner** → **Connect** dropdown →
   **Serverless** (or any UC-enabled cluster). Wait for connected/green.
3. The widgets are **input boxes at the top of the notebook** (edit the boxes,
   not the code). The defaults already match this lab — and since you created the
   storage objects in 3a, **leave `access_connector_id` BLANK** so the notebook
   skips that DDL. Then **Run all**.

| Widget | What to enter | Why |
|--------|---------------|-----|
| `catalog` | `labs` *(default)* | Top-level catalog name the labs expect. |
| `storage_account` | `lrlstorage01` *(default)* | Builds the `abfss://` URL used for verification. |
| `container` | `datalake` *(default)* | The container you created in Step 1. |
| `access_connector_id` | **leave blank** | You already created the credential in 3a; blank skips the failing DDL. |
| `job_principal` | *(optional)* a group or service principal | Grants pipeline access; leave blank to skip grants. |

As it runs you'll see it create the `labs` catalog and list the `bronze` /
`silver` / `gold` schemas, then verify the external location is reachable.

> Already comfortable and on compute that supports the DDL? You *can* instead
> paste the Access Connector ID into `access_connector_id` and let the notebook
> attempt 3a for you — it's wrapped in `try/except`, so if the DDL fails it just
> points you back to the UI steps above.

### Step 4 — Verify

**What this step does and why.** A quick sanity check that Step 3 actually
created the medallion namespaces. If these schemas exist, every later lab can
write to `labs.bronze.*`, `labs.silver.*`, and `labs.gold.*` without the
"catalog/schema not found" error.

**Where to run it** — pick whichever is handiest:
- **In the setup notebook:** add a new cell and prefix it with the SQL magic:
  ```python
  %sql
  SHOW SCHEMAS IN labs;
  ```
  (Part 3 of the notebook already runs this, so you may already see the result.)
- **SQL Editor:** left nav → **SQL Editor** → paste the query → **Run**.
- **Catalog Explorer (no query):** left nav → **Catalog** → expand **`labs`** and
  confirm the three schemas are listed.

```sql
SHOW SCHEMAS IN labs;   -- expect bronze, silver, gold
```

You should see **`bronze`**, **`silver`**, and **`gold`** (plus the built-in
`information_schema` / `default`). You can also confirm visually in **Catalog
Explorer** — the `labs` catalog now appears alongside `system` and `samples`,
with the three schemas under it.

> Don't see them? Re-open Step 3's notebook and re-run it — check that
> `access_connector_id` was filled in (the "External location … ready" line must
> print) and that there were no permission errors. It's idempotent, so re-running
> is safe.

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
