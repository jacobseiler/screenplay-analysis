from typing import Dict, List, Optional

from .character import Character


def init_characters_in_episodes(episodes):
    """
    Generate a dictionary of :py:class:`~Character` instances for characters appearing in
    the given episodes.

    Parameters
    ----------

    episodes : list of :py:class:`~Episode` instances
        Episodes that we are generating the characters for.

    Returns
    -------

    characters : dict["Character_Name", :py:class:`~Character` instance]
        Initialized character instances.  Key is the name of the character.
    """

    characters = {}

    # First determine the names of all characters across all episodes.
    character_names = []
    for episode in episodes:
        characters_in_episode = list(episode.character_lines.keys())
        character_names.extend(characters_in_episode)

    # Enforce uniqueness.
    character_names = set(character_names)

    # Now go through each character, initialize a class instance, and add to the dict.
    for character_name in character_names:
        character = Character(character_name)

        characters[character_name] = character

    return characters


def determine_lines_per_episode(episodes, characters):
    """
    Determines the number of lines spoken by each character in specified episodes.

    Parameters
    ----------

    episodes : List of :py:class:`~Episode` instances
        The episodes we're analysing.

    characters : List of :py:class:`~Character` instances
        Characters we're analysing.

    Returns
    -------

    None.  The values of :py:attr:`~Character.episode_lines` are updated directly.
    """

    for character_name in characters.keys():

        character = characters[character_name]
        for episode in episodes:

            # Check if this character was in this episode.
            try:
                lines_in_ep = episode.character_lines[character_name]
            except KeyError:
                continue

            key_name = f"s{episode.season_num:02}e{episode.episode_num:02}"
            character.episode_lines[key_name] = lines_in_ep


def determine_scene_interaction(episodes, characters, debug_name_one=None,
                                debug_name_two=None):
    """
    For given episodes and characters, determine the number of scenes that they appear together.

    Parameters
    ----------


    Returns
    -------

    None.  The values of :py:attr:`~Character.scene_appearance_dict` are updated directly.
    """

    # Go through each episode and add the characters in each scene to a dictionary.
    for episode in episodes:
        for scene_num, scene in enumerate(episode.scenes):

            # Then within each scene, we want to add all OTHER characters to that
            # character's appearance dict.
            for character_name in scene.characters:

                scene_dict = characters[character_name].scene_appearance_dict

                # Track how many scenes each character was in.
                characters[character_name].num_scenes += 1

                for other_character_name in scene.characters:

                    if character_name == debug_name_one and other_character_name == debug_name_two:
                        print(episode.scene_lines[scene_num])
                        print(f"{episode.season_num} {episode.episode_num}")

                    # Skip the i = j case.
                    if other_character_name == character_name:
                        continue

                    # Initialize the first time.
                    try:
                        scene_dict[other_character_name] += 1
                    except KeyError:
                        scene_dict[other_character_name] = 1


def determine_character_classes(
    characters: Dict[str, Character],
    main_char: bool = False,
    minor_char: bool = False,
) -> List[str]:
    """
    Given a dictionary of characters, fetches only the main/minor characters, depending who is specified.
    """

    main_characters = [
        "Daenerys", "Jon", "Arya", "Sansa", "Tyrion", "Bran", "Cersei",
        "Melisandre", "The Hound", "Joffrey", "Brienne", "Theon", "Jaime",
        "Bronn", "Ramsay", "Littlefinger", "Varys", "Jorah", "Margaery", "Sam",
        "Missandei", "Davos", "Ned", "Catelyn", "Tywin", "Robb", "Stannis", "Tormund"
    ]

    minor_characters = [
        "Qybyrn", "Grey Worm", "Pycelle", "Gilly", "Ygritte", "Gendry", "High Sparrow",
        "Oberyon", "Alliser", "Khal Drogo", "Renly", "Maester Aemon", "Podrick"
    ]

    characters_to_return = []

    if main_char:
        for character_name in main_characters:
            if character_name in characters.keys():
                characters_to_return.append(character_name)

    if minor_char:
        for character_name in minor_characters:
            if character_name in characters.keys():
                characters_to_return.append(character_name)

    return characters_to_return


