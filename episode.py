class Episode(object):

    def __init__(self, season_num, episode_num):

        self.season_num = season_num
        self.episode_num = episode_num
        self.character_lines = {}


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
