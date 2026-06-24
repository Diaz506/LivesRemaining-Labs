# Databricks notebook source
# COMMAND ----------

# MAGIC %md
# MAGIC # Lab 0 (Option B): Generate & Upload Synthetic Events
# MAGIC ## Lives Remaining Labs — Azure Databricks
# MAGIC
# MAGIC **Fictional Company**: Lives Remaining Labs is a fictional multiplayer game studio.
# MAGIC
# MAGIC ### 🎯 Goal
# MAGIC Generate 100,000 synthetic player events and land them at
# MAGIC `abfss://datalake@lrlstorage01.dfs.core.windows.net/events/` so the Lab 1 DLT
# MAGIC pipeline has data to ingest — **entirely inside Databricks**, with no local
# MAGIC Python and no Azure CLI.
# MAGIC
# MAGIC ### 🧪 Where this runs
# MAGIC Attach this notebook to **Serverless** compute. It writes straight into your
# MAGIC Unity Catalog **external location**, so the managed identity on your Access
# MAGIC Connector handles auth — no mount, no service principal.
# MAGIC
# MAGIC > This is the notebook equivalent of `scripts/generate_events.py`. The
# MAGIC > generator logic is inlined below so the notebook is self-contained (it does
# MAGIC > not need to import the script from a Git folder).

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 — Install the generator's dependencies
# MAGIC
# MAGIC The generator uses `faker` (plus `pandas`/`numpy`). This must be its **own
# MAGIC cell, run first**, because `dbutils.library.restartPython()` **restarts the
# MAGIC Python interpreter** — which clears every variable, import, and function in the
# MAGIC session. If you combined this with the generation code below, the restart
# MAGIC would wipe that work. `%pip` is a notebook magic (not Python), so it only
# MAGIC belongs here in the notebook, never inside a `.py` module.

# COMMAND ----------

# MAGIC %pip install faker numpy pandas
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2 — Parameters
# MAGIC
# MAGIC Widgets let you tweak volume without editing code. Defaults match what the
# MAGIC labs expect. `storage_account` / `container` must match your prerequisites.

# COMMAND ----------

dbutils.widgets.text("storage_account", "lrlstorage01", "ADLS Gen2 account name")
dbutils.widgets.text("container", "datalake", "ADLS Gen2 container")
dbutils.widgets.text("num_events", "100000", "Number of events")
dbutils.widgets.text("num_players", "10000", "Number of unique players")
dbutils.widgets.text("days_back", "30", "Days of history")

storage_account = dbutils.widgets.get("storage_account").strip()
container = dbutils.widgets.get("container").strip()
num_events = int(dbutils.widgets.get("num_events"))
num_players = int(dbutils.widgets.get("num_players"))
days_back = int(dbutils.widgets.get("days_back"))

events_uri = f"abfss://{container}@{storage_account}.dfs.core.windows.net/events"
target_file = f"{events_uri}/raw_events.csv"

print(f"Target:  {target_file}")
print(f"Volume:  {num_events:,} events / {num_players:,} players / {days_back} days")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3 — Generator logic
# MAGIC
# MAGIC Pure Python (no Spark) — runs on the serverless driver. Mirrors
# MAGIC `scripts/generate_events.py`; the CSV columns match the Bronze schema in
# MAGIC `docs/data-schema.md`.

# COMMAND ----------

import json
import uuid
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

EVENT_TYPES = ["login", "kill", "death", "purchase", "session_end", "logout"]
GAME_MODES = ["deathmatch", "capture_flag", "ranked", "casual"]
REGIONS = ["NA", "EU", "APAC", "LATAM"]
PLATFORMS = ["PC", "Console", "Mobile"]
WEAPONS = ["sniper_rifle", "assault_rifle", "shotgun", "pistol", "rocket_launcher"]
SKINS = ["dragon_blue", "neon_pink", "gold_warrior", "shadow_assassin", "fire_phoenix"]


def _pid():
    return f"player_{uuid.uuid4().hex[:12]}"


def _eid():
    return str(uuid.uuid4())


def _ingest(ts):
    return (ts + timedelta(seconds=random.randint(1, 10))).isoformat()


_RANDOM_MODE = object()


