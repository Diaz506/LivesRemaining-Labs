# Lab 6: Power BI Dashboards & Fabric Integration

### 🎯 Why This Lab?

Data insights live in Delta tables, but business users need **visualizations**. Power BI / Fabric connects to Databricks SQL:
- Interactive dashboards
- Drill-downs by region, platform, cohort
- Real-time metrics (DAU, churn rate, ARPU)
- Scheduled refresh (data updates 3x daily)

### 📚 Concepts

**Databricks SQL Warehouse:**
- Serverless SQL query engine (point-and-click queries)
- Optimized for analytics (vs. DLT which is optimized for ingestion)
- Enables Power BI DirectQuery (live connection)
- Pricing: Per-second when running (cheaper than all-purpose clusters)

**Power BI DirectQuery vs. Import:**
- **Import**: Copy data into Power BI (faster, but stale)
- **DirectQuery**: Query Databricks live (slower, but real-time)
- We use DirectQuery for this lab

**Dashboard Pages:**
- **Retention**: DAU trends, retention curve, churn risk segments
- **Revenue**: ARPU by cohort (whale, regular, casual, lapsed)
- **Matchmaking**: Queue wait time, win rate by tier, skill distribution
- **Engagement**: Session duration, platform/region breakdown

**Refresh Policy:**
- Databricks jobs run 2 AM UTC
- Power BI refresh 3 AM UTC (after jobs finish)
- Dashboards updated automatically each morning

### 🔧 Goal

Build Power BI dashboard connected to Databricks Gold tables.

### 📋 Deliverables

- `notebooks/powerbi/06_powerbi_dashboard_setup.py` — creates BI-friendly SQL views
- `powerbi/LivesRemaining.pbix` workbook design with 4 pages:
  - Retention & Churn
  - Revenue & ARPU
  - Matchmaking Quality
  - Engagement Metrics
- Refresh policy configured (3 AM UTC daily)

### ☁️ Azure Tasks

1. Create Databricks SQL Warehouse (serverless or provisioned)
2. Get SQL connection string from Databricks UI
3. In Power BI Desktop:
   - "Get Data" → "Azure Databricks"
   - Enter connection string & credentials
   - Select Gold tables
   - Create visuals & publish to Power BI Service
4. Set up scheduled refresh

### 🔑 Key Terms

- **Databricks SQL Warehouse**: Serverless SQL query engine
- **DirectQuery**: Live query to data source (vs. import)
- **DAU (Daily Active Users)**: Unique players logged in per day
- **Cohort**: Group of players (by spend: whale/regular/casual)
- **Retention curve**: % of players active N days after signup

### ⏱️ Time: ~2 hours

### 📖 Reference

- Databricks SQL: [Documentation](https://docs.databricks.com/en/sql/index.html)
- Power BI + Databricks: [Connection guide](https://docs.microsoft.com/en-us/power-bi/connect-data/service-azure-databricks)
- DAX formulas: [Power BI reference](https://dax.guide/)

### Prerequisites: Lab 5

---
