class Character(object):

    def __init__(self, name):

        self._name = name
        self._episode_lines = {}
        self._unique_words = []


    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def episode_lines(self):
        return self._episode_lines

    @episode_lines.setter
    def episode_lines(self, episode_lines):
        self._episode_lines = episode_lines

    @property
    def unique_words(self):
        return self._unique_words

    @unique_words.setter
    def unique_words(self, unique_words):
        self._unique_words = unique_words

    def calc_unique_words(self):

        from collections import Counter

        count = Counter()

        # For each episode, the spoken lines are kept in a list...
        # [line0, line1, line2, ..., lineN].
        for episode in self._episode_lines.keys():

            for line in self._episode_lines[episode]:
                for word in line.split():
                    count[word] += 1
