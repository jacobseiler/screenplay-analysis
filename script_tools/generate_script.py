"""
This module focuses on scraping and saving Game of Thrones scripts.  These scripts were found through the
``genius.com/albums/Game-of-thrones`` website. All scripts are saved to the ``./scripts/`` directory (which is created
if it does not exist already).

Author: Jacob Seiler
"""

import os
import re
from typing import List

import numpy as np
import requests

import html2text


def scrape_html_and_save(url: str, fname_out: str, remove_brackets: bool = False) -> None:
    """
    Scrapes a specified URL and saves the HTML to file.

    Parameters
    ----------
    url
        The URL that is being scraped from.

    fname_out
        The name of the file the formatted HTML will be saved to.

    remove_brackets : optional
        Removes the instances in the HTML of the form ``(WORD)``. These are replaced with empty lines.

    Returns
    -------
    None.  The HTML is saved to the ``fname_out``.
    """

    # Set some options for parsing the HTML to text. Idk if most of these actually do anything.
    parser = html2text.HTML2Text()
    parser.unicode_snob = True
    parser.body_width = 0
    parser.skip_internal_links = True
    parser.ignore_links = True

    # Now get the HTML page.
    r = requests.get(url)
    if r.status_code != 200:
        print(f"Encountered error while fetching webpage {url}")
        raise RuntimeError

    # Snip out all that HTML nonsense and leave just the text (this will be the script itself).
    data = r.text
    text = parser.handle(data)

    # If we are removing brackets, we're going to open it up later and save again. So use a tmp name.
    if remove_brackets:
        fname = f"{fname_out}_tmp.txt"
    else:
        fname = f"{fname_out}.txt"

    with open(fname, "w") as f:
        f.write(text)
    print(f"Saved to {fname}")

    # For some scripts, there are obnoxious brackets that specify who characters are talking to.  These will mess with
    # statistics and processing so we need to remove them.
    if remove_brackets:

        import os

        # We will seek occurences of the form "(<ANYTHING>)".
        pattern = "\([^)]*\)"  # noqa: W605

        # Open the file and replace.
        new_fname = f"{fname_out}.txt"
        with open(fname, "r") as f_in, open(new_fname, "w") as f_out:
            for line in f_in:
                new_string = re.sub(pattern, "", line)
                f_out.write(new_string)

        print(f"Removed brackets and resaved to {new_fname}")

        os.remove(f"{fname_out}_tmp.txt")
        print("Deleted old tmp file.")


def generate_episode_names(url: str, output_fname: str, debug: bool = False) -> List[str]:
    """
    Fetches and saves the name of the episodes.

    Parameters
    ----------
    url
        The URL specifying the website containing the list of all episodes.

    output_fname
        The name of the file where the episodes will be saved to.

    debug : optional
        If specified, prints out some messages to help with debugging.

    Returns
    -------
    episode_names
        The names of all the episodes.  These may have to be processed further to provide a proper URL.
    """

    # First scrape the URL and turn the ugly HTML to nicely formatted text.
    scrape_html_and_save(url, output_fname)

    # Now its time to go through the episodes and format the names of the episodes a bit.
    episode_names = []
    with open(output_fname, "r") as f:
        for line in f:
            # Ignore empty lines.
            try:
                _ = (line.split())[0]
            except IndexError:
                continue

            if debug:
                print(f"Line {line}")

            # The episode names are on lines as "### <Episode Name> Lyrics".
            reg_exp = re.compile(r"###. ([A-Z].*)Lyrics", re.IGNORECASE)
            reg_line = reg_exp.split(line)  # Split on this search.

            if debug:
                print(f"Reg_line {reg_line}")

            # A correctly matched line will be a list of the form...
            # ['', '<Name of episode>', '\n']

            # So lines without length 3 are wrong.
            if len(reg_line) < 3:
                continue

            # Trim out surrounding white space and append.
            episode_name = reg_line[1].strip()
            episode_names.append(episode_name)

    return episode_names


if __name__ == "__main__":

    output_dir = "./scripts"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    seasons = np.arange(8, 9)
    for season_num in seasons:

        # First find the names of the episodes in this Season.
        url = f"https://genius.com/albums/Game-of-thrones/Season-{season_num}-scripts"
        fname_out = f"{output_dir}/season-{season_num}-episodes.txt"
        episode_names = generate_episode_names(url, fname_out)

        # Then go through each episode and grab its script.
        for episode_num, episode_name in enumerate(episode_names):

            # For the URL, the episode names use '-' instead of spaces and use lower case
            # letter.
            url_episode_name = episode_name.replace(" ", "-").lower()

            # Commas and apostrophes are the devil.
            url_episode_name = url_episode_name.replace("'", "").lower()
            url_episode_name = url_episode_name.replace(",", "").lower()

            url = f"https://genius.com/Game-of-thrones-{url_episode_name}-annotated"
            fname_out = f"{output_dir}/s{season_num:02}e{episode_num+1:02}"
            scrape_html_and_save(url, fname_out, remove_brackets=True)
