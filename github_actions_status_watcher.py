import json
import time

import requests
import os

REPO_WORKFLOW_URL = "https://api.github.com/repos/adafruit/circuitpython/actions/workflows/build.yml/runs"
POLL_DELAY = 60 * 3  # 3 minutes

CONCLUSION_LIGHT_TIME = 30  # seconds

already_shown_ids = []

headers = {'Accept': "application/vnd.github.v3+json",
           'Authorization': f"token {os.getenv('GITHUB_API_TOKEN')}"}

print("Starting Github Workflow Status Watcher")
print("Press Ctrl-C to Exit")
while True:
    print("fetching workflow run status")
    resp = requests.get(f"{REPO_WORKFLOW_URL}?per_page=1", headers=headers)
    resp_json = resp.json()
    f = open("action_status_result.json", "w")
    f.write(json.dumps(resp_json))
    f.close()

    workflow_run_id = resp_json['workflow_runs'][0]['id']
    if workflow_run_id not in already_shown_ids:

        status = resp_json['workflow_runs'][0]['status']
        conclusion = resp_json['workflow_runs'][0]['conclusion']
        print(f"{status} - {conclusion}")
        if status == "in_progress" or status == "queued":
            print("YELLOW")

        if status == "completed":
            print(f"adding {workflow_run_id} to shown IDs")
            already_shown_ids.append(workflow_run_id)
            if conclusion == "success":
                print("GREEN ON")
                time.sleep(CONCLUSION_LIGHT_TIME)
                print("GREEN OFF")
            else:
                print("RED ON")
                time.sleep(CONCLUSION_LIGHT_TIME)
                print("GREEN OFF")
    else:
        print("already showed this run")
    time.sleep(POLL_DELAY)