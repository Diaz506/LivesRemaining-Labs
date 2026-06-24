# Lab 0: Setup & Sample Data Generation

**Goal:** Generate 100,000 synthetic player events and land them in ADLS Gen2 so the DLT pipelines have data to ingest.

⏱️ **Time:** ~30 min &nbsp;|&nbsp; **Prerequisites:** [Setup / Unity Catalog bootstrap](prerequisites.md)

> 🎮 **Mission Briefing**
>
> Maya Chen, Head of Live Ops, drops a 9am message: *"Day-30 retention fell six points after the last patch and analytics is flying blind — we have no event data to work with."* Before anyone can find the churning whales, the Player Intelligence team needs a realistic stream of player telemetry to build on. Today, you generate it.

---

### 🎯 Why this lab

The pipelines in Labs 1–3 read raw CSV events from `abfss://datalake@<account>.dfs.core.windows.net/events/`. Real telemetry contains PII, so we generate realistic *synthetic* events with `faker` instead.

---

> 🛣️ **Two ways to do this lab — pick one.**
>
> - **Option A — Local machine (Python + Azure CLI).** Generate the CSV on your
>   laptop and push it to ADLS Gen2 with `az`. Good if you're comfortable with a
>   local terminal and have the Azure CLI installed.
> - **Option B — Databricks notebook (serverless).** Generate *and* upload entirely
>   inside the workspace — no local Python, no `az login`. Recommended if you'd
>   rather stay in Databricks.
>
> Both land the exact same `events/raw_events.csv`. Do **Option A _or_ Option B**,
> then jump to [✅ Done when](#-done-when).

## 🪜 Option A — Local machine (Python + Azure CLI)

> 💻 **Where you run this.** Every command in Option A runs on **your local
> machine** (a terminal on your laptop), **not** in the Databricks workspace.
> You'll generate the CSV with Python, then push it to ADLS Gen2 with the Azure
> CLI. Make sure you've run `az login` first so the `az storage` commands can
> authenticate.

**What this step does and why.** The generator uses `faker` to invent realistic
player names/values and `pandas` to write the CSV. Installing them locally lets
you produce the dataset without touching any cloud compute.

```bash
pip install pandas faker numpy
```

### Step 2 — Generate the events CSV

**What this step does and why.** Runs the generator script to create 100k rows of
synthetic telemetry — this is the raw data Labs 1–3 will ingest. The flags control
volume (`--count`), how many distinct players (`--players`), and how far back the
timestamps span (`--days`); the values below are the defaults the labs expect.

From the repo root run the generator (it is already in `scripts/generate_events.py`):

```bash
python scripts/generate_events.py --output data/raw_events.csv --count 100000 --players 10000 --days 30
```

**Expected output (tail):**

```
✅ Saved 100,000 events to data/raw_events.csv

Summary:
  Total events: 100,000
  Unique players: ~10,000
  Event types: {'login': ..., 'kill': ..., 'purchase': ..., ...}
  Date range: <30 days ago> to <today>
```

> The CSV columns match the Bronze schema in [`../data-schema.md`](../data-schema.md): `event_id, player_id, event_type, timestamp, game_mode, region, platform, payload, ingest_ts, ingest_date`.

### Step 3 — Verify the file locally

**What this step does and why.** A quick local sanity check *before* you upload —
confirms the file has the expected shape (100k rows × 10 columns) and a healthy
spread of event types, so you don't push a broken file to the cloud.

```bash
python -c "import pandas as pd; df=pd.read_csv('data/raw_events.csv'); print(df.shape); print(df['event_type'].value_counts())"
```

You should see `(100000, 10)` and a distribution across the 6 event types.

### Step 4 — Create the `events/` path in ADLS Gen2

**What this step does and why.** The pipelines read from
`abfss://datalake@lrlstorage01.dfs.core.windows.net/events/`, so the CSV has to
land in an `events/` folder inside the `datalake` container. If you already created
the `datalake` container during [setup](prerequisites.md) (UI Step 1 or Terraform),
it exists — and the upload in Step 5 will create the `events/` folder automatically,
so this step is optional. Run it only if you want to create the folder explicitly:

```bash
az storage fs directory create \
  --account-name lrlstorage01 \
  --file-system datalake \
  --name events
```

### Step 5 — Upload the CSV to ADLS Gen2

**What this step does and why.** Copies your local CSV into the `events/` path so
Databricks can read it through the Unity Catalog external location you configured
in the prerequisites. This is the hand-off point from "local data" to "cloud data".

```bash
az storage fs file upload \
  --account-name lrlstorage01 \
  --file-system datalake \
  --source data/raw_events.csv \
  --path events/raw_events.csv
```

(Or use `azcopy copy "data/raw_events.csv" "https://lrlstorage01.blob.core.windows.net/datalake/events/"`.)

### Step 6 — Confirm the upload

**What this step does and why.** Lists the `events/` folder to prove the file
actually landed in the cloud. If `events/raw_events.csv` shows up here, Lab 1's
pipeline will be able to find it.

```bash
az storage fs file list --account-name lrlstorage01 --file-system datalake --path events -o table
```

You should see `events/raw_events.csv`.

---

## 🪜 Option B — Databricks notebook (serverless)

> 🧪 **Where you run this.** Everything below runs **inside a Databricks notebook**
> attached to **Serverless** compute — no local Python, no Azure CLI. It writes the
> CSV straight into your Unity Catalog external location, so the managed identity on
> your Access Connector handles auth (no mount, no service principal).
>
> Easiest setup: open this repo as a **Git folder** in the workspace
> (**Workspace → Create → Git folder**) so `scripts/generate_events.py` is already
> there, then create a new notebook next to it.

### Step 1 — Install the generator's dependencies

The generator uses `faker` (plus `pandas`/`numpy`); install them into the notebook
session, then restart Python so the imports are picked up.

```python
%pip install faker numpy pandas
dbutils.library.restartPython()
```

### Step 2 — Generate and upload in one cell

`generate_events()` is pure Python (no Spark), so it runs on the serverless driver.
We write the CSV to the driver's local `/tmp`, then `dbutils.fs.cp` copies it into
the `events/` path through the external location.

```python
import sys, os
sys.path.append(os.path.abspath("../../scripts"))   # path to scripts/generate_events.py
from generate_events import generate_events
import pandas as pd

events = generate_events(num_events=100000, num_players=10000, days_back=30)
df = pd.DataFrame(events)

df.to_csv("/tmp/raw_events.csv", index=False)
dbutils.fs.cp(
    "file:/tmp/raw_events.csv",
    "abfss://datalake@lrlstorage01.dfs.core.windows.net/events/raw_events.csv"
)
```

> **Can't import `generate_events`?** The `../../scripts` path assumes the notebook
> sits inside the repo's Git folder. If it doesn't, adjust the path, clone the repo
> first, or paste the generator's functions into a cell.

### Step 3 — Confirm the upload

Lists the `events/` folder to prove the file landed — the equivalent of Option A's
Step 6, but from the notebook.

```python
display(dbutils.fs.ls("abfss://datalake@lrlstorage01.dfs.core.windows.net/events/"))
```

You should see `raw_events.csv` (~12–15 MB) in the listing.

> 💡 Prefer to skip the temp file? You can write with Spark instead —
> `spark.createDataFrame(df).coalesce(1).write.option("header","true").csv("abfss://datalake@lrlstorage01.dfs.core.windows.net/events/")`
> — but that produces `part-*.csv` files rather than a single `raw_events.csv`.
> Lab 1's Autoloader reads either layout fine.

---

## ✅ Done when

- [ ] You generated 100k events (Option A: `data/raw_events.csv` locally; Option B: in the notebook)
- [ ] `events/raw_events.csv` is present in the `datalake` container
- [ ] The 6 event types and 4 regions appear in the summary

## 🧯 Troubleshooting

| Symptom | Fix |
|---------|-----|
| `Error: Install dependencies...` when running the script | Run the install step (`pip install pandas faker numpy`, or `%pip install` in Option B). |
| `az: command not found` (Option A) | Install the Azure CLI, then run `az login`. |
| `ModuleNotFoundError: faker` (Option B) | Re-run the `%pip install` cell, then `dbutils.library.restartPython()` before importing. |
| `cannot import name 'generate_events'` (Option B) | The notebook isn't in the repo Git folder — fix the `sys.path.append(...)` path, or clone the repo. |
| Upload `403` / `AuthorizationPermissionMismatch` | Option A: your identity needs **Storage Blob Data Contributor** on the storage account. Option B: the Access Connector's managed identity needs it (set during prerequisites Step 3). |
| `ContainerNotFound` / filesystem missing | Create the `datalake` container first (prerequisites UI Step 1), then retry. |

**Next:** [Lab 1 — Bronze ingestion →](lab-1-bronze-ingestion.md)
