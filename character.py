class Character(object):

    def __init__(self, name):

        self._name = name
        self._episode_lines = {}
        self._unique_words = []


    @property
    def name(self):
        return self._name

    @property
    def episode_lines(self):
        return self._episode_lines

    @property
    def unique_words(self):
        return self._unique_words


    def calc_lines_in_episodes(self, episodes):

        for episode in episodes:

            # Check if this character was in this episode. If not, move to the next
            # episode.
            try:
                lines_in_ep = episode.character_lines[self._name]
            except KeyError:
                continue

            # Add these lines to a dictionary.
            key_name = f"s{episode.season_num:02}e{episode.episode_num:02}"
            self._episode_lines[key_name] = lines_in_ep


    def calc_unique_words(self):

        from collections import Counter

        count = Counter()

        # For each episode, the spoken lines are kept in a list...
        # [line0, line1, line2, ..., lineN].
        for episode in self._episode_lines.keys():

            for line in self._episode_lines[episode]:
                for word in line.split():
                    count[word] += 1
