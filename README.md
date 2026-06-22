# Lives Remaining Labs — Databricks E2E Data Lab

**⚠️ FICTIONAL COMPANY: Lives Remaining Labs is a fictional game studio created for this reference implementation.**

---

**Multiplayer game studio analysis: player events, churn prediction, matchmaking quality & retention optimization.**

## Overview

Lives Remaining Labs is a reference end-to-end Databricks project demonstrating:
- **Real-time event ingestion** via Delta Live Tables (DLT)
- **Feature engineering** for churn and ARPU modeling
- **ML lifecycle** with MLflow (experiment tracking, model registry, serving)
- **Governance** via Unity Catalog
- **Analytics** dashboards in Power BI / Fabric

**KPIs:** Churn rate, ARPU, retention lift, matchmaking quality score, player session length.

## Repo Structure

```
LivesRemaining-Labs/
├── terraform/              # Databricks workspace, Unity Catalog, jobs
├── src/
│   ├── dlt/               # DLT pipeline code (Bronze → Silver → Gold)
│   └── jobs/              # Training & inference job scripts
├── notebooks/             # Runnable lab examples
│   ├── dlt/              # DLT labs
│   └── jobs/             # MLflow & training labs
├── docs/                  # Architecture, lab guides, runbooks
├── data/                  # Sample datasets & synthetic event generators
└── powerbi/              # Dashboard & Fabric integration notes
```

## Quick Start

1. **Review** `docs/architecture.md` for design decisions
2. **Complete labs** in order (see `docs/labs.md`)
3. **Provision infra** via Terraform
4. **Run DLT pipelines** to ingest and transform events
5. **Train churn model** and set up scoring jobs
6. **Build dashboards** in Power BI

## Next Steps

- [ ] Review `docs/labs.md` for lab sequence
- [ ] Review data schemas in `docs/data-schema.md`
- [ ] Generate synthetic events in `data/`
- [ ] Configure Terraform variables for your Databricks workspace
- [ ] Deploy and run Lab 1 (Bronze ingestion)

## License

MIT
