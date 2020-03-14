"""
Functions to handle and investigate episodes.
"""

from typing import List

from containers.episode import Episode


def determine_num_episodes_season(episodes: List[Episode]):
    """
    Determine the number of episodes in each season from a list of episodes.
    """

    # Initial values..
    current_season = episodes[0].season_num
    num_episodes = 1
    season_labels = []
    num_episodes_season = []

    # Go through all the remaining episodes.
    for episode in episodes[1::]:

        # Are we on a new season?
        if episode.season_num != current_season:

            # If so, add the current totals to the list.
            season_labels.append(f"Season {current_season}")
            num_episodes_season.append(num_episodes)

            # Then re-initializze for next season.
            num_episodes = 1
            current_season = episode.season_num

        # Still in current season.
        else:
            num_episodes += 1

    # Remember to add the last one!
    season_labels.append(f"Season {current_season}")
    num_episodes_season.append(num_episodes)

    return season_labels, num_episodes_season
