from character import Character


def init_characters_in_episodes(episodes):
    """
    Generate a dictionary of :py:class:`~Character` instances for characters appearing in
    the given episodes.

    Parameters
    ----------

    episodes: List of :py:class:`~Episode` instances
        Episodes that we are generating the characters for.

    Returns
    -------

    characters: dict["Character_Name", :py:class:`~Character` instance]
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

    # For each character, add their lines from each episode.
    for character_name in characters.keys():

        character = characters[character_name]

        for episode in episodes:

            # Check if this character was in this episode. If not, move to the next
            # episode.
            try:
                lines_in_ep = episode.character_lines[character_name]
            except KeyError:
                continue


            # Add these lines to a dictionary.
            key_name = f"s{episode.season_num:02}e{episode.episode_num:02}"
            character.episode_lines[key_name] = lines_in_ep


def determine_scene_interaction(episodes, characters, debug_name_one=None,
                                debug_name_two=None):

    # Go through each episode and add the characters in each scene to a dictionary.
    for episode in episodes:

        # episode.scene_characters is a list of lists. So go through each scene.
        for scene_num, scene in enumerate(episode.scene_characters):

            # Then within each scene, we want to add all OTHER characters to that
            # character's appearance dict.
            for character_name in scene:

                scene_dict = characters[character_name].scene_appearance_dict

                for other_character_name in scene:

                    if character_name == debug_name_one and \
                        other_character_name == debug_name_two:
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



def determine_character_classes(characters, main_char=False, minor_char=False,
                                extras=False):

    main_characters = [
        "Daenerys", "Jon", "Arya", "Sansa", "The Mountain", "Tyrion", "Bran", "Cersei",
        "Melisandre", "The Hound", "Khal Drogo", "Joffrey", "Brienne", "Theon", "Jaime",
        "Bronn", "Ramsay", "Littlefinger", "Varys", "Jorah", "Margaery", "Sam",
        "Missandei", "Davos", "Ned", "Catelyn", "Tywin", "Robb", "Bronn", "Stannis",
        "Tormund"
    ]

    minor_characters = [
        "Qybyrn", "Grey Worm", "Pycelle", "Gilly", "Ygritte", "Gendry", "High Sparrow",
        "Oberyon", "Alliser", "Khal Drogo", "Renly", "Maester Aemon"]

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
