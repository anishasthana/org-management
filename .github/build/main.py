import yaml
import os
import requests
import git

def main():
    with open("./config/opendatahub-io/org.yaml", "r") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        new_odh_org = data.get("orgs").get("opendatahub-io")
    # os.system("git  --no-pager log -n 5")
    os.system("git fetch --all")
    os.system("git checkout main")
    # os.system("git --no-pager log -n 5")

    with open("./config/opendatahub-io/org.yaml", "r") as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
        old_odh_org = data.get("orgs").get("opendatahub-io")

    pr_number = os.environ.get("PR_NUMBER")
    affected_teams = get_affected_teams(old_odh_org, new_odh_org)
    approver_teams = get_valid_approvers(old_odh_org, affected_teams)
    pr_approvers = get_pr_approvers(pr_number, os.environ.get("TOKEN"))
    for team in approver_teams:
        if team.intersection(pr_approvers):
            print(f"Valid reviewer found for {team} in PR approvers: {pr_approvers}")
        else:
            print(f"No valid reviewers found for {team} in PR approvers: {pr_approvers}")
            exit(1)


def get_affected_teams(old_org, new_org):
    affected_teams = []
    if old_org==new_org:
        print("No changes detected to org yaml")
        exit(0)
    old_org_teams = old_org.get("teams")
    new_org_teams = new_org.get("teams")
    for team in old_org_teams:
        if old_org_teams.get(team) != new_org_teams.get(team):
            print(f"{team} has been changed")
            affected_teams.append(team)
    return affected_teams


def get_valid_approvers(org: dict, teams: list):
    approvers = []
    for team in teams:
        approvers.append(set(org.get("teams").get(team).get("maintainers")))
    return approvers


def get_pr_approvers(id: int, token: str):
    response = requests.get(
        "https://api.github.com/repos/" + os.environ.get("REPO") + "/pulls/" + id + "/reviews",
        headers={
        "Authorization": "Bearer " + token
        }
    )

    # Check the response status code
    if response.status_code == 200:
        # Get the list of review comments from the response
        reviews = response.json()

        # Create a list of users who have approved the PR
        approved_users = set()
        for review in reviews:
            if review['state'] == "CHANGES_REQUESTED":
                exit(1)
            if review['state'] == "APPROVED":
                approved_users.add(review['user']['login'])

        # Print the list of approved users
        return approved_users
    else:
        # Print the response status code
        print(response.status_code)

if __name__ == "__main__":
    main()
