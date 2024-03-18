# Description

This is a simple Slack bot that listens to messages in a channel, and when it finds a (single)
message linking to a Gitlab MR, it will send the MR contents to OpenAI and post back a summary of the MR as a reply to
the original message.

### Requirements ###
1. Python 3.11 or higher
2. Poetry
3. A previously set-up and installed Slack app 
4. Make sure to subscribe to the `message.channels` event in the Slack app settings.
5. Access to a Gitlab repo and a personal access token with the `api` scope.

### Steps to run locally ##
1. Make a copy of `.env.sample` and rename it to `.env`.
2. Fill in the required environment variables in the `.env` file.
3. Install dependencies in whatever env you like with `poetry install`.
4. Run the app with `python main.py`
5. Expose through ngrok: `ngrok http 3000` (or whatever port you are using)
6. Get the ngrok URL and paste it in the `Request URL` field in the Slack app settings. (make sure to add `/slack/events` at the end of the URL)
