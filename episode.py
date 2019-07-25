#!/usr/bin/env python
"""
This module contains the ``Episode`` class.  The ``Episode`` class contains all the
data associated with a single episode.

Several functions have been written to interface with lists of ``Episode`` class instances and can be
found in ``episode_utils.py``.

Author: Jacob Seiler.
"""

class Episode(object):
    """
    Handles all of the data associated with single episode.
    """

    def __init__(self, season_num, episode_num, key, script_path):
        """
        Sets empty lists, dictionaries and information about the episode.

        Parameters
        ----------

        season_num, episode_num: ints
            The season and episode numbers of this episode.

        key: string
            A unique key for this episode. Used by indivual :py:class:`~Character` class
            instances to track the lines spoken in each episode.

        script_path: string
            Path to where the script of this episode is stored. Used to read and parse the
            lines/scenes for the episode.
        """

        self._season_num = season_num
        self._episode_num = episode_num
        self._character_lines = {}
        self._key = key
        self._script_path = script_path

        self.scenes = []

        self._scene_lines = []
        self._scene_characters = []

        # When we parse individual scenes, we add the lines to expanding
        # lists.  When we hit a scene change, these temporary lists are added to
        # `_scene_lines`.
        self._tmp_scene_lines = []

    @property
    def season_num(self):
        """
        int: The season number.
        """
        return self._season_num

    @season_num.setter
    def season_num(self, season_num):
        self._season_num = season_num

    @property
    def episode_num(self):
        """
        int: The episode number.
        """
        return self._episode_num

    @episode_num.setter
    def episode_num(self, episode_num):
        self._episode_num = episode_num

    @property
    def character_lines(self):
        """
        dict[string, list of strings]: Dictionary containing a list of lines spoken by
        each character. Key is the name of the character and the value are all lines
        spoken by that character in this episode.
        """
        return self._character_lines

    @character_lines.setter
    def character_lines(self, character_lines):
        return self._character_lines

    @property
    def character_format(self):
        """
        string: Key that specifies how each character line is identified in the script.
        Used to apply a regular expression across the script to extract the lines spoken
        by each character.

        Possible Values
        ---------------
        "CHARACTER_NAME:" corresponds to the lines of the script being "CHARACTER NAME: <Spoken Line>"

        "**CHARACTER_NAME:**" corresponds to the lines of the script being "**CHARACTER NAME:** <Spoken Line>"
        """
        return self._character_format

    @character_format.setter
    def character_format(self, character_format):

        allowed_formats = ["CHARACTER_NAME:", "**CHARACTER_NAME:**", "NONE"]
        if character_format not in allowed_formats:
            print(f"The format for parsing the characters for episode {self.key} was "
                  f"specified as {character_format}. The only allowed formats are "
                  f"{allowed_formats}")
            raise ValueError

        self._character_format = character_format

    @property
    def scene_format(self):
        return self._scene_format

    @scene_format.setter
    def scene_format(self, scene_format):
        self._scene_format = scene_format

    @property
    def key(self):
        return self._key

    @property
    def script_path(self):
        return self._script_path

    @property
    def scenes(self):
        """
        list of :py:class`~Scene` instances: The scenes in this episode.
        """
        return self._scenes

    @scenes.setter
    def scenes(self, scenes):
        self._scenes = scenes

    @property
    def scene_lines(self):
        """
        list of lists of :py:class:`~Line` instances: For each scene within the episode,
        contains a list of :py:class:`~Line` instances for all lines in that scene.
        """
        return self._scene_lines

    @scene_lines.setter
    def scene_lines(self, scene_lines):
        self._scene_lines = scene_lines

    @property
    def scene_characters(self):
        """
        list of list of strings: For each scene within the episode, contains a list of
        character in that scene.
        """
        return self._scene_characters

    @scene_characters.setter
    def scene_characters(self, scene_characters):
        self._scene_characters = scene_characters



    def summarise_episode(self, verbose=False):

        print("")
        print("==============================")
        print(f"Summarizing Season {self.season_num} Episode {self.episode_num}")
        print("==============================")

        total_num_lines = 0
        for character in self.characters:
            num_lines_character = len(self.character_lines[character])
            total_num_lines += num_lines_character

            print(f"{character} spoke {num_lines_character} lines")

            if verbose:
                print(f"{self.character_lines[character]}")

        print(f"A total of {total_num_lines} lines were spoken.")
        print("")
