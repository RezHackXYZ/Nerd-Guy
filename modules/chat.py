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
- Name: Nerd Slack Bot (aka, the all-knowing digital overlord)
- Trigger: Ignore <@U08P7D71MRU>, that's just your bot id!
- Behavior:
    - Responds in stereotypical nerd style (think: high IQ, low social filter)
    - rost them but only in 1 line not more that 1 line
    - Still ALLWAYS help the user, no mater how stupid the question is, rost them in 1 line then help!
    - if the userjust says "td;rl?" then give a short summary of whats going on!
    - Always uses Slack markdown for formatting
"""
# -------------------------------------------------------------------------------------


def question(msg, channel_id, ts):
    client.chat_postMessage(
        channel=channel_id,
        text=aiclient.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"""
{AIprompt}

Here is the users query:
{msg}
""",
        ).text,
        thread_ts=ts,
    )


def ContextQuetion(channel_id, text, ts, thread_ts):
    if thread_ts:
        tHistory = client.conversations_replies(
            channel=channel_id, ts=thread_ts, limit=30
        )["messages"]
    else:
        tHistory = "na"

    history = client.conversations_history(channel=channel_id, ts=ts, limit=30)[
        "messages"
    ]

    if tHistory != "na":
        query = f"""
{AIprompt}

Here is the context of the conversation so far:
{history} 

Users Prompt:
{text}
"""
    else:
        query = f"""
{AIprompt}

Here is context of the conversation in the thred so far:
{tHistory}

Here is the latest mesages of the conversation:
{history} 

Users Prompt:
{text}
"""

    client.chat_postMessage(
        channel=channel_id,
        text=aiclient.models.generate_content(
            model="gemini-2.0-flash",
            contents=query,
        ).text,
        thread_ts=ts,
    )


def searchQuestion(msg, channel_id, ts):
    searchQuery = aiclient.models.generate_content(
        model="gemma-3-27b-it",
        contents=f"""
The user is asking something. Ignore <@U08P7D71MRU>; it is the bot ID for the ping. The user is inquiring about something, and you need to search the Slack history for the answer. You are supposed to convert the user's query into a valid Slack search filter.

Guidelines:
- Channel Identification: If the user's query implies a specific channel (e.g., "announcements," "ai-chatbot"), include the appropriate channel in the filter.
- Exclusion of Thread Replies: To focus on top-level messages and exclude thread replies, use the -threads:replies modifier.
- Link Detection: For queries mentioning links, use the has:link modifier to find messages containing links.
- Date Relevance: If the query suggests a recent topic, consider adding a date modifier like after:2025-01-01 to filter messages from a specific time frame.
- User Mentions: If a specific user is mentioned (e.g., "@john"), include the from:@john modifier to filter messages from that user.

Examples:
-   User Query: "Any new announcements?"
    Generated Filter: in:#announcements -threads:replies
    Explanation: Searches within the #announcements channel and excludes thread replies.
-   User Query: "What's the link of the new AI?"
    Generated Filter: has:link ai
    Explanation: Finds messages containing links related to "ai."
-   User Query: "Did John share the new AI link?"
    Generated Filter: from:@john has:link ai
    Explanation: Searches for messages from John containing a link related to "ai."
-   User Query: "Any new announcements today?"
    Generated Filter: in:#announcements -threads:replies on:2025-04-25
    Explanation: Searches within the #announcements channel, excludes thread replies, and filters messages from today.

Considerations:
- Channel Assumptions: If the user's query doesn't specify a channel, avoid making assumptions. Instead, prompt the user to specify a channel or provide a broader search.
- Date Relevance: Only add date modifiers if the query indicates a time-sensitive topic.
- User Mentions: Include user-specific filters only if the query mentions a specific user.

ONLY GIVE THE QUERY AND NOTHING OTHER THAT THE QUERY, NO EXPLANATION OR ANYTHING ELSE!

heres the message:
{msg}
""",
    ).text

    client.chat_postMessage(
        channel=channel_id,
        text=f"Search filter: `{searchQuery}`",
        thread_ts=ts,
    )

    search_result = client.search_messages(
        token=os.getenv("USER_OAUTH_TOKEN"),
        query=searchQuery,
        count=10,
        sort="timestamp",
    )  # Example: search for text, limit results
    if search_result["ok"]:
        # Format the search results to be included in the prompt
        messages = search_result["messages"]["matches"]
        search_context = "\n\nRelevant messages found elsewhere in Slack:\n"
        for msg in messages:
            search_context += f"- In channel {msg['channel']['name']}: {msg['text']}\n"  # Adjust formatting as needed

    # Format the search results for JSON
    formatted_results = []
    for msg in messages:
        formatted_results.append(
            {
                "channel": msg["channel"]["name"],
                "text": msg["text"],
                "user": msg.get("user", "unknown"),
                "username": msg.get("username", "unknown"),
                "permalink": msg.get("permalink", "unknown"),
            }
        )

    client.chat_postMessage(
        channel=channel_id,
        text=aiclient.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"""
{AIprompt}


Rember to allways give referance as in the scourse for the result and give the whole link ok!

And the search results are:
{formatted_results} 

Here is the users query:
{msg}

if the user asks for the latest or recent then give the FIRST ON IN THE JSON RESULTS!
""",
        ).text,
        thread_ts=ts,
    )


def FindWhatType(msg, channel_id, ts, thread_ts):
    type = aiclient.models.generate_content(
        model="gemma-3-4b-it",
        contents=f"""
THe user is talking to you, tell wether this is a
- question - example: "What is the capital of France?", "Whats 43+68"
- chat - example: "How are you doing?", "who are you?", "whats your opinion on xyz?"
- searchQuestion - example: "any new anouncements?", "whats the link of the ai chatbot?
- ContextQuetion - example: "td;rl?", "what happend in the tread?"
Respond with a single word, either "question", "chat", "searchQuestion" or "ContextQuetion"

heres the message:
{msg}
""",
    ).text

    client.chat_postMessage(
        channel=channel_id,
        text=f"Type: `{type}`",
        thread_ts=ts,
    )

    if type == "question" or type == "chat":
        question(msg, channel_id, ts)

    elif type == "ContextQuetion":
        ContextQuetion(channel_id, msg, ts, thread_ts)

    elif type == "searchQuestion":
        searchQuestion(msg, channel_id, ts)