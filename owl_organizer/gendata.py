import openai
import json
import os
import time
import curses
import uuid

from openai.error import InvalidRequestError, ServiceUnavailableError, RateLimitError

with open('{}/.config/gptchat.conf'.format(os.path.expanduser("~"), 'r')) as file:
    api_key = file.readline().strip();
    openai.api_key = api_key

model = "text-davinci-003"
temperature = 0.9

def gendata(jsonld, n, schema_class):
    mainresults = []
    for i in range(n):
        result = {}
        result["@context"] = "https://schema.org"
        generated_uuid = uuid.uuid4().hex
        result["@type"] = schema_class
        result["@id"] = f"{schema_class}-{generated_uuid}"
        for j in jsonld["@graph"]:
            if j["@type"] == "rfds:Class":
                continue
            label = j["rdfs:label"]
            if type(label) is dict:
                label = label["@value"]
            comment = j["rdfs:comment"]
            prompt = f"""
            Generate a random value for a \"{label}\". A \"{label}\" is defined exactly as specified on the next line.

            \"{comment}\"

            Do not reply with anything other than the random value. No preamble text, or ending text.
            """
            try:
                response = openai.Completion.create(
                    engine=model,
                    prompt=prompt,
                    temperature=temperature,
                    max_tokens=2048,
                )
                example = response.choices[0].text.strip()
                result[label] = example
            except InvalidRequestError as e:
                raise RunTimeError("AI data generation is unavailable at this time.")
            except ServiceUnavailableError as e:
                raise RunTimeError("AI data generation is unavailable at this time.")
            except RateLimitError as e:
                raise RunTimeError("AI data generation is unavailable at this time.")
        mainresults.append(result)
    return mainresults


def generate_data(stdscr):
    while True:
        curses.curs_set(0)
        stdscr.move(1,0)
        # Set up the initial screen
        curses.curs_set(0)
        stdscr.clear()
        stdscr.addstr(0, 0, "Enter a schema name to generate data for:")
        stdscr.refresh()

        # Get user input
        curses.echo()
        schema = stdscr.getstr(1, 0).decode().strip()
        curses.noecho()

        try:
            f = open(f"schemas/{schema}.jsonld")
            f.close()
        except FileNotFoundError as e:
            stdscr.addstr(3, 0, "Error: Schema has not been downloaded first.")
            stdscr.refresh()
            time.sleep(3)
            continue
        break

    while True:
        curses.curs_set(0)
        stdscr.move(1,0)
        # Set up the initial screen
        curses.curs_set(0)
        stdscr.clear()
        stdscr.addstr(0, 0, "Enter number of data samples to generate:")
        stdscr.refresh()

        # Get user input
        curses.echo()
        number = stdscr.getstr(1, 0).decode().strip()
        curses.noecho()

        try:
            number = int(number)
            if number < 1:
                raise ValueError("No negative numbers allowed")
        except ValueError as e:
            stdscr.addstr(3, 0, "Error: You must type an integer")
            stdscr.refresh()
            time.sleep(3)
            continue
        break


    curses.curs_set(0)
    stdscr.clear()
    stdscr.refresh()
    print("Please wait while the schema data is generated...")

    with open(f"schemas/{schema}.jsonld") as f:
        jsonld = json.load(f)
        try:
            results = gendata(jsonld, number, schema)
        except Exception as e:
            stdscr.addstr(1, 0, "AI data generation is unavailable at this time")
            stdscr.refresh()
            time.sleep(3)
            return
        try:
            with open(f"datasets/{schema}.json") as g:
                oldresults = json.load(g)
                for r in results:
                    oldresults.append(r)
                results = oldresults
        except FileNotFoundError as e:
            pass
        except json.decoder.JSONDecodeError as e:
            pass
        with open(f"datasets/{schema}.json", "w") as g:
            json.dump(results, g, indent=2)
