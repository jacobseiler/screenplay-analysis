import character_utils as c_utils
import episode_utils as e_utils
from character import Character
from episode import Episode
from parse_script import parse_all_eps

import matplotlib
import numpy as np
from matplotlib import pyplot as plt
from tqdm import tqdm

colors = ["r", "b", "g"]


def adjust_legend(ax, location="upper right", scatter_plot=False):
    """
    Adjusts the legend of a specified axis.

    Parameters
    ----------

    ax : ``matplotlib`` axes object
        The axis whose legend we're adjusting

    location : String, default "upper right". See ``matplotlib`` docs for full options
        Location for the legend to be placed.

    scatter_plot : Boolean, optional
        For plots involved scattered-plotted data, we adjust the size and alpha of the
        legend points.

    Returns
    -------

    None. The legend is placed directly onto the axis.
    """

    legend = ax.legend(loc=location)
    handles = legend.legendHandles

    legend.draw_frame(False)

    # First adjust the text sizes.
    for t in legend.get_texts():
        t.set_fontsize(40)

    # For scatter plots, we want to increase the marker size.
    if scatter_plot:
        for handle in handles:
            # We may have lines in the legend which we don't want to touch here.
            if isinstance(handle, matplotlib.collections.PathCollection):
                handle.set_alpha(1.0)
                handle.set_sizes([10.0])


def plot_line_count_hist(characters, episodes, plot_output_path,
                         characters_to_plot=None, plot_output_format="png"):

    if characters_to_plot is None:
        characters_to_plot = characters.keys()

    fig = plt.figure(figsize=(32, 16))
    ax = fig.add_subplot(111)

    bar_width = 1.0/len(characters_to_plot)
    max_lines = 0
    xticklabels = ["DUMMY"]  # For some reason, the 0th label doesn't appear...

    for character_num, character_name in enumerate(characters_to_plot):

        # Allows for easier indexing later.
        character_lines = characters[character_name].episode_lines

        for ep_count, episode in enumerate(episodes, start=1):

            key = episode.key

            # Don't spam the legend; only add a label if it's the first iteration.
            if ep_count == 1:
                label = character_name
            else:
                label = ""

            # Maybe the character didn't appear in this episode.
            try:
                lines_in_ep = len(character_lines[key])
            except KeyError:
                lines_in_ep = 0

            # Remember the maximum number of lines.
            if lines_in_ep > max_lines:
                max_lines = lines_in_ep

            # Position on the x-axis is shifted depending on how many characters we
            # have.
            x_pos = ep_count + bar_width*character_num

            ax.bar(x_pos, lines_in_ep, width=bar_width, label=label,
                color=colors[character_num])

            # Remember the episode numbers so we can add to the x-axis later.
            if character_num == 0:
                xticklabels.append(episode.episode_num)

    # The histogram has been made. Now let's go through and add some text to prettify.

    season_labels, num_eps_season = e_utils.determine_num_episodes_season(episodes)

    for season_idx in range(len(num_eps_season)):

        # Place a dotted line for reference to show the end of Season.
        # Need to know the total number of episodes before this season, so use cumsum.
        line_loc = np.cumsum(num_eps_season)[season_idx] + (bar_width*1.5)
        ax.axvline(line_loc, linestyle='--', linewidth=5)

        # Then place some text.
        text = season_labels[season_idx]

        # Want the text to be between two seasons.
        if season_idx == 0:
            x_loc = num_eps_season[season_idx] / 2.0
        else:
            x_loc = (np.cumsum(num_eps_season)[season_idx] + \
                np.cumsum(num_eps_season)[season_idx-1]) / 2.0
        # Shift slightly yo.
        x_loc -= 0.5

        if max_lines > 15:
            y_loc = max_lines - 10
        else:
            y_loc = 5

        ax.text(x_loc, y_loc, text, fontsize=20)

    ax.set_xlabel(r"$\mathbf{Episode \: Number}$", fontsize=40)
    ax.set_ylabel(r"$\mathbf{Number \: Lines}$", fontsize=40)

    ax.set_xlim([0.8, np.cumsum(num_eps_season)[-1] + 0.2])
    ax.set_ylim([0, max_lines+5])

    ax.xaxis.set_major_locator(plt.MultipleLocator(1))
    ax.set_xticklabels(xticklabels)

    adjust_legend(ax, location="upper left", scatter_plot=True)

    fig.tight_layout()

    output_file = "{0}/line_count.{1}".format(plot_output_path, plot_output_format)
    fig.savefig(output_file)
    print("Saved file to {0}".format(output_file))
    plt.close()


def plot_wordcloud_character(season, plot_output_path, plot_output_format="png"):

    from wordcloud import WordCloud, STOPWORDS

    stopwords = set(STOPWORDS)
    additional_stopwords = ["will"]
    for word in additional_stopwords:
        stopwords.add(word)

    characters = ["Tyrion", "Jon", "Robert"]
    for character_num, character in enumerate(characters):

        all_words = []
        fig = plt.figure()
        ax = fig.add_subplot(111)

        for episode in season:

            # Maybe the character didn't appear in this episode.
            try:
                character_lines = episode.character_lines[character]
            except KeyError:
                continue

            # Because `character_lines` is a list, we don't want to keep any nested
            # structure.
            all_words.extend(character_lines)

        # Join all the words into a single string.
        all_words = " ".join(all_words)


        wordcloud = WordCloud(stopwords=stopwords).generate(all_words)

        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis("off")

        output_file = f"{plot_output_path}/wordcloud_{character}.{plot_output_format}"
        fig.savefig(output_file)
        print(f"Saved file to {output_file}")
        plt.close()




if __name__ == "__main__":

    # Parse all the episodes we desire.
    season_nums = np.arange(1, 9)
    episode_nums = np.arange(1, 11)
    debug = False

    episodes = parse_all_eps(season_nums, episode_nums, debug)

    # Instead of breaking into episodes, can also distribute as characters.
    characters = c_utils.init_characters_in_episodes(episodes)
    c_utils.determine_lines_per_episode(episodes, characters)

    # Then let's do some plotting!

    # This is a histogram of the number of lines said by the character across the Season.
    characters_to_plot = ["Cersei", "Tyrion"]
    plot_line_count_hist(characters, episodes, "./plots", characters_to_plot)

    # Wordcloud of the words said by characters.
    plot_wordcloud_character(season, "./plots")
