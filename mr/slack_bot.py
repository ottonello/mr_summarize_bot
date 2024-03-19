import os
import re
import threading
from typing import Any

from slack_bolt import App

from mr.mr import summarize_mr
from mr.mr import summarize_diff
from mr.settings import Settings

# Define the pattern you want to match to extract the MR id
mr_pattern = r"merge_requests/(\d+)"

# More specific pattern for comparing tags
# diff_pattern = r'compare/v(\d{6}-\d{4}\.\d+)\.\.\.v(\d{6}-\d{4}\.\d+)'
# More generic version
diff_pattern = r'compare/([a-zA-Z0-9\.-]+)\.\.\.([a-zA-Z0-9\.-]+)'


class Task:
    def __init__(self, body: str, say: Any,
                 settings: Settings,
                 merge_request_id: str | None = None, from_tag: str | None = None, to_tag: str | None = None):
        self.merge_request_id = merge_request_id
        self.from_tag = from_tag
        self.to_tag = to_tag
        self.body = body
        self.say = say
        self.settings = settings

    def call(self):
        summary = None
        if self.merge_request_id:
            print(f"The merge request ID is: {self.merge_request_id}, gonna summarize now...")

            summary = summarize_mr(self.settings, self.merge_request_id)
        elif self.from_tag and self.to_tag:
            print(f"Comparing tags {self.from_tag} and {self.to_tag}, gonna summarize now...")

            summary = summarize_diff(self.settings, self.from_tag, self.to_tag)

        if summary:
            print(f"Summarizing done, sending reply now...")
            self.say({"text": summary, "thread_ts": self.body["event"]["ts"]})
        else:
            print("No summary found or nothing to do with this message.")


def start_bot(settings: Settings):
    # Initialize the Slack app with your bot token
    app = App(
        token=settings.slack_token,
        signing_secret=settings.slack_signing_secret
    )

    @app.event("message")
    def handle_message(body, say, logger):
        message = body["event"]["text"]

        task = None

        if match := re.search(mr_pattern, message):
            merge_request_id = match.group(1)

            task = Task(body, say, settings, merge_request_id=merge_request_id)
        elif match := re.search(diff_pattern, message):
            from_tag, to_tag = match.groups()

            task = Task(body, say, settings, from_tag=from_tag, to_tag=to_tag)

        if task:
            thread = threading.Thread(target=task.call)
            thread.start()

    app.start(port=int(os.environ.get("PORT", settings.port)))
