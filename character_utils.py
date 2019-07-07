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
