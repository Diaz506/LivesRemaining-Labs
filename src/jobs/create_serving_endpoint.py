"""
Lab 7: Create or update a Databricks Model Serving endpoint.

Requires DATABRICKS_HOST and DATABRICKS_TOKEN environment variables. Use a PAT or
service-principal token with permission to manage serving endpoints.
"""

import argparse
import os
import time

import requests


def parse_args():
    parser = argparse.ArgumentParser(description="Create Databricks serving endpoint for churn scoring.")
    parser.add_argument("--endpoint-name", default="lives-remaining-churn")
    parser.add_argument("--model-name", default="lives_remaining_churn_model")
    parser.add_argument("--model-version", required=True)
    parser.add_argument("--workload-size", default="Small", choices=["Small", "Medium", "Large"])
    parser.add_argument("--scale-to-zero", action="store_true")
    return parser.parse_args()


def databricks_request(method, path, payload=None):
    host = os.environ["DATABRICKS_HOST"].rstrip("/")
    token = os.environ["DATABRICKS_TOKEN"]
    response = requests.request(
        method=method,
        url=f"{host}{path}",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=payload,
        timeout=60,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"Databricks API error {response.status_code}: {response.text}")
    return response.json() if response.text else {}


def main():
    args = parse_args()
    config = {
        "served_entities": [
            {
                "entity_name": args.model_name,
                "entity_version": args.model_version,
                "workload_size": args.workload_size,
                "scale_to_zero_enabled": args.scale_to_zero,
            }
        ]
    }

    existing = databricks_request("GET", "/api/2.0/serving-endpoints")
    names = {endpoint["name"] for endpoint in existing.get("endpoints", [])}

    if args.endpoint_name in names:
        databricks_request("PUT", f"/api/2.0/serving-endpoints/{args.endpoint_name}/config", config)
        print(f"Updated endpoint {args.endpoint_name}")
    else:
        databricks_request("POST", "/api/2.0/serving-endpoints", {"name": args.endpoint_name, "config": config})
        print(f"Created endpoint {args.endpoint_name}")

    for _ in range(30):
        endpoint = databricks_request("GET", f"/api/2.0/serving-endpoints/{args.endpoint_name}")
        state = endpoint.get("state", {}).get("ready", "UNKNOWN")
        print(f"Endpoint state: {state}")
        if state == "READY":
            return
        time.sleep(20)

    raise TimeoutError(f"Endpoint {args.endpoint_name} did not become READY in time.")


if __name__ == "__main__":
    main()
