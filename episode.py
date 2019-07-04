class Episode(object):

    def __init__(self, season_num, episode_num):

        self.season_num = season_num
        self.episode_num = episode_num
        self.characters = {}

    def summarise_episode(self):

        print("==============================")
        print(f"Summarizing Season {self.season_num} Episode {self.episode_num}")
        print("==============================")

        total_num_lines = 0
        for character in self.characters:
            num_lines_character = len(self.characters[character].lines)
            total_num_lines += num_lines_character

            print(f"{character} spoke {num_lines_character} lines")

        print(f"A total of {total_num_lines} lines were spoken.")

