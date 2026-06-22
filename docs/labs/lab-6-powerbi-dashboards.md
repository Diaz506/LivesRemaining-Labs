# Lab 6: Power BI Dashboards & Fabric Integration

**Goal:** Expose BI-friendly views over the Gold tables and connect Power BI / Fabric to Databricks SQL for interactive dashboards.

⏱️ **Time:** ~2 hr &nbsp;|&nbsp; **Prerequisites:** [Lab 5](lab-5-batch-scoring.md)

---

### 🎯 Why this lab

Business users need visuals, not Delta tables. `notebooks/powerbi/06_powerbi_dashboard_setup.py` creates stable SQL views; Power BI connects to a Databricks **SQL Warehouse** via DirectQuery and refreshes each morning.

**Views created (see `powerbi/README.md`):**

| View | Content |
|------|---------|
| `labs.gold.vw_retention_churn` | Churn KPIs by date, region, platform, risk tier |
| `labs.gold.vw_player_segments` | Engagement & revenue cohort summaries |
| `labs.gold.vw_arpu_summary` | Premium tier & monetization metrics |
| `labs.gold.player_churn_scores` | Player-level drillthrough / action list |

---

## 🪜 Steps

### Step 1 — Create the BI views

Run `notebooks/powerbi/06_powerbi_dashboard_setup.py` on a cluster (or paste its SQL into a SQL warehouse). Confirm:

```sql
SELECT * FROM labs.gold.vw_retention_churn LIMIT 10;
SELECT * FROM labs.gold.vw_arpu_summary    LIMIT 10;
```

### Step 2 — Create a SQL Warehouse

**SQL → SQL Warehouses → Create**: serverless, size **2X-Small** is fine for the lab. Once running, open **Connection details** and copy:
- **Server hostname**
- **HTTP path**

### Step 3 — Connect Power BI Desktop

In Power BI Desktop: **Get Data → Azure Databricks**:
1. Paste **Server hostname** and **HTTP path**
2. Data Connectivity mode: **DirectQuery**
3. Sign in with Azure AD (or a PAT)
4. Select catalog `labs` → schema `gold` → the four views/tables above → **Load**

### Step 4 — Build the report pages

Create four pages:

| Page | Visuals (source) |
|------|------------------|
| **Retention & Churn** | Players by `risk_tier` over `compute_date`; avg `churn_probability` by region/platform (`vw_retention_churn`) |
| **Revenue & ARPU** | Spend by `premium_tier`; whale share (`vw_arpu_summary`) |
| **Segments** | Engagement × revenue matrix (`vw_player_segments`) |
| **Action list** | Table of high-risk, high-spend players (`player_churn_scores`) with drillthrough |

### Step 5 — Publish and schedule refresh

1. **Publish** to a Power BI workspace.
2. In the service, configure **Scheduled refresh** at **03:00 UTC** (after the 02:00 scoring job).

> **Fabric alternative:** use a Lakehouse SQL endpoint / shortcut to `labs.gold` and build the report in Fabric instead of Power BI Desktop.

---

## ✅ Done when

- [ ] The three `vw_*` views return rows
- [ ] Power BI connects to the SQL Warehouse via DirectQuery
- [ ] A 4-page report is published with scheduled refresh at 03:00 UTC

## 🧯 Troubleshooting

| Symptom | Fix |
|---------|-----|
| Views empty | Run Lab 5 so `player_churn_scores` exists. |
| Power BI sign-in fails | Confirm the SQL Warehouse is running and you have `USE CATALOG labs` + `SELECT` on `labs.gold`. |
| Slow visuals | Switch heavy pages from DirectQuery to Import, or pre-aggregate in the views. |

**Next:** [Lab 7 — Real-time scoring (optional) →](lab-7-realtime-scoring.md)
