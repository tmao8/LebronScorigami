import requests
import os

def update_repo_var(value):
    # Defined variables
    repo_owner = "tmao8"
    repo_name = "LebronScorigami"
    variable_name = "LAST_TWEET_DATE"
    new_value = value

    # API URL
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/actions/variables/{variable_name}"

    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    # Headers, including the personal access token
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Payload
    payload = {
        "value": new_value
    }

    # Make the PATCH request
    response = requests.patch(url, json=payload, headers=headers)

    if response.status_code == 204:
        print(f"Successfully updated variable '{variable_name}' to '{new_value}'")
    else:
        print(f"Failed to update variable '{variable_name}'")
        print(response.json())
