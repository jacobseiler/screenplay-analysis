from containers.character import Character
from containers.episode import Episode
from containers.line import Line
from containers.scene import Scene

import re

import numpy as np
import pandas as pd

#TODO
# * Don't hard code the path for the scripts.


def parse_episode(fname, episode, debug=False):

    # There may be some episodes that don't have scripts yet.  Skip these and print a
    # warning.
    if episode.character_format == "NONE" and episode.scene_format == "NONE":
        print(f"Script has been flagged as not existing for s{episode.season_num:02}"
              f"e{episode.episode_num:02}. Skipping.")
        return

    # Start with a new scene.
    episode.current_scene = Scene(episode.season_num, episode.episode_num)

    with open(fname, "r") as f:

        # Strictly speaking I don't need to loop over lines here to get the character
        # lines. I could instead pass the entire file and use regex to pull out all the
        # character lines.  However, we want to pull out scenes
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

    # Add the final scene to the episode.
    episode.scenes.append(episode.current_scene)


def parse_character_line(line, episode, debug=False):

    if debug:
        print("Line {0}".format(line))

    # The format of the character line will change slightly depending upon the episode and
    # season.  Let's use a dedicated function to separate the line into the character name
    # and their spoken line.
    spoken_line = regex_character_line(line, episode, debug=debug)

    # A character didn't speak this line.
    if spoken_line is None:

        # However, it could be the case that we've hit a scene change.
        scene_change = determine_if_scene_change(line, episode, debug=debug)

        if scene_change:
            # If so, add all of lines to the list and reset the tracking.

            # Careful, maybe something happened and there weren't actually any lines added
            # to this scene yet.
            if len(episode.current_scene.lines) > 0:
                episode.scenes.append(episode.current_scene)

            episode.current_scene = Scene(episode.season_num, episode.episode_num)

        return

    # At this point, we have verified that a character spoke the line. Add some extra info
    # for further tracking.
    spoken_line.season_num = episode.season_num
    spoken_line.episode_num = episode.episode_num

    character_name = spoken_line.character_name

    # episode.character_line is a dict["character_name": list of Lines].
    # So let's check if we have already instantiated this character. If not, initialize.
    if character_name not in episode.character_lines:
        episode.character_lines[character_name] = []

    # Update the spoken line.
    episode.character_lines[character_name].append(spoken_line)

    # Update the scene this character spoke in.
    episode.current_scene.lines.append(spoken_line)

    if character_name == "King's":
        print(f"{episode.season_num} {episode.episode_num}")
        print(spoken_line.spoken_line)


def determine_if_scene_change(line, episode, debug=False):

    scene_change = False

    if episode.scene_format == "SCENE":
        if "Scene shift" in line or "Blackout" in line or "scene" in line.lower():
            scene_change = True
    elif episode.scene_format == "DASHES":
        if "\- - -" in line or "\---" in line:
            scene_change = True
    elif episode.scene_format == "STARS":
        if "* * *" in line or "***" in line:
            scene_change = True
    elif episode.scene_format == "INT/EXT":
        if "INT" in line or "EXT" in line or "Interior" in line or "Exterior" in line:
            scene_change = True
    elif episode.scene_format == "CUT":
        if "CUT TO" in line:
            scene_change = True
    elif episode.scene_format == "INT/EXT/CUT":
        if "INT" in line or "EXT" in line or "CUT TO" in line:
            scene_change = True

    return scene_change


def regex_character_line(line, episode, debug=False):

    # These are all scene descriptions.
    if line[0] == "[" or line[0] == "_" or "CUT TO" in line or "_CUT" in line \
                    or "INT" in line or "EXT" in line:
        return None

    if episode.character_format == "**CHARACTER_NAME:**":
        spoken_line = parse_stars_character_line(line, debug=debug)
    elif episode.character_format == "CHARACTER_NAME:":
        spoken_line = parse_capital_character_line(line, debug=debug)
    else:
        print(f"Character format for s{episode.season_num:02}e{episode.episode_num:02} "
              "is {episode.character_format}. This is not a recognised format.")
        raise ValueError


    return spoken_line


def parse_capital_character_line(line, debug=False):

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
        return None

    # The character name has an extra ":" at the end. Eliminate it.
    character_name = character_line[1][:-1]

    # Finally, strip any whitespace round the outside, round the outside.
    character_name = character_name.strip()

    # To be a valid line, all letters must be upper case.
    if character_name != character_name.upper():
        return None

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
        return None

    # At this point we're sure it was an actual line. So instantiate a Line instance and
    # return it.
    _line = Line(character_name, spoken_line)

    if debug:
        print(f"Character name {character_name}")
        print(f"Spoken line {spoken_line}")

    return _line



def parse_stars_character_line(line, debug=False):

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
        return None

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

    # At this point we're sure it was an actual line. So instantiate a Line instance and
    # return it.
    _line = Line(character_name, spoken_line)

    return _line


def parse_all_eps(season_nums, episode_nums, debug=False):

    episodes = []

    # Each episode can be parsed slightly differently. This pandas dataframe will provide
    # the keys used to determine how to parse each episode.
    formats = pd.read_csv("./formats.txt", sep=" ", comment="#")

    for season_num in season_nums:
        for episode_num in episode_nums:

            # Need the formats on how we parse the characters and scenes.
            episode_format = formats[(formats["season_num"] == season_num) & \
                                        (formats["episode_num"] == episode_num)]

            # Some seasons don't have episodes 1-10. So try this and skip if we don't
            # have.
            try:
                character_format = str(episode_format["character_format"].values[0])
                scene_format = str(episode_format["scene_format"].values[0])
            except IndexError:
                continue

            key = f"s{season_num:02}e{episode_num:02}"
            script_path = f"./script_tools/scripts/{key}.txt"

            episode = Episode(season_num, episode_num, key, script_path)

            episode.character_format = character_format
            episode.scene_format = scene_format

            episodes.append(episode)

    # Now go through each episode and parse the script.
    for episode in episodes:
        parse_episode(episode.script_path, episode, debug)

    return episodes
