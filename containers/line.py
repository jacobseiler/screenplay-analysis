from .character_utils import normalize_name

from textblob import TextBlob


class Line(object):

    def __init__(self, character_name, spoken_line):

        self.character_name = character_name
        self._spoken_line = spoken_line

        sentiment = TextBlob(spoken_line).sentiment
        self._subjectivity = sentiment.subjectivity
        self._polarity = sentiment.polarity

    @property
    def character_name(self):
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
        return self._spoken_line

    @spoken_line.setter
    def spoken_line(self, spoken_line):
        self._spoken_line = spoken_line

    @property
    def subjectivity(self):
        return self._subjectivity

    @property
    def polarity(self):
        return self._polarity

    def __repr__(self):
        """
        Sets the represenation of a line to simply be the line itself.
        """

        my_string = f"'{self.spoken_line}'; polarity:{self.polarity}; " \
                    f"subjectivity:{self.subjectivity}"
        return my_string
