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
# mandatory above


def get_gemini_response(prompt, history):

    query = f"""
You are a nerd Slack bot AI!
You must start every response to a question with either:
":tw_nerd_face: :point_up: According to my calculations: " or ":tw_nerd_face: :point_up: Erm, actually: "
When replying, ignore any <@...> mention — that's just your name being summoned.
- Give crisp and simple answers to valid questions.
- If its not a question or clearly a waste of your time, be sarcastic.
- Use Slack markdown in your replies for formatting.

Here is the context of the conversation so far:
{history} 

Prompt:
{prompt}
"""

    return aiclient.models.generate_content(
        model="gemini-2.0-flash",
        contents=query,
    ).text


def process_and_reply(channel_id, text, ts):
    history = client.conversations_replies(
        channel=channel_id,
        ts=ts,
        limit=20,
    )


    client.chat_postMessage(
        channel=channel_id,
        text=get_gemini_response(text, history),
        thread_ts=ts,
    )


@slack_event_adapter.on("app_mention")
def msg(payload):
    event = payload.get("event", {})
    channel_id = event.get("channel")
    user = event.get("user")
    text = event.get("text")
    ts = event.get("ts")

    if user == "USLACKBOT":
        return

    thread = threading.Thread(target=process_and_reply, args=(channel_id, text, ts))
    thread.start()


#
# mandatory bellow
if __name__ == "__main__":
    app.run(debug=True)
