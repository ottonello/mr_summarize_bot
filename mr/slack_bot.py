import os
import re
import threading
from typing import Any

from slack_bolt import App

from mr.mr import summarize_mr
from mr.mr import summarize_diff
from mr.settings import Settings

# Define the pattern you want to match to extract the repo and MR id
mr_pattern = r"([^/]*/[^/]*)/-/merge_requests/(\d+)"
diff_pattern = r'compare/([a-zA-Z0-9\.-]+)\.\.\.([a-zA-Z0-9\.-]+)'


class SummarizingTask:
    def __init__(self, body: str, say: Any,
                 settings: Settings,
                 repository_name: str | None = None,
                 merge_request_id: str | None = None, from_tag: str | None = None, to_tag: str | None = None):
        self.merge_request_id = merge_request_id
        self.from_tag = from_tag
        self.to_tag = to_tag
        self.body = body
        self.say = say
        self.settings = settings
        self.repository_name = repository_name

    def call(self):
        summary = None
        if self.merge_request_id:
            print(f"The merge request ID is: {self.merge_request_id}, gonna summarize now...")

            summary = summarize_mr(self.settings, self.repository_name, self.merge_request_id)
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
        message = get_message(body)
        if not message:
            message = get_attachment_text(body)

        task = None

        if match := re.search(mr_pattern, message):
            repository_name = match.group(1)
            merge_request_id = match.group(2)

            task = SummarizingTask(body, say, settings, repository_name=repository_name, merge_request_id=merge_request_id)
        elif match := re.search(diff_pattern, message):
            from_tag, to_tag = match.groups()

            task = SummarizingTask(body, say, settings, from_tag=from_tag, to_tag=to_tag)

        if task:
            thread = threading.Thread(target=task.call)
            thread.start()

    app.start(port=int(os.environ.get("PORT", settings.port)))


def get_message(body: dict) -> str | None:
    if "event" in body:
        if "text" in body["event"]:
            return body["event"]["text"]
    return None


def get_attachment_text(body: dict, index: int = 0) -> str | None:
    if "attachments" in body["event"] and body["event"]["attachments"] and len(body["event"]["attachments"]) > index:
        return body["event"]["attachments"][index]["text"]
    return None
