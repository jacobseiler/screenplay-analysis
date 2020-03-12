"""
This module contains the ``Scene`` class.  The ``Scene`` class contains all the data associated with a single scene.
This information includes the lines that have been spoke, the name of each character that speaks during the scene, and
the season + episode number the scene belongs to.

Author: Jacob Seiler
"""

from typing import List


class Scene(object):

    def __init__(self, season_num: int, episode_num: int):

        self._lines: List[str] = []
        self._characters: List[str] = []

        self._season_num = season_num
        self._episode_num = episode_num

    @property
    def lines(self):
        """
        list of strings : The lines spoken by all characters during the scene.
        """
        return self._lines

    @lines.setter
    def lines(self, lines: List[str]):
        self._lines = lines

    @property
    def characters(self):
        """
        list of strings : Name of each character that talks in the scene.
        """
        # Go through each line in the scene, and then build a list of all the characters
        # that spoke.
        chars_in_scene = []

        for line in self.lines:
            chars_in_scene.append(line.character_name)

        # Enforce uniqueness.
        unique_chars = list(set(chars_in_scene))

        return unique_chars

    @characters.setter
    def characters(self, characters: List[str]):
        self._characters = characters

    @property
    def season_num(self):
        """
        int : The season number the scene belongs to.
        """
        return self._season_num

    @season_num.setter
    def season_num(self, season_num: int):
        self._season_num = season_num

    @property
    def episode_num(self):
        """
        int : The episode number the scene belongs to.
        """
        return self._episode_num

    @episode_num.setter
    def episode_num(self, episode_num: int):
        self._episode_num = episode_num

    def __repr__(self):

        my_string = f"s{self.season_num:02d}e{self.episode_num:02} scene"

        return my_string

    def __str__(self):

        my_string = f"Characters in Scene for Season {self.season_num} Episode " \
                    f"{self.episode_num} is {self.characters}. A total of {len(self.lines)} " \
                    f"lines were spoken."

        return my_string