# TODO: These should be ported into their own module and listed as "GoT_Names".
# This way the user can load the desired names to populate the list.
# Explicitly split into 'named_character' and 'NPC'?
def normalize_name(character_name: str, allowed_double_names: Optional[List[str]] = None) -> str:
    """
    Ensures consistency for a character's name.  For some scripts, "Jaime Lannister" is listed as "Jaime", "JAIME",
    etc.

    Parameters
    ----------

    character_name : string
        The original name of the character as it appears in the script.

    allowed_double_names : list of strings, optional
        Some characters are allowed to have two names (e.g., "The Hound").  This parameter specifies those names.  If
        ``None``, then uses the default values (see source code).

    Returns
    -------

    character_name : string
        The normalized name of the character.
    """

    import string
    # First be consistent and capitalize the first letter in all names of a character.
    # Use `capwords` rather than `title` because `title` capitalizes letters after
    # apostrophes.
    character_name = string.capwords(character_name)

    # There are only a handful of names we (by default) allow to be multiple words.
    if allowed_double_names is None:
        allowed_double_names = [
            "The Hound", "Khal Drogo", "Maester Luwin", "Septa Mordane",
            "Waymar", "Grand Maester Pycelle", "Maester Pycelle", "Street Urchin",
            "King's Landing Baker", "Hot Pie", "Ser Alliser",
            "Maryn Trant", "King Joffrey", "King's Landing Page",
            "Wine Merchant", "Stable Boy", "Old Nan", "Little Bird",
            "The Group", "The Others At The Table", "Gold Cloak", "Crowd",
            "Black Lorren", "The Mountain", "Pyatt Pree", "Eddison Tollett",
            "Kraznys Mo Nakloz", "Grey Worm", "Ser Dontos", "Dying Man", "Old Man",
            "Blone Prostitute", "Black Haired Prostitute", "Sand Snakes", "High Sparrow",
            "Slave Owner", "Night's Watchman", "Khal Moro", "Young Rodrik", "Young Ned",
            "Three-Eyed Raven", "Young Lyanna", "Young Hodor", "Lady Walda", "Lady Crane",
            "Maester Aemon", "Ser Vardis", "Maester Walkan", "Maester Pycelle",
            "High Septon", "Black Walder"
        ]

    # Populate a bunch of <House> <scout/warrior/guards>.
    houses = [
        "Lannister", "Stark", "Tyrell", "Baratheon", "Kings", "Nights Watch",
        "Kings Landing", "Wounded", "Frey"
    ]
    NPC_classes = ["Soldier", "soldier", "Scout", "Warrior", "Guards", "Bannerman", "Bannermen",
                   "Guard", "Boy"]
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
        "Three-eyed": "Three-Eyed Raven",
        "Three-Eyed": "Three-Eyed Raven",
        "Three": "Three-Eyed Raven",
        "Eddard": "Ned",
        "Samwell": "Sam",
        "Maester Aemon": "Aemon",
        "Royce": "Waymar",
        "Sandor": "The Hound",
        "Hound": "The Hound",
        "Luwin": "Maester Luwin",
        "Drogo": "Khal Drogo",
        "Grand Maester Pycelle": "Pycelle",
        "Maester Pycelle": "Pycelle",
        "King Joffrey": "Joffrey",
        "Samwell": "Sam",
        "Ser Alliser": "Alliser",
        "Baelish": "Littlefinger",
        "Petyr": "Littlefinger",
        "Mountain": "The Mountain",
        "Gregor": "The Mountain",
        "Sparrow": "High Sparrow",
        "Blackfish": "Brynden",
        "Twyin": "Tywin",  # Spelling lul.
        "Rodrick": "Rodrik",  # Spelling.
        "Oberyon": "Oberyn",
    }

    if character_name in name_map:
        character_name = name_map[character_name]

    return character_name


def determine_character_death(characters: Dict[str, Character]) -> Dict[str, Character]:
    """
    Determines when each character died and updates the :py:attr:`~Character.episode_death` attribute.
    """

    deaths = {
        "Daenerys": "s08e06",
        "The Mountain": "s08e05",
        "Cersei": "s08e05",
        "Melisandre": "s08e03",
        "The Hound": "s08e05",
        "Khal Drogo": "s01e10",
        "Joffrey": "s04e02",
        "Theon": "s08e03",
        "Jaime": "s08e05",
        "Ramsay": "s06e08",
        "Littlefinger": "s07e07",
        "Varys": "s08e05",
        "Jorah": "s08e03",
        "Margaery": "s06e10",
        "Missandei": "s08e04",
        "Ned": "s01e10",
        "Catelyn": "s03e09",
        "Tywin": "s04e09",
        "Robb": "s03e09",
        "Stannis": "s05e10",

        "Qybyrn": "s08e05",
        "Pycelle": "s06e10",
        "Ygritte": "s04e09",
        "High Sparrow": "s06e10",
        "Oberyn": "s04e08",
        "Alliser": "s06e03",
        "Renly": "s02e05",
        "Maester Aemon": "s05e07",
    }

    for character_name, character in characters.items():
        try:
            character._episode_death = deaths[character_name]
        except KeyError:
            character._episode_death = "alive"

    return characters
