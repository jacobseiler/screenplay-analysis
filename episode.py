class Episode(object):

    def __init__(self, season, episode_number):

        self.season = season
        self.episode_number = episode_number
        self.characters = {}

    def summarise_episode(self):

        print("==============================")
        print(f"Summarizing Season {self.season} Episode {self.episode_number}")
        print("==============================")

        for character in self.characters:
            print(f"{character} spoke {len(self.characters[character].lines)} lines")

