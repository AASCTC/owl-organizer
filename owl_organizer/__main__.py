import requests
import json
import curses
from bs4 import BeautifulSoup
import re
from fuzzywuzzy import fuzz
import time

def search_schemas(strings, query):
    """Perform a fuzzy search for a query in a list of strings"""
    results = []
    for string in strings:
        score = fuzz.token_sort_ratio(string.lower(), query.lower())
        if score > 10:  # Set a threshold for the score
            results.append((string, score))
    results.sort(key=lambda x: x[1], reverse=True)
    return [r[0] for r in results]

schema_names = []
def get_schemas():
    """Search for schemas on schema.org"""
    url = f"https://schema.org/docs/full.html"
    response = requests.get(url)

    if response.status_code != 200:
        return []

    # Parse the HTML page using BeautifulSoup and extract the schema names
    soup = BeautifulSoup(response.content, "html.parser")
    # Assuming `soup` is a BeautifulSoup object
    elements = soup.find_all(class_=re.compile(r'\b(dttBranch|dttFocusItem)\b'))
    schema_names = []
    for element in elements:
        # Remove leading "C." deonoting class name
        schema_name = element.get('id')[2:]
        schema_names.append(schema_name)

    return schema_names

def download_schema(schema_name):
    """Download the schema with the given name from schema.org"""
    url = "https://raw.githubusercontent.com/schemaorg/schemaorg/main/data/releases/15.0/schemaorg-all-http.jsonld"
    response = requests.get(url)

    if response.status_code != 200:
        return None

    data = response.json()["@graph"]

    for d in data:
        if d["@id"] == f"schema:{schema_name}" and d["@type"] == "rdfs:Class":
            return json.dumps(d)

    raise KeyError("Schema not found")

def update_status(stdscr, screen, width, height, status_msg, sleep_factor=0):
    stdscr.attron(curses.A_REVERSE)
    screen.addstr(height-1, 0, status_msg + " " * (width-len(status_msg)-1))
    stdscr.attroff(curses.A_REVERSE)
    screen.refresh()
    time.sleep(sleep_factor)


def display_search_results(stdscr, query, results):
    # Initialize curses
    screen = curses.initscr()
    curses.noecho()
    curses.cbreak()
    screen.keypad(True)

    selected_idx = 0

    # Loop until user quits
    while True:
        # Get screen dimensions
        height, width = screen.getmaxyx()

        # Calculate number of results per page
        results_per_page = height - 4

        # Calculate number of pages
        num_pages = (len(results) + results_per_page - 1) // results_per_page

        # Initialize cursor position and page number
        page_num = selected_idx // results_per_page

        # Clear the screen
        screen.clear()

        # Print the query and page number
        screen.addstr(0, 0, f"Search results for '{query}' - Page {page_num+1}/{num_pages}")
        update_status(stdscr, screen, width, height, f"Use arrow keys to navigate, Enter to download, or Esc to quit.")

        # Print the results for the current page
        j = 0
        for i in range(page_num*results_per_page, (page_num+1) * results_per_page):
            if i < len(results):
                result = results[i]
                if i == selected_idx:
                    stdscr.attron(curses.A_REVERSE)
                screen.addstr(j+1, 0, f"{result}")
                stdscr.attroff(curses.A_REVERSE)
            j += 1
        j = 0

        # Draw the scroll bar
        scroll_bar_height = height // num_pages
        scroll_bar_pos = int(height / num_pages * page_num)
        for i in range(0, scroll_bar_height):
            screen.addstr(scroll_bar_pos+i, width-1, "|")

        # Move the cursor to the current position
        screen.move(selected_idx % results_per_page + 1, 0)

        # Refresh the screen
        screen.refresh()

        # Handle user input for navigating the search results
        key = screen.getch()

        # Handle arrow key input
        if key == curses.KEY_UP:
            selected_idx -= 1
            if selected_idx < 0:
                selected_idx = 0
        elif key == curses.KEY_DOWN:
            selected_idx += 1
            if selected_idx >= len(results):
                selected_idx = len(results)-1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            # Download the selected schema and save it to a file
            schema_name = results[selected_idx]
            update_status(stdscr, screen, width, height, f"Downloading schema \"{schema_name}\"...")
            schema_data = download_schema(schema_name)
            if schema_data is not None:
                filename = f"schemas/{schema_name}.jsonld"
                with open(filename, "w") as file:
                    file.write(schema_data)
                update_status(stdscr, screen, width, height, f"Schema saved to {filename}", sleep_factor=3)
            else:
                update_status(stdscr, screen, width, height, f"Error: Could not download schema {schema_name}", sleep_factor=3)
        elif key == 27:  # ESC key
            break

def main(stdscr):
    print("Please wait while the list of schemas is fetched...")
    curses.curs_set(0)
    stdscr.move(1,0)
    schema_names = get_schemas()
    # Set up the initial screen
    curses.curs_set(0)
    stdscr.clear()
    stdscr.addstr(0, 0, "Enter a schema name to search for:")
    stdscr.refresh()

    # Get user input for the search query
    curses.echo()
    query = stdscr.getstr(1, 0).decode()
    curses.noecho()

    # Search for schemas on schema.org
    results = search_schemas(schema_names, query)

    # Display the search results in a scrollable list
    display_search_results(stdscr, query, results)

    # Clean up curses
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()


if __name__ == "__main__":
    curses.wrapper(main)