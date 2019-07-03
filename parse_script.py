from character import Character
from episode import Episode

import re
import requests
import numpy as np
import html2text


def generate_txt(url, save_path):

    # Set some options for parsing the HTML to text.
    parser = html2text.HTML2Text()
    parser.unicode_snob = True
    parser.body_width = 0
    parser.skip_internal_links = True
    parser.ignore_links = True

    # Now get the HTML page.
    r = requests.get(url)
    if r.status_code != 200:
        print("Encountered error while fetching webpage {0}".format(url))
        raise RuntimeError

    # Snip out all that HTML nonsense and leave just the text (this will be the script
    # itself).
    data = r.text
    text = parser.handle(data)

    # Now save the trimmed text.
    fname_out = "{0}/s01e02.txt".format(save_path)
    with open(fname_out, "w") as f:
        f.write(text)


def parse_txt(fname):

    episode = Episode(1, 1)

    with open(fname, "r") as f:
        for line in f:

            # Ignore empty lines.
            try:
                _ = (line.split())[0]
            except IndexError:
                continue

            # Lines starting with "[" a scene descriptions.
            if line[0] == "[":
                continue

            # Everything is good. This is a line spoken by a character.
            parse_character_line(line, episode)

    for character in episode.characters.keys():
        print("{0} has {1} lines".format(character, episode.characters[character].line_count))
        print(episode.characters[character].lines)
        print("")


def parse_character_line(line, episode):

    # A line spoken by a character will start with "**Character name:**".
    # Be careful, sometimes the colon is inside the ** or outside with a space...
    print("Line {0}".format(line))

    # Search for "**<ANYTHING>:**" OR "**<ANYTHING>**:" OR **<ANYTHING>** :".
    # Here '[A-Z]' means we only match actual characters. This allows us to ignore
    # extraneous '****' at the start of some lines (e.g., one line is '**********Catelyn
    # Stark:** 17 years ago you rode off with Robert Baratheon...'
    reg_exp = re.compile(r"\*\*([A-Z].*)\:\*\*|\*\*([A-Z].*)\*\*\:|\*\*([A-Z].*)\*\* \:", re.IGNORECASE)
    character_line = reg_exp.split(line)  # Split on this search.

    print("Character Line {0}".format(character_line))

    # Now since we have defined 3 search times, a line spoken by a character will return a
    # list of the form...
    # ['', <CHARACTER_NAME OR NONE>, <CHARACTER_NAME OR NONE>, <CHARACTER_NAME OR NONE>, 'Actual line']
    # TWO ELEMENTS of character_line[1 or 2 or 3] will be None. The remaining one will be
    # not None.

    # Garbage lines will have length less than 5.
    if len(character_line) < 5:
        return

    # Otherwise, let's filter out into a list that is [character_name, spoken_line].
    filtered_line = list(filter(None, character_line))

    # Actually sometimes extraneous "****" cause this filtered list to be 3 elements long,
    # ["*****", character_name, spoke_line]. Check for this.
    if len(filtered_line) == 2:
        character_name = filtered_line[0]
        spoken_line = filtered_line[1]
    elif len(filtered_line) == 3:
        character_name = filtered_line[1]
        spoken_line = filtered_line[2]
    else:
        print("line is {0}\tregex line is {1}\tfiltered line is {2}".format(line,
            character_line, filtered_line))
        raise ValueError

    # episode.characters is a dict["character_name": Character Class Instance].
    # So let's check if we have already instantiated this character. If not, initialize.
    if character_name not in episode.characters.keys():
        episode.characters[character_name] = Character(character_name)

    character = episode.characters[character_name]

    # Update the number of lines.
    character.line_count += 1

    # Now there is an annoying "\n" at the end of each line. Eliminate it...
    spoken_line = spoken_line.split("\n")

    # Still a little bit of white space at the start and end.
    spoken_line = spoken_line[0].strip()

    # Update the spoken line.
    character.lines.append(spoken_line)



if __name__ == "__main__":


    url = "https://genius.com/Game-of-thrones-the-kingsroad-annotated"
    save_path = "/home/jseiler/screenplay-analysis/scripts"
    #generate_txt(url, save_path)

    txt_file_path = "/home/jseiler/screenplay-analysis/scripts/s01e02.txt"
    parse_txt(txt_file_path)
