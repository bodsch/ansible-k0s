#!/bin/python

import os
import sys
import requests
# import json


class GitHub:

    def __init__(self):
        """ """
        self.github_access_token = os.environ.get('GH_TOKEN', None)
        self.github_repository = os.environ.get('GH_REPOSITORY', None)
        self.github_username = os.environ.get('GH_USERNAME', None)
        self.github_keep_workflows = os.environ.get('GH_KEEP_WORKFLOWS', 2)

        self.github_base_url = "https://api.github.com"

        if not self.github_access_token:
            print("missing environment variable 'GH_TOKEN'")
            sys.exit(1)

        if not self.github_repository:
            print("missing environment variable 'GH_REPOSITORY'")
            sys.exit(1)

        if not self.github_username:
            print("missing environment variable 'GH_USERNAME'")
            sys.exit(1)

        self.headers = {
            "Authorization": f"token {self.github_access_token}",
        }

    def header(self):
        """ """
        print("")
        print(f"Delete old workflows for the repository {self.github_repository}")
        print(f" {self.github_keep_workflows} log files are kept.")
        print("")

    def get_user_repos(self, username):
        url = f"{self.github_base_url}/users/{self.github_username}/repos"

        query_params = {
            "sort": "updated",
            "per_page": 5
        }

        response = requests.get(url, params=query_params)

        if response.status_code == 200:
            repositories_data = response.json()
            return repositories_data
        else:
            return None

    def create_repo(self, repo_name, repo_descr=None):
        url = f"{self.github_base_url}/user/repos"

        # create json data to send using the post request
        data = {
            "name": repo_name,
            "description": repo_descr,
        }

        response = requests.post(url, headers=self.headers, json=data)

        if response.status_code == 201:
            repo_data = response.json()
            return repo_data
        else:
            return None

    def list_defined_workflows(self):
        url = f"{self.github_base_url}/repos/{self.github_username}/{self.github_repository}/actions/workflows"

        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            repositories_data = response.json()
            return repositories_data
        else:
            return None

    def active_workflows(self, workflows):
        """ """
        return [x for x in workflows.get("workflows", []) if x.get("state", None) in ["active", "disabled_inactivity", "skipped"]]

    def remove_old_workflows(self, workflows):
        """ """
        for wf in workflows:
            wf_id = wf.get("id")
            wf_name = wf.get("name")

            print(f"- Workflow name: '{wf_name}'")

            runned_wf = self.list_workflow(wf_id)

            total_count = runned_wf.get("total_count")

            print(f"  found {total_count} workflows")

            if int(total_count) > int(self.github_keep_workflows):
                workflow_runs = runned_wf.get("workflow_runs")

                runned_wf = self.remove_elements(workflow_runs, int(self.github_keep_workflows))

                msg_wf = ','.join(str(x) for x in runned_wf)

                print("  delete the following workflows:")
                self.remove_workflows(runned_wf)

    def list_workflow(self, wf_id):

        url = f"{self.github_base_url}/repos/{self.github_username}/{self.github_repository}/actions/workflows/{wf_id}/runs"

        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            repositories_data = response.json()
            return repositories_data
        else:
            return None

    def remove_elements(self, workflow, keep_elements):

        runned_wf_ids = [x.get("id") for x in workflow]
        runned_wf_ids = runned_wf_ids[keep_elements:]

        return runned_wf_ids

    def remove_workflows(self, workflow_ids=[]):
        """ """
        result = []
        for wf_id in workflow_ids:
            print(f"  - id {wf_id}")
            url = f"{self.github_base_url}/repos/{self.github_username}/{self.github_repository}/actions/runs/{wf_id}"

            response = requests.delete(url, headers=self.headers)

            # print(f"  = {response}")

        return result


gh = GitHub()
gh.header()
workflows = gh.list_defined_workflows()

if workflows:
    # print(workflows)
    wf = gh.active_workflows(workflows)
    # print(json.dumps(wf, sort_keys=True, indent=2))
    gh.remove_old_workflows(wf)
