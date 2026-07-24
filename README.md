# Module 0 — Environment & Foundations
**n8n Data Platform Engineer — Skills Track**

![n8n](https://img.shields.io/badge/n8n-EA4B71?style=for-the-badge&logo=n8n&logoColor=white)
![BigQuery](https://img.shields.io/badge/BigQuery-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white)
![dbt](https://img.shields.io/badge/dbt-FF694B?style=for-the-badge&logo=dbt&logoColor=white)
![Dagster](https://img.shields.io/badge/Dagster-6E43E8?style=for-the-badge&logo=dagster&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Status](https://img.shields.io/badge/Status-In%20Progress-yellow?style=for-the-badge)

Local-first setup connecting a self-hosted automation tool to a cloud data warehouse, an ELT transformation layer, and an orchestration layer — the four systems this track builds on.

---

## Architecture

```mermaid
flowchart LR
    subgraph Local["🖥️ Local VM — Ubuntu"]
        N8N["🔗 n8n<br/>workflow automation<br/>:5678"]
        DBT["🏗️ dbt-core<br/>transformation layer"]
        DAG["🎛️ Dagster<br/>orchestration<br/>:3000"]
    end

    subgraph Cloud["☁️ Google Cloud"]
        BQ["🗄️ BigQuery<br/>n8n-self-practice<br/>sandbox tier"]
    end

    N8N -.future integration.-> BQ
    DBT -->|oauth auth| BQ
    DAG -->|will orchestrate| DBT

    style N8N fill:#EA4B71,stroke:#333,color:#fff
    style DBT fill:#FF694B,stroke:#333,color:#fff
    style DAG fill:#6E43E8,stroke:#333,color:#fff
    style BQ fill:#4285F4,stroke:#333,color:#fff
    style Local fill:#F8F9FA,stroke:#333,stroke-width:2px
    style Cloud fill:#E8F0FE,stroke:#1a73e8,stroke-width:2px
```

---

## What's Working

| Component | Status | Verified By |
|---|---|---|
| 🔗 n8n | ✅ Running | Local Docker, `localhost:5678` reachable |
| ☁️ BigQuery auth | ✅ Connected | `gcloud auth application-default login` |
| 🏗️ dbt → BigQuery | ✅ Connected | `dbt debug` → All checks passed |
| 🎛️ Dagster | ✅ Running | `localhost:3000` webserver live |

---

## Setup Flow

```mermaid
sequenceDiagram
    participant Dev as 👩‍💻 Developer
    participant GCP as ☁️ Google Cloud
    participant dbt as 🏗️ dbt-core
    participant Dag as 🎛️ Dagster

    Dev->>GCP: gcloud init (select project)
    Dev->>GCP: gcloud auth application-default login
    Dev->>dbt: dbt init my_project (oauth method)
    dbt->>GCP: dbt debug (verify connection)
    GCP-->>dbt: ✅ All checks passed
    Dev->>Dag: dagster project scaffold
    Dev->>Dag: dagster dev
```

1. `gcloud init` — authenticate CLI, select GCP project (`n8n-self-practice`)
2. `gcloud auth application-default login` — application-level credentials for dbt
3. Python venv created outside the dbt project folder (`~/n8n-practice/venv`)
4. `dbt init my_project` — oauth authentication method, no service account key needed (sandbox tier constraint)
5. `dbt debug` — confirms warehouse connection
6. `dagster project scaffold` + `dagster dev` — orchestration layer running, not yet wired to any real asset

---

## 🔍 Self-Check: Tested vs Assumed

**✅ Tested:**
- [x] dbt connects to BigQuery and passes all debug checks
- [x] n8n workflow persists after container restart (Docker volume mount confirmed)
- [x] Dagster webserver serves UI on `localhost:3000`
- [x] Service account/OAuth scope limited to sandbox project — no billing account attached

**⚠️ Assumed (not yet tested):**
- [ ] Behavior once real data volume exceeds sandbox free-tier limits
- [ ] Dagster-to-dbt integration (`dagster-dbt`) — install confirmed, integration not yet wired
- [ ] n8n-to-BigQuery direct integration — not yet attempted

---

## ➡️ Next Module
**Module 1 — Advanced SQL for Analytics Engineering** — window functions, CTEs, and incremental-query patterns against a public BigQuery dataset.
