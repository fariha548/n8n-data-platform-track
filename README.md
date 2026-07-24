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

---

# Module 1 — Advanced SQL for Analytics Engineering

![SQL](https://img.shields.io/badge/SQL-Advanced-4285F4?style=for-the-badge&logo=googlebigquery&logoColor=white)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen?style=for-the-badge)

Practiced against `bigquery-public-data.thelook_ecommerce.orders` — a public e-commerce dataset. Full queries in `sql/module1_advanced_sql.sql`.

## Concepts Covered

```mermaid
mindmap
  root((Advanced SQL))
    Window Functions
      COUNT OVER PARTITION
      Per-user sequencing
    Running Totals
      SUM OVER
      ROWS BETWEEN
    Deduplication
      ROW_NUMBER
      QUALIFY filter
    Aggregation
      Monthly cohorts
      GROUP BY and EXTRACT
```

## Query Summary

| # | Concept | What It Solves |
|---|---|---|
| 1 | Basic exploration | Understand raw table shape and columns |
| 2 | Window function COUNT OVER | Number each user's orders in sequence |
| 3 | Running total SUM OVER | Cumulative items ordered per user, over time |
| 4 | Dedup ROW_NUMBER plus QUALIFY | Isolate latest order per user, reused in dbt staging models |
| 5 | Monthly aggregation | Cohort-style breakdown by year, month, status |

## Self-Check: Tested vs Assumed

Tested:
- [x] All 5 queries return correct, verified results against the public dataset
- [x] QUALIFY correctly filters window function output, not possible with plain WHERE
- [x] Running total values manually spot-checked against raw num_of_item values

Assumed, not yet tested:
- [ ] Query performance and cost at production-scale row counts, millions plus rows
- [ ] Behavior with NULL values in partition or order columns, not encountered in this sample

## Next Module
**Module 2 — dbt Fundamentals on BigQuery** — staging and marts models, first working ELT pipeline.



---

# Module 2 — dbt Fundamentals on BigQuery

![dbt](https://img.shields.io/badge/dbt-Fundamentals-FF694B?style=for-the-badge&logo=dbt&logoColor=white)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen?style=for-the-badge)

First working ELT pipeline: raw BigQuery public data transformed through staging into a business-ready mart table.

## Pipeline Lineage


## Models Built

| Layer | Model | Purpose |
|---|---|---|
| Staging | stg_orders | Cleaned order records from raw source |
| Staging | stg_users | Cleaned user records from raw source |
| Staging | stg_order_items | Cleaned order line items from raw source |
| Mart | fct_orders | Joined, business-ready order fact table with total value |

## Self-Check: Tested vs Assumed

Tested:
- [x] All 3 staging models build successfully as views
- [x] fct_orders correctly joins staging models via ref, dbt-managed dependency graph
- [x] 13 of 13 data tests pass, unique and not_null on key columns
- [x] Lineage graph confirms correct dependency order

Assumed, not yet tested:
- [ ] Incremental materialization, all models are full-refresh views so far
- [ ] Behavior on schema drift if source table columns change

## Next Module
**Module 3 — Data Modeling: Dimensional Design** — star schema and SCD Type 2 snapshots.
