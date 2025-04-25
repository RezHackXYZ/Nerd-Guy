from modules.Real_function_Exicution import send_message, aiprompt, get_history


def context(text, channel_id, thread_ts, nothred):
    contextAmount = aiprompt(
        f"""
You are a Slack bot. You are given a query from a user and need to tell how mutch context is needed to answer the query.
1 being a case where the user has asked for the latest anouncment or somthing like that!
50 being a case where the user has asked to summarize whats going on in the chanle or a td;rl!
min 1 and max 50

The query is:
{text}
""",
        "gemma-3-4b-it",
    )

    with open("prompt.txt", "r", encoding="utf-8") as file:
        prompt = file.read()

    if nothred == True:
        send_message(
            channel_id,
            aiprompt(
                f"""
Info:
You are a Slack bot.
Ignore <@...> — it's your Slack bot ID being pinged!

Instruction/Behavior:
{prompt}

Context of the conversation so far In the channel so far:
{get_history(channel_id, contextAmount, "na")}

User Query:
{text}
"""
            ),
            thread_ts,
        )

    else:
        send_message(
            channel_id,
            aiprompt(
                f"""
Info:
You are a Slack bot.
Ignore <@...> — it's your Slack bot ID being pinged!

Instruction/Behavior:
{prompt}

Context of the conversation so far In the thread so far:
{get_history(channel_id,"", thread_ts)}

Context of the conversation so far In the channel so far:
{get_history(channel_id, contextAmount, "na")}

User Query:
{text}
"""
            ),
            thread_ts,
        )
