# Lab 7: Real-Time Scoring Endpoint (Optional)

### 🎯 Why This Lab?

Batch scoring (Lab 5) runs daily. But what if we need **live risk scores** for:
- Showing churn risk in-game UI
- Triggering retention offers in real-time
- A/B testing different interventions

**Databricks Model Serving** deploys model as REST API.

### 📚 Concepts

**Batch vs. Real-Time:**
- **Batch**: Process all players nightly (Lab 5)
- **Real-time**: Score individual players on-demand (this lab)
- Real-time: Higher latency SLA (<100ms), higher cost
- Batch: Cheaper, but stale predictions

**Model Serving Endpoint:**
- REST API that returns predictions
- Auto-scales based on load
- Integrates with feature store (optional)

**Authentication (Azure):**
- Clients authenticate via Azure Entra
- Service principal with Databricks workspace permissions
- Token-based (Bearer token in HTTP header)

**Latency SLA:**
- P50 (median): ~20–50ms
- P95: ~100–200ms
- Goal: <100ms for game UI

### 🔧 Goal

Deploy MLflow model as REST endpoint for real-time scoring.

### 📋 Deliverables

- Model endpoint deployed via Databricks Model Serving
- `src/jobs/create_serving_endpoint.py` — endpoint deployment helper
- `notebooks/jobs/07_realtime_scoring_endpoint.py` — endpoint walkthrough and test client
- Latency benchmarks (P50, P95, P99)
- Documentation for integration

### ☁️ Azure Tasks

- Deploy model to Databricks Model Serving
- Configure authentication (service principal)
- Test from local client
- Monitor via Databricks UI

### 🔑 Key Terms

- **Inference endpoint**: REST API for predictions
- **Latency SLA**: Response time guarantee (P50, P95, P99)
- **Bearer token**: OAuth token in HTTP header
- **Scaling**: Auto-add replicas under high load
- **A/B testing**: Show intervention to subset, measure impact

### ⏱️ Time: ~1.5 hours

### 📖 Reference

- Databricks Model Serving: [Documentation](https://docs.databricks.com/en/machine-learning/model-serving/index.html)
- REST API design: [Best practices](https://restfulapi.net/)
- Azure Entra auth: [OAuth 2.0](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow)

### Prerequisites: Lab 4

---
