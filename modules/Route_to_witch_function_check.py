from modules.Real_function_Exicution import send_message, aiprompt


def FindWhatType(text, channel_id, ts, thread_ts, user):
    if user == "USLACKBOT":
        return

    elif text.replace("<@U08P7D71MRU> ", "") == "ping":
        send_message(channel_id, "🏓 PONG! 🏓", ts)

    else:
        Type = FindType(text)
        send_message(
            channel_id,
            f"Type: `{Type}`",
            ts,
        )


def FindType(text):
    return aiprompt(query.replace("{query}", text), "gemma-3-4b-it")


query = """
You are a Slack bot. You are given a query and need to classify it into one of the following categories:
Choose whether this query needs:
- context: The query is incomplete and needs more context, or the user is asking for a summary, TL;DR, or something similar.
- search: The user is asking for something that needs to be searched within the Slack workspace, like “What are the new announcements?” Queries that cannot be answered using Slack (e.g., “How many moons does Jupiter have?”) should not be classified as search, because they require searching the internet, not the Slack workspace.
- none: The query is complete and does not need any additional context or search.
Ignore <@U08P7D71MRU> — it's your Slack bot ID being pinged!
Respond with ONLY the type of the query, nothing else, no newline, no extra text, no explanation.

The query is:
{query}
"""
