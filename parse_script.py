from character import Character
from episode import Episode

import re

import numpy as np


def normalize_name(character_name, allowed_double_names=None):

    import string
    # First be consistent and capitalize the first letter in all names of a character.
    # Use `capwords` rather than `title` because `title` capitalizes letters after
    # apostrophes.
    character_name = string.capwords(character_name)

    # There are only a handful of names we (by default) allow to be multiple words.
    if allowed_double_names is None:
        allowed_double_names = [
            "The Hound", "Khal Drogo", "Maester Luwin", "Septa Mordane",
            "Waymar Royce", "Grand Maester Pycelle", "Street Urchin",
            "Kings Landing Baker", "Hot Pie", "Ser Alliser",
            "Maryn Trant", "King Joffrey", "King's Landing Page",
            "Wine Merchant", "Stable Boy", "Old Nan", "Little Bird"
        ]

    # Populate a bunch of <House> <scout/warrior/guards>.
    houses = ["Lannister", "Stark", "Tyrell", "Baratheon", "Kings", "Nights Watch", "Kings Landing"]
    NPC_classes = ["Scout", "Warrior", "Guards", "Bannerman", "Bannermen", "Guard", "Boy"]
    random_NPCs = []
    for house in houses:
        for NPC_class in NPC_classes:
            random_NPCs.append(f"{house} {NPC_class}")

    allowed_double_names = allowed_double_names + random_NPCs

    # Now if a character's name is not allowed to be double, we will split it into two and
    # take the first name.
    if character_name not in allowed_double_names:
        character_name = character_name.split()[0]

    # We also map some names explicitly to others...
    name_map = {
        "Sandor": "The Hound",
        "Luwin": "Maester Luwin",
        "Drogo": "Khal Drogo",
        "Pycelle": "Grand Maester Pycelle",
        "King Joffrey": "Joffrey",
        "Samwell": "Sam",
        "Alliser": "Ser Alliser"
    }

    if character_name in name_map:
        character_name = name_map[character_name]

    return character_name

def parse_episode(fname, episode, debug=False):

    with open(fname, "r") as f:

        # Strictly speaking I don't need to loop over lines here to get the character
        # lines. I could instead pass the entire file and use regex to pull out all the
        # character lines.  However, in future, I will want to pull out scenes
        # chronologically. Hence it will be useful to iterate line-by-line.
        for line in f:

            # Ignore empty lines.
            try:
                _ = (line.split())[0]
            except IndexError:
                continue

            # Parse the line to see if a character spoke it (and add to the appropriate
            # character).
            parse_character_line(line, episode, debug=debug)


def parse_character_line(line, episode, debug=False):

    if debug:
        print("Line {0}".format(line))

    # The format of the character line will change slightly depending upon the episode and
    # season.  Let's use a dedicated function to separate the line into the character name
    # and their spoken line.
    character_name, spoken_line = regex_character_line(line, episode, debug=debug)

    # Got a garbage line.
    if character_name is None or spoken_line is None:
        return

    # At this point, the assigned character has been given a line. However,
    # some scripts name characters slightly differently.  For example, "Cersei" in one
    # script may be "Cersei Baratheon" in another or "CERSEI LANNISTER" in another
    # different one.  Hence let's normalize the name so it is consistent across episodes
    # and seasons.
    character_name = normalize_name(character_name)

    # episode.characters is a dict["character_name": Character Class Instance].
    # So let's check if we have already instantiated this character. If not, initialize.
    if character_name not in episode.characters.keys():
        episode.characters[character_name] = Character(character_name)

    character = episode.characters[character_name]

    # Update the spoken line.
    character.lines.append(spoken_line)


def regex_character_line(line, episode, debug=False):

    # For Season 1, all episodes other than episode 1 follow the same format.
    if episode.season_num == 1 and episode.episode_num == 1:
        character_name, spoken_line = regex_season_one_episode_one_line(line, debug=debug)
    elif episode.season_num == 1 and episode.episode_num > 1:
        character_name, spoken_line = regex_season_one_episode_greater_one_line(line, debug=debug)

    return character_name, spoken_line


def regex_season_one_episode_one_line(line, debug=False):

    # Lines starting with "[" a scene descriptions.
    if line[0] == "[":
        return None, None

    # A line spoken by a character will start with "CHARACTER_NAME:".

    # Search for any word starting with a capital word followed by a ":".
    reg_exp = re.compile(r"([A-Z].*\:)")
    character_line = reg_exp.split(line)  # Split on this search.

    if debug:
        print("Character Line {0}".format(character_line))

    # A line spoken by a character will return a list of the form...
    # ['', CHARACTER_NAME:, <Spoken line>]

    # Garbage lines will have length less than 3.
    if len(character_line) < 3:
        return None, None

    # The character name has an extra ":" at the end. Eliminate it.
    character_name = character_line[1][:-1]

    # Finally, strip any whitespace round the outside, round the outside.
    character_name = character_name.strip()

    # To be a valid line, all letters must be upper case.
    if character_name != character_name.upper():
        return None, None

    # The spoken line is the final element of `character_line`.
    spoken_line = character_line[2]

    # Now there is an annoying "\n" at the end of each line. Eliminate it...
    spoken_line = (spoken_line.split("\n"))[0]

    # Still a little bit of white space at the start and end.
    spoken_line = spoken_line.strip()

    # The webpage has an alphabet on it for navigation.  Since these letters are capital
    # letters, they've been captured by our method.  In these instances, the
    # `spoke_line` is empty. So if the spoken line is empty, don't count anything.
    if spoken_line == "":
        return None, None

    if debug:
        print(f"Character name {character_name}")
        print(f"Spoken line {spoken_line}")

    return character_name, spoken_line



def regex_season_one_episode_greater_one_line(line, debug=False):

    # Lines starting with "_" a scene descriptions.
    if line[0] == "-":
        return None, None

    # A line spoken by a character will start with "**Character name:**".
    # Be careful, sometimes the colon is inside the ** or outside with a space...

    # Search for "**<ANYTHING>:**" OR "**<ANYTHING>**:" OR **<ANYTHING>** :".
    # Here '[A-Z]' means we only match actual characters. This allows us to ignore
    # extraneous '****' at the start of some lines (e.g., one line is '**********Catelyn
    # Stark:** 17 years ago you rode off with Robert Baratheon...'
    reg_exp = re.compile(r"\*\*([A-Z].*)\:\*\*|\*\*([A-Z].*)\*\*\:|\*\*([A-Z].*)\*\* \:", re.IGNORECASE)
    character_line = reg_exp.split(line)  # Split on this search.

    if debug:
        print("Character Line {0}".format(character_line))

    # Now since we have defined 3 search times, a line spoken by a character will return a
    # list of the form...
    # ['', <CHARACTER_NAME OR NONE>, <CHARACTER_NAME OR NONE>, <CHARACTER_NAME OR NONE>, 'Actual line']
    # TWO ELEMENTS of character_line[1 or 2 or 3] will be None. The remaining one will be
    # not None.

    # Garbage lines will have length less than 5.
    if len(character_line) < 5:
        return None, None

    # Otherwise, let's filter out into a list that is [character_name, spoken_line].
    filtered_line = list(filter(None, character_line))

    # Actually sometimes extraneous "*...*" cause this filtered list to be 3 elements long,
    # ["*...*", character_name, spoke_line]. Check for this.
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

    # Now there is an annoying "\n" at the end of each line. Eliminate it...
    spoken_line = (spoken_line.split("\n"))[0]

    # Still a little bit of white space at the start and end.
    spoken_line = spoken_line.strip()

    return character_name, spoken_line
