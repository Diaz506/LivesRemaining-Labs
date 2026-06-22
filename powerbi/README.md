# Power BI / Fabric Dashboards

**FICTIONAL COMPANY:** Lives Remaining Labs is a fictional game studio for this Databricks reference implementation.

## Overview

Lives Remaining Labs dashboards connect to Gold tables for real-time retention analytics, cohort drills, and server health monitoring.

## Connection Setup

1. **Data Source**: Databricks SQL (DirectQuery or Import)
2. **Connection String**: `<workspace-url>/sql/protocolv1/o/<org-id>/<cluster-id>`
3. **Credentials**: Service principal or user PAT
4. **Setup Notebook**: Run `notebooks/powerbi/06_powerbi_dashboard_setup.py` before connecting.

## Recommended Tables and Views

| Object | Purpose |
|--------|---------|
| `labs.gold.vw_retention_churn` | Churn risk KPIs by date, region, platform, and risk tier |
| `labs.gold.vw_player_segments` | Engagement and revenue cohort summaries |
| `labs.gold.vw_arpu_summary` | Premium tier and monetization metrics |
| `labs.gold.player_churn_scores` | Player-level drillthrough and retention action list |

## Dashboard Pages

### Page 1: Retention & Churn
- DAU trend (7d / 30d rolling)
- Churn risk distribution (Low / Medium / High)
- Retention curve by cohort (New vs. Veteran)
- Churn reason breakdown (seasonality, balance changes, etc.)

### Page 2: Revenue & ARPU
- ARPU by region
- Spend distribution (whales vs. free players)
- Purchase funnel (browsed → purchased)
- LTV by acquisition month

### Page 3: Matchmaking Quality
- Average queue wait time (by region)
- Skill tier distribution
- Win rate by tier
- Complaints/reports trend

### Page 4: Engagement Metrics
- Average session duration
- Daily active players (DAU)
- Session count distribution
- Platform/region breakdown

## Suggested DAX Measures

```DAX
Players = SUM(vw_retention_churn[players])
Avg Churn Probability = AVERAGE(vw_retention_churn[avg_churn_probability])
High Risk Players = CALCULATE([Players], vw_retention_churn[risk_tier] = "high")
High Risk Share = DIVIDE([High Risk Players], [Players])
ARPU 30D = AVERAGE(vw_arpu_summary[avg_spend_30d])
```

## Refresh Policy

- **Gold tables**: Refreshed daily at 2 AM UTC
- **Power BI**: Scheduled refresh 3 AM UTC (after Databricks jobs complete)

## Files

- `LivesRemaining.pbix` — Main dashboard workbook

See individual page documents for drill-down specs.
