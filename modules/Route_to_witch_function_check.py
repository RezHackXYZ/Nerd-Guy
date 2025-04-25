from modules.Real_function_Exicution import send_message, aiprompt
from modules.none import none
from modules.context import context


def FindWhatType(text, channel_id, ts, thread_ts, user):
    if user == "USLACKBOT":
        return

    if not thread_ts:
        thread_ts = ts
        noThread = True


    if text.replace("<@U08P7D71MRU> ", "") == "ping":
        send_message(channel_id, "🏓 PONG! 🏓", thread_ts)
    else:
        Type = aiprompt(query.replace("{query}", text), "gemma-3-4b-it")
        send_message(
            channel_id,
            f"Type: {Type}",
            thread_ts,
        )

        if "none" in Type:
            none(text, channel_id, thread_ts)
        elif "context" in Type:
            context(text, channel_id, ts, noThread)
        elif "search" in Type:
            print("idk what to do")
            #TODO - ahh 


query = """
You are a Slack bot. You are given a query and need to classify it into one of the following categories:
Choose whether this query needs:
- context: The query is incomplete and needs more context, or the user is asking for a summary, tl;dr, or something similar.
- search: The user is asking for something that needs to be searched within the Slack workspace, like “What are the new announcements?” Queries that cannot be answered using Slack (e.g., “How many moons does Jupiter have?”) should not be classified as search, because they require searching the internet, not the Slack workspace.
- none: The query is complete and does not need any additional context or search.
Ignore <@...> — it's your Slack bot ID being pinged!
Respond with ONLY the type of the query, nothing else, no newline, no extra text, no explanation, AND NO EXTRA SPACES.
If you are confuzed or the user query dosint make any sense, classify it as "none".

The query is:
{query}
"""
