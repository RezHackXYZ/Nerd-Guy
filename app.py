import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask
from slackeventsapi import SlackEventAdapter
from google import genai
import threading

load_dotenv(dotenv_path=Path(".") / ".env")
aiclient = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
client = slack.WebClient(token=os.getenv("SLACK_OAUTH_TOKEN"))
app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(
    os.getenv("SLACK_SIGNING_SECRET"), "/slack/events", app
)

from modules.Route_to_witch_function_check import FindWhatType


@slack_event_adapter.on("app_mention")
def msg(payload):
    event = payload.get("event", {})
    channel_id = event.get("channel")
    user = event.get("user")
    text = event.get("text")
    ts = event.get("ts")
    thread_ts = event.get("thread_ts")

    thread = threading.Thread(
        target=FindWhatType, args=(text, channel_id, ts, thread_ts,user)
    )
    thread.start()


# -------------------------------------------------------------------------------------
# mandatory bellow
if __name__ == "__main__":
    app.run(debug=True)
