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

![Lineage Graph](assets/module2_lineage.png)


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

---

# Module 3 — Data Modeling: Dimensional Design

![dbt](https://img.shields.io/badge/dbt-Snapshots-FF694B?style=for-the-badge&logo=dbt&logoColor=white)
![BigQuery](https://img.shields.io/badge/BigQuery-Star%20Schema-4285F4?style=for-the-badge&logo=googlebigquery&logoColor=white)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen?style=for-the-badge)

Star schema built on top of Module 2's staging layer, with SCD Type 2 change tracking via dbt snapshots.

## Star Schema

```mermaid
erDiagram
    fct_orders }o--|| dim_users : user_key
    fct_orders }o--|| dim_date : order_date_key
    fct_order_items }o--|| dim_users : user_key
    fct_order_items }o--|| dim_products : product_key
    fct_order_items }o--|| dim_date : order_date_key
    fct_order_items }o--|| fct_orders : order_id

    dim_users {
        string user_key PK
        string user_id
        string city
        boolean is_current
    }
    dim_products {
        string product_key PK
        string product_id
        string category
    }
    dim_date {
        date date_key PK
    }
    fct_orders {
        string order_id PK
        string user_key FK
        date order_date_key FK
    }
    fct_order_items {
        string order_item_id PK
        string user_key FK
        string product_key FK
        date order_date_key FK
    }
```

## Models Built

| Layer | Model | Purpose |
|---|---|---|
| Snapshot | users_snapshot | SCD Type 2 change tracking on users (check strategy) |
| Dimension | dim_users | Surrogate key, current + historical user attributes |
| Dimension | dim_products | Surrogate key, static product attributes |
| Dimension | dim_date | Calendar spine, 2019–2026 |
| Fact | fct_orders | Order grain — 1 row per order |
| Fact | fct_order_items | Line-item grain — 1 row per order item, carries product_key |

## Design Decisions

- **fct_orders vs fct_order_items split**: an order can contain multiple products, so `product_key` cannot live on the order-grain fact without breaking grain. Product-level analysis goes through `fct_order_items` instead.
- **SCD2 fan-out guard**: joins from fact tables to `dim_users` filter on `is_current = true` to prevent duplicate rows if a user's tracked attributes ever change.
- **check strategy over timestamp**: source table has no `updated_at` column, so snapshot uses `check_cols` on the fields most likely to change (address, traffic_source) rather than a blanket column check.

## Self-Check: Tested vs Assumed

Tested:
- [x] Snapshot correctly captures dbt_valid_from/dbt_valid_to on first run
- [x] Found and fixed a source data-quality issue — city column held the literal string "null" for ~5% of Brazil rows, silently bypassing IS NULL checks
- [x] All fact-to-dimension joins verified for null foreign keys (0 nulls on user_key, product_key, date_key)
- [x] 19 of 19 data tests pass across staging, dimensions, and facts

Assumed, not yet tested:
- [ ] SCD2 behavior on an actual attribute change — source data is static, so a second snapshot run producing a new row version hasn't been observed yet
- [ ] dim_date coverage beyond 2026 if the source data range extends further

## Next Module
**Module 4 — Orchestration with Dagster**

[![Dagster](https://img.shields.io/badge/Dagster-6E43E8?style=for-the-badge&logo=dagster&logoColor=white)](https://camo.githubusercontent.com/) [![Slack](https://img.shields.io/badge/Slack-4A154B?style=for-the-badge&logo=slack&logoColor=white)](https://camo.githubusercontent.com/) [![Status](https://img.shields.io/badge/Status-Complete-brightgreen?style=for-the-badge)](https://camo.githubusercontent.com/)

The Module 2/3 dbt project wrapped in a Dagster orchestration layer: scheduled runs, freshness observability, and real Slack alerting on failure.

## Architecture

```mermaid
flowchart LR
    subgraph dbt["🏗️ dbt Project"]
        M["9 models<br/>28 tests"]
    end

    subgraph Dagster["🎛️ Dagster Orchestration"]
        A["📦 dbt Assets<br/>dagster-dbt wrap"]
        S["⏰ Schedule<br/>daily 06:00 UTC"]
        F["📈 FreshnessPolicy<br/>26h tolerance"]
        RS["🚨 run_failure_sensor"]
    end

    subgraph Alert["🔔 Alerting"]
        SL["💬 Slack #new-channel"]
    end

    M -->|wrapped as| A
    S -->|triggers| A
    A -->|tracked by| F
    A -->|on FAILURE| RS
    RS -->|POST webhook| SL

    style dbt fill:#FF694B,stroke:#333,color:#fff
    style Dagster fill:#F3F0FF,stroke:#6E43E8,stroke-width:2px
    style Alert fill:#ECE4F7,stroke:#4A154B,stroke-width:2px
    style A fill:#6E43E8,stroke:#333,color:#fff
    style S fill:#8B6EF0,stroke:#333,color:#fff
    style F fill:#8B6EF0,stroke:#333,color:#fff
    style RS fill:#E8433E,stroke:#333,color:#fff
    style SL fill:#4A154B,stroke:#333,color:#fff
```

## Induced-Failure Self-Check

```mermaid
sequenceDiagram
    participant Dev as 👩‍💻 Developer
    participant Model as 🏗️ stg_orders.sql
    participant Dag as 🎛️ Dagster
    participant BQ as ☁️ BigQuery
    participant Slack as 💬 Slack

    Dev->>Model: typo order_id → order_idd
    Dev->>Dag: Materialize all 9 assets
    Dag->>BQ: run stg_orders
    BQ-->>Dag: ❌ column not found
    Dag-->>Dag: fct_orders, fct_order_items fail (propagation)
    Dag->>Slack: 🚨 run_failure_sensor fires
    Slack-->>Dev: "dbt run failed: run_id=8aab9e24"
    Dev->>Model: revert typo
    Dev->>Dag: Materialize again
    Dag->>BQ: run all 9 models
    BQ-->>Dag: ✅ all pass
```

## What's Working

| Component | Status | Verified By |
|---|---|---|
| 🎛️ dagster-dbt integration | ✅ Working | All 9 assets materialize via Dagster, not raw dbt |
| ⏰ Daily schedule | ✅ Enabled | Toggled ON in UI, `materialize_dbt_models_schedule` |
| 📈 Freshness observability | ✅ Working | Asset detail page shows "Passing" state |
| 🚨 Slack alert on failure | ✅ Working | Real message received: run_id `8aab9e24` |
| 🔁 Failure → fix → pass cycle | ✅ Verified | Run `8aab9e24` (fail) → Run `94bd25d5` (pass) |

## 🔍 Self-Check: Tested vs Assumed

**✅ Tested:**

- [x] dbt project wrapped as native Dagster assets via `dagster-dbt`, all 9 models visible and materializable in UI
- [x] Daily schedule defined and enabled (cron `0 6 * * *`)
- [x] Freshness tracked via `FreshnessPolicy` (new API) — confirmed "Passing" state on a live asset after materialization
- [x] Induced failure (typo'd column) correctly failed `stg_orders` and cascaded to `fct_orders`/`fct_order_items`, while unrelated assets stayed green
- [x] `run_failure_sensor` fired a real Slack webhook message on failure, confirmed in-channel
- [x] Revert-and-repass confirmed with a second clean run (paired run IDs as evidence)
- [x] Concurrent-run behavior tested (not assumed) — two back-to-back materialize triggers exposed a real race condition: `DbtProject.prepare_if_dev()` running twice simultaneously briefly left `dbt_packages/` in an inconsistent state, failing one run with "0 package(s) installed." This happened despite `dagster_dbt`'s own `run_with_concurrent_update_guard` — a genuine limitation, not a VM issue

**⚠️ Assumed (not yet tested):**

- [ ] Backfill behavior across multiple missed schedule windows — not triggered in this project
- [ ] Fix for the concurrent-run race condition above — documented as a known limitation, not patched (out of scope for this module)

## Notes on the Build

- `dagster-dbt`'s factory functions (`build_last_update_freshness_checks`, `build_sensor_for_freshness_checks`) turned out to be superseded by a newer `FreshnessPolicy`/`apply_freshness_policy` API in this Dagster version (1.13.15) — migrated to the new pattern after hitting a `SupersessionWarning`.
- Both the dbt CLI resource and the project's dbt-project object needed an explicit profiles directory configured — the dbt profile lives outside the project folder in this setup.
- Two local `dagster dev` crashes during testing were traced to local machine memory pressure (swap near capacity, limited available RAM) rather than an application defect — resolved by restarting; a permanent fix (increasing available memory) is still pending.

## Next Module

**Module 5** — TBD
