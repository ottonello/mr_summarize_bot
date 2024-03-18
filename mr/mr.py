import requests
import openai

from mr.settings import Settings


# Fetch the merge request changes
def summarize_mr(settings:Settings, mr_id: str):
    # Set the headers for the API request
    headers = {
        "Private-Token": settings.gitlab_private_token
    }

    changes_url = f"{settings.gitlab_url}/api/v4/projects/{settings.gitlab_project_id}/merge_requests/{mr_id}/changes"
    changes_response = requests.get(changes_url, headers=headers)

    if changes_response.status_code == 200:
        changes = changes_response.json()["changes"]
        changes_text = "\n".join([f"{change['new_path']} ({change['diff']})" for change in changes])

        # Send the changes to the OpenAI API for summarization
        messages = [
            {"role": "system", "content": "You are a code review assistant."},
            {"role": "user", "content": f"Please provide a small summary of the changes. Be direct and concise and get to the point:\n\n{changes_text}"}
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

    print("-" * 30)