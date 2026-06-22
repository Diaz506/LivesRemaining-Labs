# Lives Remaining Labs — Azure Databricks E2E Data Lab

**⚠️ FICTIONAL COMPANY: Lives Remaining Labs is a fictional game studio created for this reference implementation.**

---

**Multiplayer game studio analysis on Azure Databricks: player events, churn prediction, matchmaking quality & retention optimization.**

## Overview

Lives Remaining Labs is a reference end-to-end **Azure Databricks** project demonstrating:
- **Real-time event ingestion** via Delta Live Tables (DLT) from Azure Event Hubs / Blob Storage
- **Feature engineering** for churn and ARPU modeling
- **ML lifecycle** with MLflow (experiment tracking, model registry, serving)
- **Governance** via Unity Catalog
- **Analytics** dashboards in Power BI / Fabric on Azure
- **Infrastructure** provisioned via Terraform (Azure provider)

**KPIs:** Churn rate, ARPU, retention lift, matchmaking quality score, player session length.

## Repo Structure

```
LivesRemaining-Labs/
├── terraform/              # Databricks workspace, Unity Catalog, jobs
├── src/
│   ├── dlt/               # DLT pipeline code (Bronze → Silver → Gold)
│   └── jobs/              # Training & inference job scripts
├── notebooks/             # Runnable lab examples
│   ├── dlt/               # DLT Bronze/Silver/Gold labs
│   ├── jobs/              # MLflow, scoring, serving labs
│   └── powerbi/           # Power BI/Fabric setup notebook
├── docs/                  # Architecture, lab guides, runbooks
├── data/                  # Sample datasets & synthetic event generators
└── powerbi/              # Dashboard & Fabric integration notes
```

## Prerequisites

- **Azure subscription** with resource group
- **Azure Databricks workspace** (Premium tier recommended for Unity Catalog)
- **Azure Storage Account** (ADLS Gen2) for data lake
- **Terraform** >= 1.0 with Azure provider
- **Python** 3.9+ (for local script testing)
- **PowerShell** or **Azure CLI** for resource provisioning

👉 **[See setup guide →](docs/setup-azure.md)** (coming soon)

## Quick Start

1. **Review** `docs/architecture.md` for design decisions
2. **Complete labs** in order (see `docs/labs.md`)
3. **Provision infra** via Terraform
4. **Run DLT pipelines** to ingest and transform events
5. **Train churn model** and set up scoring jobs
6. **Build dashboards** in Power BI

## Labs (7 total, ~10–11 hours)

| Lab | Duration | Focus | Link |
|-----|----------|-------|------|
| **Lab 0** | 30 min | Generate synthetic events | [Start](docs/labs.md#lab-0-setup--sample-data-generation) |
| **Lab 1** | 1 hr | Bronze ingestion (DLT Autoloader) | [Start](docs/labs.md#lab-1-bronze-ingestion-via-dlt-autoloader) |
| **Lab 2** | 1.5 hr | Silver transformations & quality checks | [Start](docs/labs.md#lab-2-silver-transformations--quality-checks) |
| **Lab 3** | 1.5 hr | Feature engineering for ML (Gold) | [Start](docs/labs.md#lab-3-feature-engineering-for-ml) |
| **Lab 4** | 2 hr | Churn prediction with MLflow | [Start](docs/labs.md#lab-4-churn-prediction-with-mlflow) |
| **Lab 5** | 1 hr | Batch scoring & predictions | [Start](docs/labs.md#lab-5-batch-scoring--predictions) |
| **Lab 6** | 2 hr | Power BI dashboards | [Start](docs/labs.md#lab-6-power-bi-dashboards--fabric-integration) |
| **Lab 7** (optional) | 1.5 hr | Real-time scoring endpoint | [Start](docs/labs.md#lab-7-real-time-scoring-endpoint-optional) |

👉 **[View full lab sequence →](docs/labs.md)**

## Documentation

- **[Azure Databricks Setup Guide](docs/setup-azure.md)** — Prerequisites & workspace provisioning
- **[Architecture Overview](docs/architecture.md)** — System design, Azure services, data flow
- **[Data Schema](docs/data-schema.md)** — Bronze/Silver/Gold table schemas
- **[Lab Sequence](docs/labs.md)** — Step-by-step instructions for all 7 labs

## Next Steps

- [ ] Run Lab 0 locally to generate or refresh sample events
- [ ] Upload sample events to ADLS Gen2
- [ ] Run the DLT notebooks/pipelines in order: Bronze → Silver → Gold
- [ ] Train and register the churn model with MLflow
- [ ] Publish batch scores and connect Power BI to the Gold views

## License

MIT
