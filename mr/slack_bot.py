import os
import re
import threading
from typing import Any

from slack_bolt import App

from mr.mr import summarize_mr
from mr.settings import Settings

# Define the pattern you want to match to extract the MR id
pattern = r"merge_requests/(\d+)"

class Task:
    def __init__(self, merge_request_id: str, body: str, say: Any, settings: Settings):
        self.merge_request_id = merge_request_id
        self.body = body
        self.say = say
        self.settings = settings

    def call(self):
        print(f"The merge request ID is: {self.merge_request_id}, gonna summarize now...")

        summary = summarize_mr(self.settings, self.merge_request_id)

        print(f"The merge request ID is: {self.merge_request_id}, summarizing done, so gonna reply now...")
        self.say({"text": summary, "thread_ts": self.body["event"]["ts"]})


def start_bot(settings: Settings):
    # Initialize the Slack app with your bot token
    app = App(
        token=settings.slack_token,
        signing_secret=settings.slack_signing_secret
    )
    @app.event("message")
    def handle_message(body, say, logger):
        # Check if the message is from the desired channel
        if body["event"]["channel"] == settings.slack_channel_id:
            message = body["event"]["text"]

            # Find the merge request ID using re.search
            match = re.search(pattern, message)
            if match:
                merge_request_id = match.group(1)

                task = Task(merge_request_id, body, say, settings)

                thread = threading.Thread(target=task.call)
                thread.start()
            else:
                print("No merge request ID found in the string.")


    app.start(port=int(os.environ.get("PORT", settings.port)))
