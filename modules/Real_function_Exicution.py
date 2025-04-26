import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
import slack

load_dotenv(dotenv_path=Path(".") / ".env")
aiclient = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
client = slack.WebClient(token=os.getenv("SLACK_OAUTH_TOKEN"))

# INITIALIZATION OF STUFF
# --------------------------------------------------------------------------------------------


def aiprompt(query, model="gemini-2.0-flash"):
    return aiclient.models.generate_content(
        model=model,
        contents=query,
    ).text


def get_history(channel_id, limit, ts):
    if ts == "na":
        return client.conversations_history(
            channel=channel_id, limit=limit
        )["messages"]
    else:
        return client.conversations_history(
                channel=channel_id, ts=ts
            )["messages"]

def send_message(channel_id, text, ts):
    client.chat_postMessage(
        channel=channel_id,
        text=text,
        thread_ts=ts,
    )


def AddEmoji(channel_id, ts, emoji):
    client.reactions_add(
        channel=channel_id,
        name=emoji,
        timestamp=ts,
    )

def RemoveEmoji(channel_id, ts, emoji):
    client.reactions_remove(
        channel=channel_id,
        name=emoji,
        timestamp=ts,
    )