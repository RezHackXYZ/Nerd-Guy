
from modules.Real_function_Exicution import send_message, aiprompt

def none(text, channel_id, thread_ts):
    with open("prompt.txt", 'r', encoding='utf-8') as file:
        prompt = file.read()
    
    RealPrompt = f"""
Info:
You are a Slack bot.
Ignore <@...> — it's your Slack bot ID being pinged!

Instruction/Behavior:
{prompt}

User Query:
{text}
"""

    response = aiprompt(RealPrompt)

    send_message(
            channel_id,
            response,
            thread_ts,
        )
