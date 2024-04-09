import urllib.parse

import requests
import openai

from mr.settings import Settings


def get_headers(settings: Settings):
    return {
        "Private-Token": settings.gitlab_private_token
    }


def summarize_diff(settings: Settings, from_tag: str, to_tag: str) -> str | None:
    compare_url = f"{settings.gitlab_url}/api/v4/projects/{settings.gitlab_project_id}/repository/compare"

    params = {
        "from": from_tag,
        "to": to_tag
    }
    changes_response = requests.get(compare_url, headers=get_headers(settings), params=params)
    return summarize_changes(changes_response)


# Fetch the merge request changes
def summarize_mr(settings: Settings, repository_name: str, mr_id: str) -> str | None:
    changes_url = f"{settings.gitlab_url}/api/v4/projects/{urllib.parse.quote_plus(repository_name)}/merge_requests/{mr_id}/changes"
    changes_response = requests.get(changes_url, headers=get_headers(settings))

    return summarize_changes(changes_response)


def summarize_changes(changes_response):
    if changes_response.status_code == 200:
        # Get the diff data
        diff_data = changes_response.json()
        if "changes" not in diff_data:
            diff_text = "\n".join([f"{change['new_path']} ({change['diff']})" for change in diff_data["diffs"]])
        else:
            changes = changes_response.json()["changes"]
            diff_text = "\n".join([f"{change['new_path']} ({change['diff']})" for change in changes])

        # Send the changes to the OpenAI API for summarization
        messages = [
            {"role": "system", "content": "You are a helpful assistant that summarizes code changes."},
            {"role": "user",
             "content": f"Please provide a short and concise summary of the following code changes, in less than 1000 characters:\n\n{diff_text}"}
        ]

        response = openai.chat.completions.create(
            model="gpt-4-0125-preview",
            messages=messages,
            max_tokens=500,
            n=1,
            stop=None,
            temperature=0.2,
        )

        # Print the summary
        summary = response.choices[0].message.content.strip()
        print(f"Changes Summary: {summary}")
        return summary
    else:
        print(f"Error fetching changes: {changes_response.status_code} - {changes_response.text}")
