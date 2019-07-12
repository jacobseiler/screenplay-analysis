#!/usr/bin/env python
"""
This module contains the ``Character`` class.  The ``Character`` class contains all the
data associated with an individual character.

Several functions have been written to interface with lists of ``Character`` classes and can be
found in ``character_utils.py``.

Author: Jacob Seiler.
"""

class Character(object):
    """
    Handles all of the data associated with an individual character.
    """

    def __init__(self, name):
        """
        Initialize empty lists and dictionaries.

        Parameters
        ----------

        name: string
            The name of the character being initialized.
        """

        self._name = name
        self._episode_lines = {}
        self._unique_words = []
        self._scene_appearance_dict = {}


    @property
    def name(self):
        """
        string: Name of the character.
        """
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def episode_lines(self):
        """
        dict[string, list of strings]: The lines spoken by the character in each episode.
        Key is "s{season_num}e{episode_num}" and the values are a list of lines spoken by
        the character in the episode.

        Episodes where the character do not speak are **not** initialize. These instances
        should be caught with a ``try: except KeyError:`` statement.
        """
        return self._episode_lines

    @episode_lines.setter
    def episode_lines(self, episode_lines):
        self._episode_lines = episode_lines

    @property
        """
        TODO: Update this when I actually use it...
        """
    def unique_words(self):
        return self._unique_words

    @unique_words.setter
    def unique_words(self, unique_words):
        self._unique_words = unique_words

    @property
    def scene_appearance_dict(self):
        """
        dict[string, int]: Number of times this character speaks in the same scene as
        another character.  Key is the name of the other character.
        """
        return self._scene_appearance_dict

    @scene_appearance_dict.setter
    def scene_appearance_dict(self, appearance_dict):
        self._scene_appearance_dict = appearance_dict


    def calc_unique_words(self):

        from collections import Counter

        count = Counter()

        # For each episode, the spoken lines are kept in a list...
        # [line0, line1, line2, ..., lineN].
        for episode in self._episode_lines.keys():

            for line in self._episode_lines[episode]:
                for word in line.split():
                    count[word] += 1
