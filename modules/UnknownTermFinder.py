from modules.Real_function_Exicution import aiprompt
import json

def FindTerms(string):
    with open("config.json", "r") as f:
        config = json.load(f)

    UnknownTerms = aiprompt(f"""
Ignore <@...> — it's your Slack bot ID being pinged!
You are given a query from a user and need to find any unknown terms in the query.
Unknow terms are words that are not in the english dictionary or are not common acronyms.
give each term comma seperated and only the term nothing else!
if there are no unknown terms return "none"
ignore spelling mistakes and other errors

only provide the term, if it is part of these:
{config["terms"]}

The query is:
{string}
""","gemma-3-4b-it")
    UnknownTerms = UnknownTerms.replace("\n", "")
    UnknownTerms = UnknownTerms.split(",")

    

    UnknownTemsList={

    }

    if UnknownTerms[0] == "none":
        return "none"
    for term in UnknownTerms:
        if term in config["terms"]:
            UnknownTemsList[term] = config["terms"][term]
        else:
            UnknownTemsList[term] = "unknown"

    return UnknownTemsList