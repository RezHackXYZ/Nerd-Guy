from modules.Real_function_Exicution import (
    send_message,
    AddEmoji,
    RemoveEmoji,
    aiprompt,
    get_history,
)
from modules.UnknownTermFinder import FindTerms
import json
import random


def stage1(text, channel_id, ts, thread_ts, user):
    if user == "USLACKBOT":
        return
    if not thread_ts:
        thread_ts = ts
    if text.replace("<@U08P7D71MRU> ", "") == "ping":
        send_message(channel_id, "🏓 PONG! 🏓", thread_ts)

    else:
        with open("config.json", "r") as f:
            config = json.load(f)
        thinkEmoji = random.choice(config["AiThinkEmoji"])

        AddEmoji(channel_id, ts, thinkEmoji)

        terms = FindTerms(text)
        search = "none"
        contextNeeded = aiprompt(
            f"""
For the give query, catogrize it into 
1. "100" - user has asked for a summary or, a tl;dr etc
2. "5" - normal quetion, no summary needed
in most cases it will be one of these but if you feal it is somwhere in between needed for the context then
give a number inbetween 5 and 100
only respond with the number and nothing else!
Ignore <@...> — it's your Slack bot ID being pinged!

The Users query is:
{text}
""",
            "gemma-3-4b-it",
        )

        send_message(
            channel_id,
            aiprompt(
                f"""
Info:
You are a Slack bot. AND USE SLACK MARKDOWN!
Ignore <@...> — it's your Slack bot ID being pinged!
You may use emojis in your msgs!

Instruction/Behavior: {config["AiBehaviour"]}

{'' if not thread_ts else f"Context of the conversation so far In the thread so far: {get_history(channel_id, '', thread_ts)}"}

Context of the conversation so far In the channel so far: {get_history(channel_id, contextNeeded, "na")}

{'' if terms == "none" else f"Here is the explanation of the unknown terms: {terms}"}

Some Notes for you:{config["notes"]}

{'' if search == "none" else f"Here is the search result of anything needed: {search}"}

User Query: {text}
"""
            ),
            thread_ts,
        )

        RemoveEmoji(channel_id, ts, thinkEmoji)
        AddEmoji(channel_id, ts, random.choice(config["AiAnsweredEmoji"]))