def _base(player_id, event_type, ts, payload, game_mode=_RANDOM_MODE):
    return {
        "event_id": _eid(),
        "player_id": player_id,
        "event_type": event_type,
        "timestamp": ts.isoformat(),
        "game_mode": random.choice(GAME_MODES) if game_mode is _RANDOM_MODE else game_mode,
        "region": random.choice(REGIONS),
        "platform": random.choice(PLATFORMS),
        "payload": json.dumps(payload),
        "ingest_ts": _ingest(ts),
        "ingest_date": ts.date().isoformat(),
    }


def _make_event(event_type, player_id, ts):
    if event_type == "login":
        return _base(player_id, "login", ts, {
            "session_token": str(uuid.uuid4()), "ip_country": fake.country_code()})
    if event_type == "kill":
        return _base(player_id, "kill", ts, {
            "opponent_id": _pid(), "weapon": random.choice(WEAPONS),
            "headshot": random.choice([True, False]),
            "experience_granted": random.randint(50, 200)})
    if event_type == "death":
        return _base(player_id, "death", ts, {
            "killed_by": _pid(), "weapon": random.choice(WEAPONS),
            "distance_m": random.randint(5, 500)})
    if event_type == "purchase":
        skin = random.choice(SKINS)
        return _base(player_id, "purchase", ts, {
            "item_id": f"skin_{skin}",
            "item_name": f"{skin.replace('_', ' ').title()} Skin",
            "item_price_usd": random.choice([4.99, 9.99, 19.99, 29.99]),
            "currency": "USD",
            "payment_method": random.choice(["credit_card", "paypal", "google_play", "apple_pay"])})
    if event_type == "session_end":
        return _base(player_id, "session_end", ts, {
            "total_kills": random.randint(0, 100), "total_deaths": random.randint(0, 50),
            "total_earned_xp": random.randint(100, 10000),
            "duration_seconds": random.randint(300, 7200),
            "items_purchased": random.randint(0, 5)})
    # logout — game_mode is intentionally None (no active match)
    return _base(player_id, "logout", ts,
                 {"reason": random.choice(["user_quit", "timeout", "connection_lost"])},
                 game_mode=None)


def generate_events(num_events=100000, num_players=10000, days_back=30):
    players = [_pid() for _ in range(num_players)]
    start = datetime.utcnow() - timedelta(days=days_back)
    events = []
    for i in range(num_events):
        if i % 10000 == 0:
            print(f"  {i:,} / {num_events:,}")
        ts = start + timedelta(
            days=random.randint(0, days_back - 1),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59),
        )
        events.append(_make_event(random.choice(EVENT_TYPES), random.choice(players), ts))
    return events

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4 — Generate, then upload to the external location
# MAGIC
# MAGIC On **serverless**, `dbutils.fs` can't read the driver's local `/tmp`
# MAGIC (`LocalFilesystemAccessDeniedException`). So instead of a temp file, we build a
# MAGIC Spark DataFrame and write it **directly** to the external location. Spark emits
# MAGIC a `part-*.csv`, which we then rename to a clean `raw_events.csv` (Lab 1's
# MAGIC Autoloader actually reads the whole `events/` folder, so either name works).

# COMMAND ----------

import pandas as pd

events = generate_events(num_events, num_players, days_back)
df = pd.DataFrame(events)

# Write directly to cloud storage via Spark (serverless-safe — no local FS).
tmp_dir = f"{events_uri}/_tmp_raw"
(
    spark.createDataFrame(df)
    .coalesce(1)
    .write.mode("overwrite")
    .option("header", "true")
    .csv(tmp_dir)
)

# Spark writes part-*.csv inside tmp_dir; move the single part to a clean filename.
part = [f.path for f in dbutils.fs.ls(tmp_dir) if f.name.endswith(".csv")][0]
dbutils.fs.mv(part, target_file)
dbutils.fs.rm(tmp_dir, recurse=True)

print(f"\n✅ Uploaded {len(df):,} events to {target_file}")
print(f"  Unique players: {df['player_id'].nunique():,}")
print(f"  Event types:    {df['event_type'].value_counts().to_dict()}")
print(f"  Regions:        {df['region'].value_counts().to_dict()}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5 — Confirm the upload

# COMMAND ----------

display(dbutils.fs.ls(events_uri))

# COMMAND ----------

# MAGIC %md
# MAGIC ### ✅ Done
# MAGIC You should see `raw_events.csv` (~12–15 MB) in the listing above. You're ready
# MAGIC for **Lab 1 — Bronze ingestion**.
