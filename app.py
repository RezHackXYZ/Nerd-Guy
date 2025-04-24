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
# -------------------------------------------------------------------------------------
AIprompt = """
You are a nerd Slack bot You know Everything, and will felx but help the user! Talk in steriotipical nerd style.
When replying, ignore any <@...> mention — that's just your name being summoned.
- Give crisp and simple answers to valid questions.
- If its not a question or clearly a waste of your time, be sarcastic And roast them! rost them on anything the gramer anything!.
- Use Slack markdown in your replies for formatting.
"""
# -------------------------------------------------------------------------------------


def get_gemini_response(prompt, history, tHistory):
    if tHistory != "na":
        query = f"""
{AIprompt}

Here is the context of the conversation so far:
{history} 

Users Prompt:
{prompt}
"""
    else:
        query = f"""
{AIprompt}

Here is context of the conversation in the thred so far:
{tHistory}

Here is the latest mesages of the conversation:
{history} 

Users Prompt:
{prompt}
"""

    return aiclient.models.generate_content(
        model="gemini-2.0-flash",
        contents=query,
    ).text


def process_and_reply(channel_id, text, ts, thread_ts):
    if thread_ts:
        tHistory = client.conversations_replies(
            channel=channel_id, ts=thread_ts, limit=30
        )["messages"]
    else:
        tHistory = "na"

    history = client.conversations_history(channel=channel_id, ts=ts, limit=30)[
        "messages"
    ]

    client.chat_postMessage(
        channel=channel_id,
        text=get_gemini_response(text, history, tHistory),
        thread_ts=ts,
    )


@slack_event_adapter.on("app_mention")
def msg(payload):

    event = payload.get("event", {})
    channel_id = event.get("channel")
    user = event.get("user")
    text = event.get("text")
    ts = event.get("ts")
    thread_ts = event.get("thread_ts")

    if user == "USLACKBOT" or channel_id == "C0266FRGV":
        return

    thread = threading.Thread(
        target=process_and_reply, args=(channel_id, text, ts, thread_ts)
    )
    thread.start()
    """

    searchQuery = text.replace("<@U08P7D71MRU>", "")

    search_result = client.search_messages(
        token=os.getenv("USER_OAUTH_TOKEN"), query=searchQuery, count=5
    )  # Example: search for text, limit results
    if search_result["ok"]:
        # Format the search results to be included in the prompt
        messages = search_result["messages"]["matches"]
        search_context = "\n\nRelevant messages found elsewhere in Slack:\n"
        for msg in messages:
            search_context += f"- In channel {msg['channel']['name']}: {msg['text']}\n"  # Adjust formatting as needed

    client.chat_postMessage(
        channel=channel_id,
        text=search_result["messages"]["matches"],
        thread_ts=ts,
    )"""


# -------------------------------------------------------------------------------------
# mandatory bellow
if __name__ == "__main__":
    app.run(debug=True)
