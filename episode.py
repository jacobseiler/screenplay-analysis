class Episode(object):

    def __init__(self, season_num, episode_num):

        self._season_num = season_num
        self._episode_num = episode_num
        self._character_lines = {}

    @property
    def season_num(self):
        return self._season_num

    @season_num.setter
    def season_num(self, season_num):
        self._season_num = season_num

    @property
    def episode_num(self):
        return self._episode_num

    @episode_num.setter
    def episode_num(self, episode_num):
        self._episode_num = episode_num

    @property
    def character_lines(self):
        return self._character_lines

    @character_lines.setter
    def character_lines(self, character_lines):
        return self._character_lines


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
