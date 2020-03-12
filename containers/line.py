"""
This module contains the ``Line`` class.  The ``Line`` class contains all the data associated with a single line of
dialogue. This information includes the name of the character that spoke the line, the line itself, the subjectivity,
and the polarity of the line.  These last two properties are experimental and haven't been explore deeply.

Author: Jacob Seiler
"""

from containers.character_utils import normalize_name
from textblob import TextBlob


class Line(object):

    def __init__(self, character_name: str, spoken_line: str):

        self._character_name = character_name
        self._spoken_line = spoken_line

        sentiment = TextBlob(spoken_line).sentiment
        self._subjectivity = sentiment.subjectivity
        self._polarity = sentiment.polarity

    @property
    def character_name(self):
        """
        str : The name of the character speaking the line.  This has been normalized using
        :py:func:`~containers.character_utils.normalize_name`.
        """
        return self._character_name

    @character_name.setter
    def character_name(self, character_name):
        # Before we set the name, normalize it. This prevents weird instances of where a
        # character is called slightly different names across episodes (e.g., 'Jaime
        # Lannister' versus 'Jaime').
        character_name = normalize_name(character_name)

        self._character_name = character_name

    @property
    def spoken_line(self):
        """
        str : The line spoken by the character.
        """
        return self._spoken_line

    @spoken_line.setter
    def spoken_line(self, spoken_line):
        self._spoken_line = spoken_line

    @property
    def subjectivity(self):
        """
        float? : The subjectivity of the line. Experimental.
        """
        return self._subjectivity

    @property
    def polarity(self):
        """
        float? : The polarity of the line. Experimental.
        """
        return self._polarity

    def __repr__(self):
        """
        Sets the represenation of a line to simply be the line itself.
        """

        my_string = f"'{self.spoken_line}'; polarity:{self.polarity}; " \
                    f"subjectivity:{self.subjectivity}"
        return my_string
