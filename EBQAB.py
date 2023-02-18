from allennlp.predictors.predictor import Predictor
import allennlp_models.rc
import textwrap
import random
from googlesearch import search
import requests, html5lib
from bs4 import BeautifulSoup
import wikipediaapi
import wolframalpha
from timeit import default_timer
import sys

predictor = Predictor.from_path("https://storage.googleapis.com/allennlp-public-models/bidaf-elmo.2021-02-11.tar.gz")
wikipedia = wikipediaapi.Wikipedia("en")
wolframalpha_client = wolframalpha.Client("67PEAP-WG9HRK2966")

def answer(question):
    answers = []
    for result in search(question, tld="com", num=3, stop=3, pause=2):
        information = """\
                      """
        html = requests.get(result)
        soup = BeautifulSoup(html.text, "html5lib")
        for txt in soup.find_all("p"):
            information += "\n"+txt.get_text()
        try:
            ans = ""
            prediction = predictor.predict(
                            passage=textwrap.dedent(information),
                            question=question
                         )
            for paragraph in information.split("\n"):
                if prediction["best_span_str"] in paragraph:
                    ans += paragraph.strip()
            if not ans:
                answers.append(prediction["best_span_str"])
            else:
                answers.append(ans)
        except:
            continue
    if len(answers) == 0:
        return ""
    else:
        final_answer = random.choice(answers)
        return final_answer
  
def wiki(query):
    page = wikipedia.page(query)
    result = page.summary
    return result 

def wolfram(query):
    result = wolframalpha_client.query(query)
    return result

print("ELMo-BiDAF Question Answering Bot (EBQAB)")
print("Input a command.")
print("Type \"/ask\" to ask a question or \"/help\" for usage.")
cache = {}
while True:
    start = default_timer()
    command = input("Input: ")
    if command.strip().lower().startswith("/ask"):
        question = command.replace("/ask", "", 1).strip()
        if not question:
            print("Please input a question.")
        else:
            print("Thinking....")
            if question.strip().lower() in cache.keys():
                if (default_timer() - cache[question.strip().lower()][1]) <= 3600:
                    ans = cache[question.strip().lower()][0]
                    cache[question.strip().lower()] = cache.pop(question.strip().lower())
                else:
                    ans = answer(question)
                    cache[question.strip().lower()] = [ans, default_timer()]
            else:
                ans = answer(question)
                cache[question.strip().lower()] = [ans, default_timer()]
            if not ans:
                print("There are no answers available.")
            else:
                print(f"Answer: {ans}")
    elif command.strip().lower().startswith("/feedback"):
        if not bool(cache):
            print("There is currently nothing saved in cache.")
        else:
            correction = command.replace("/feedback", "", 1).strip()
            if not correction:
                print("Please give a correction that you want to make.")
            else:
                print("The previous answer will be replaced with this correction.")
                cache[list(cache.keys())[-1]] = [correction, default_timer()]
    elif command.strip().lower().startswith("/help"):
        print(textwrap.dedent("""\
                              List of commands for EBQAB:
                              - /ask [question]: Ask a question and get the answer for it.
                              - /feedback [correction]: Make a correction to the previous answer if it is incorrect.
                              - /help: Get a list of commands for EBQAB and their usage.
                              - /wiki [query]: (Additional Feature) Search the result for a query with Wikipedia.
                              - /wolfram [query]: (Additional Feature) Search the result for a query with Wolfram|Alpha.
                              - /exit: Exit the application."""))
    elif command.strip().lower().startswith("/wiki"):
        query = command.replace("/wiki", "", 1).strip()
        if not query:
            print("Please input a query.")
        else:
            result = wiki(query)
            if not result:
                print("There are no results available.")
            else:
                print(f"Result: {result}")
    elif command.strip().lower().startswith("/wolfram"):
        query = command.replace("/wolfram", "", 1).strip()
        if not query:
            print("Please input a query.")
        else:
            result = wolfram(query)
            if not result:
                print("There are no results available.")
            else:
                print("Result:")
                for pod in result.pods:
                    for subpod in pod.subpods:
                        print(subpod.plaintext)
    elif command.strip().lower().startswith("/exit"):
        print("Exitting...")
        sys.exit()
    else:
        print("Invalid command. Type \"/ask\" to ask a question or \"/help\" for usage.")


