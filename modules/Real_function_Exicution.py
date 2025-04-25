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

# To get the AI msgs
def aiprompt(query,model="gemini-2.0-flash"):
    return aiclient.models.generate_content(
        model=model,
        contents=query,
    ).text


#for sending msgs
def send_message(channel_id, text, ts):
    client.chat_postMessage(
        channel=channel_id,
        text=text,
        thread_ts=ts,
    )