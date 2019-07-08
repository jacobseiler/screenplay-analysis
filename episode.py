class Episode(object):

    def __init__(self, season_num, episode_num, key, script_path):

        self._season_num = season_num
        self._episode_num = episode_num
        self._character_lines = {}
        self._key = key
        self._script_path = script_path

        self._scene_lines = []
        self._scene_characters = []

        self._characters_spoken_in_scene = []
        self._lines_spoken_in_scene = []

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

    @property
    def character_format(self):
        return self._character_format

    @character_format.setter
    def character_format(self, character_format):
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
    def scene_lines(self):
        return self._scene_lines

    @scene_lines.setter
    def scene_lines(self, scene_lines):
        self._scene_lines = scene_lines

    @property
    def scene_characters(self):
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
