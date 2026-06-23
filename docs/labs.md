# Lives Remaining Labs — Lab Sequence

**FICTIONAL COMPANY:** Lives Remaining Labs is a fictional multiplayer game studio created for educational purposes.

**Platform:** Azure Databricks (Premium workspace with Unity Catalog)

Start with the prerequisites, then complete the labs in order. Each lab now has its own guide plus a matching runnable notebook or script where applicable.

## Lab Guides

| Lab | Duration | Concept | Guide | Primary runnable artifact |
|-----|----------|---------|-------|---------------------------|
| Prerequisites | - | Azure and Databricks setup | [Open](labs/prerequisites.md) | Terraform / workspace setup |
| Setup | 15 min | Workspace + Unity Catalog (UI default, Terraform optional) | [Open](labs/prerequisites.md) | `notebooks/setup/00_unity_catalog_setup.py` (or `terraform/`) |
| Lab 0 | 30 min | Data generation | [Open](labs/lab-0-setup-data-generation.md) | `scripts/generate_events.py` |
| Lab 1 | 1 hr | DLT Autoloader Bronze ingestion | [Open](labs/lab-1-bronze-ingestion.md) | `notebooks/dlt/01_ingest_bronze.py` |
| Lab 2 | 1.5 hr | Silver transformations and quality checks | [Open](labs/lab-2-silver-transformations.md) | `notebooks/dlt/02_silver_transformations.py` |
| Lab 3 | 1.5 hr | Gold feature engineering | [Open](labs/lab-3-feature-engineering.md) | `notebooks/dlt/03_feature_engineering_gold.py` |
| Lab 4 | 2 hr | Churn prediction with MLflow | [Open](labs/lab-4-churn-prediction.md) | `notebooks/jobs/04_train_churn_model.py` |
| Lab 5 | 1 hr | Batch scoring and predictions | [Open](labs/lab-5-batch-scoring.md) | `notebooks/jobs/05_batch_scoring.py` |
| Lab 6 | 2 hr | Power BI dashboards and Fabric integration | [Open](labs/lab-6-powerbi-dashboards.md) | `notebooks/powerbi/06_powerbi_dashboard_setup.py` |
| Lab 7 | 1.5 hr | Optional real-time scoring endpoint | [Open](labs/lab-7-realtime-scoring.md) | `notebooks/jobs/07_realtime_scoring_endpoint.py` |

## Summary: 7 Labs, ~10-11 hours

| Lab | Duration | Concept | Outcome |
|-----|----------|---------|---------|
| 0 | 30 min | Data generation | 100k events in ADLS |
| 1 | 1 hr | DLT Autoloader | Bronze table with raw events |
| 2 | 1.5 hr | Silver transforms | Clean Silver event/session tables |
| 3 | 1.5 hr | Feature engineering | Gold feature tables |
| 4 | 2 hr | MLflow churn model | Trained and registered model |
| 5 | 1 hr | Batch scoring | Daily predictions table |
| 6 | 2 hr | Power BI dashboards | Interactive analytics UI |
| 7 | 1.5 hr | Real-time endpoint | Live prediction API |

## Learning Path

**Beginner focus:** Labs 0-2 explain the data flow from events to raw and clean tables. Labs 3-4 introduce feature engineering and model training. Lab 6 shows the business-facing analytics outcome.

**Intermediate focus:** Labs 5-7 cover deployment and production scoring patterns.

**Azure focus:** Each lab shows how Azure services integrate across ADLS Gen2, Azure Databricks, Entra identity, Databricks SQL, and Power BI/Fabric.

## Troubleshooting

See the individual lab guides and notebooks for lab-specific errors and fixes. If stuck, check Databricks workspace logs under **Jobs UI > Run history > Logs** or the Delta Live Tables event log.
