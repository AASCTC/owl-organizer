from fuzzywuzzy import process
import json
import curses
import time

from fuzzywuzzy import fuzz

def scrollable_text(screen, lines):
    curses.curs_set(0)
    screen.clear()
    screen.refresh()
    # Set up variables
    current_line = 0
    max_lines = len(lines)
    screen_height, screen_width = screen.getmaxyx()
    pad = curses.newpad(max_lines, screen_width)

    # Fill pad with lines
    for i, line in enumerate(lines):
        if len(line) > screen_width:
            line = line[:screen_width-3] + "..."
        pad.addstr(i, 0, line)

    # Display initial pad on screen
    pad.refresh(current_line, 0, 0, 0, screen_height-1, screen_width-1)

    # Loop for handling user input
    while True:
        # Get user input
        key = screen.getch()

        # Handle user input
        if key == curses.KEY_UP:
            current_line = max(0, current_line - 1)
        elif key == curses.KEY_DOWN:
            current_line = min(max_lines-1, current_line + 1)
        elif key == 27:  # ESC key
            break

        # Refresh pad on screen
        pad.refresh(current_line, 0, 0, 0, screen_height-1, screen_width-1)

    # Clean up curses when done
    return


def search_json(data, field, search_term):
    """
    Performs a fuzzy search on a list of JSON datasets on a specific field.

    Args:
    - data: A list of JSON datasets to search through
    - field: A field to search
    - search_term: The search term to use

    Returns:
    - A list of tuples containing the matching dataset and the similarity score
    """

    # Initialize an empty list to store the matching datasets and their scores
    results = []

    # Iterate through each dataset in the data list
    for dataset in data:
        # Extract the field value for the current dataset
        if field not in dataset.keys():
            continue
        dataset_field_value = dataset[field]

        # Calculate the similarity score between the search term and the dataset field value
        similarity_score = fuzz.ratio(search_term, dataset_field_value)

        # Add the matching dataset and its similarity score to the results list
        if similarity_score > 10: # you can adjust this score threshold based on your requirements
            results.append((dataset, similarity_score))

    results = sorted(results, key = lambda x: x[1], reverse=True)
    # Return the list of matching datasets and their scores
    return results

def search_data(stdscr):
    while True:
        curses.curs_set(0)
        stdscr.move(1,0)
        # Set up the initial screen
        curses.curs_set(0)
        stdscr.clear()
        stdscr.addstr(0, 0, "Enter the schema name with the dataset to search in:")
        stdscr.refresh()

        # Get user input
        curses.echo()
        schema = stdscr.getstr(1, 0).decode().strip()
        curses.noecho()

        try:
            f = open(f"datasets/{schema}.json")
            f.close()
        except FileNotFoundError as e:
            stdscr.addstr(3, 0, "Error: Dataset has not been created.")
            time.sleep(3)
            continue
        break

    curses.curs_set(0)
    stdscr.move(1,0)
    # Set up the initial screen
    curses.curs_set(0)
    stdscr.clear()
    stdscr.addstr(0, 0, "Enter the dataset field to search in:")
    stdscr.refresh()

    # Get user input
    curses.echo()
    field = stdscr.getstr(1, 0).decode().strip()
    curses.noecho()

    curses.curs_set(0)
    stdscr.move(1,0)
    # Set up the initial screen
    curses.curs_set(0)
    stdscr.clear()
    stdscr.addstr(0, 0, "Enter the search term:")
    stdscr.refresh()

    # Get user input for the search query
    curses.echo()
    search_term = stdscr.getstr(1, 0).decode().strip()
    curses.noecho()

    curses.curs_set(0)
    stdscr.clear()
    stdscr.refresh()
    print("Searching...")

    with open(f"datasets/{schema}.json") as f:
        data = json.load(f)
        try:
            matches = search_json(data, field, search_term)
        except Exception as e:
            stdscr.addstr(1, 0, "Error occured while searching data")
            stdscr.refresh()
            time.sleep(3)
            return
        results = []
        for match in matches:
            results.append(match[0]["@id"])
            results.append("Similarity Score: " + str(match[1]))
            results.append("-------------------------")
        scrollable_text(stdscr, results)
