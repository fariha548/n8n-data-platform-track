import os
from datetime import timedelta

import requests
from dagster import (
    Definitions,
    DefaultSensorStatus,
    RunFailureSensorContext,
    run_failure_sensor,
)
from dagster_dbt import DbtCliResource
from dagster.preview.freshness import FreshnessPolicy, apply_freshness_policy

from .assets import my_project_dbt_assets
from .gemini_asset import gemini_enriched_records
from .project import my_project_project
from .schedules import schedules

my_project_dbt_assets_with_freshness = my_project_dbt_assets.map_asset_specs(
    lambda spec: apply_freshness_policy(
        spec,
        FreshnessPolicy.cron(
            deadline_cron="0 6 * * *",
            lower_bound_delta=timedelta(hours=2),
        ),
    )
)


@run_failure_sensor(
    monitor_all_code_locations=True,
    default_status=DefaultSensorStatus.RUNNING,
)
def slack_on_dbt_failure(context: RunFailureSensorContext):
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook_url:
        return
    message = (
        f"dbt run failed: job={context.dagster_run.job_name} "
        f"run_id={context.dagster_run.run_id}"
    )
    requests.post(webhook_url, json={"text": message}, timeout=10)


defs = Definitions(
    assets=[my_project_dbt_assets_with_freshness, gemini_enriched_records],
    schedules=schedules,
    sensors=[slack_on_dbt_failure],
    resources={
        "dbt": DbtCliResource(project_dir=my_project_project, profiles_dir="/home/muhammad/.dbt"),
    },
)
