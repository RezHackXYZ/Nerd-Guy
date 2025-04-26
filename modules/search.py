from modules.Real_function_Exicution import aiprompt, search


def DoSearch(text):
    para = aiprompt(
        f"""
this is the users query:
{text}

Ignore <@...> — it's your Slack bot ID being pinged!
as per you dose this query need to be searched in SLACK, SLACK NOT THE INTERNET?
example: 
"news?": yes! they want the news on anouncemts
"hi!": no! they just want to say hi
"help me!": no! they just want help
"how are you?": no! they just want to say hi

that is thing 1 if your awnser is no then just give the response as "no" and your done!

but if its yes then give the following:
"yes,number,sort,query"

yes => as in yes this query needs to be searched
number => the number of results to be returned (for news it wil be 1 as the user want only the latest but for other thing it will be a larger no with max 50 use your geuse!)
sort => the sort of the results (for news it will be "timestamp" but for other thing it will be "score")
query => the query to be searched in slack (for news it will be "in:#announcements -threads:replies" as we want to search in the announcements channel and and only the top lever msg no replys or threads, this is simple slack search filtes use your understanding!)

""",
        "gemma-3-4b-it",
    )

    if para == "no":
        return "none"

    para = para.replace("\n", "")
    para = para.split(",")

    return search(
        para[2], para[3], int(para[1]), 
    )
