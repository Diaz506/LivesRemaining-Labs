# Lab 2: Silver Transformations & Quality Checks

**Goal:** Turn raw Bronze events into clean, typed, deduplicated Silver tables (`labs.silver.*`) with DLT expectations.

⏱️ **Time:** ~1.5 hr &nbsp;|&nbsp; **Prerequisites:** [Lab 1](lab-1-bronze-ingestion.md)

---

### 🎯 Why this lab

Bronze is raw and untrustworthy (string timestamps, mixed casing, JSON blobs, duplicates). The Silver layer is the *trusted* source for Gold features, ML, and BI. `src/dlt/silver_pipeline.py` casts types, normalizes casing, parses payload JSON into columns, deduplicates by `event_id`, and derives sessions.

**Artifacts:** `src/dlt/silver_pipeline.py` (pipeline), `notebooks/dlt/02_silver_transformations.py` (walkthrough).

**Outputs:**

| Table | What it is |
|-------|-----------|
| `labs.silver.player_events_cleaned` | Deduplicated, typed, payload-parsed events |
| `labs.silver.player_sessions` | One row per completed session (from `session_end`) |
| `labs.silver.player_purchase_events` | Clean purchase events for ARPU |
| `labs.silver.silver_quality_summary` | Daily event counts / quality metrics |

---

## 🪜 Steps

### Step 1 — Confirm Bronze exists

```sql
SELECT COUNT(*) FROM labs.bronze.lives_remaining_raw_events;
```

If this errors, finish [Lab 1](lab-1-bronze-ingestion.md) first.

### Step 2 — Read the transformation logic

Open `src/dlt/silver_pipeline.py` and note:
- `player_events_cleaned` (lines 20–77): `to_timestamp`, `lower/trim/upper/initcap` normalization, `dropDuplicates(["event_id"])`, and `get_json_object` payload parsing.
- `player_sessions` (lines 80–125): filters `session_end`, derives a deterministic `session_id`, computes `duration_min`, `kd_ratio`, `win_rate`.
- Expectations: `@dlt.expect_or_drop` (hard rules) vs `@dlt.expect` (warn-only) — e.g. `positive_duration`, `known_region`.

### Step 3 — Create the Silver DLT pipeline

**Workflows → Delta Live Tables → Create pipeline**:

| Setting | Value |
|---------|-------|
| Pipeline name | `lives-remaining-silver` |
| Source code | `…/src/dlt/silver_pipeline.py` |
| Destination | Catalog `labs`, Target schema `silver` |
| Pipeline mode | **Triggered** |

> The pipeline reads `labs.bronze.lives_remaining_raw_events` (a different catalog/schema than its target), so make sure the cluster identity can read `labs.bronze`.

### Step 4 — Run and watch expectations

Click **Start**. In the DLT graph, open each table node → **Data quality** tab and confirm pass/drop counts for:
- `valid_event_id`, `valid_player_id`, `valid_event_type`
- `positive_duration` on `player_sessions`

### Step 5 — Validate the outputs

```sql
-- Cleaned events: types and parsed columns
SELECT event_type_normalized, COUNT(*) AS n
FROM labs.silver.player_events_cleaned GROUP BY event_type_normalized ORDER BY n DESC;

-- No duplicate event_ids
SELECT COUNT(*) - COUNT(DISTINCT event_id) AS dupes FROM labs.silver.player_events_cleaned;  -- expect 0

-- Sessions look sane
SELECT ROUND(AVG(duration_min),1) avg_min, ROUND(AVG(kd_ratio),2) avg_kd, ROUND(AVG(win_rate),2) avg_wr
FROM labs.silver.player_sessions;

-- Purchases ready for ARPU
SELECT COUNT(*) purchases, ROUND(SUM(item_price_usd),2) revenue FROM labs.silver.player_purchase_events;
```

Run the matching cells in `notebooks/dlt/02_silver_transformations.py` for a guided view.

---

## ✅ Done when

- [ ] All four `labs.silver.*` tables are populated
- [ ] `dupes = 0` for `event_id`
- [ ] Sessions have `duration_min > 0` and reasonable `kd_ratio` / `win_rate`
- [ ] Expectation metrics visible in the DLT UI

## 🧯 Troubleshooting

| Symptom | Fix |
|---------|-----|
| `Table not found: labs.bronze...` | Run Lab 1 and confirm its target schema is `labs.bronze`. |
| All session rows dropped | They derive from `session_end` events — confirm Lab 0 generated them. |
| Nulls in parsed columns | Expected for non-matching event types (e.g. `weapon` is null for purchases). |

**Next:** [Lab 3 — Feature engineering →](lab-3-feature-engineering.md)
