from episode import Episode
from parse_script import parse_episode

import numpy as np
import matplotlib
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
        t.set_fontsize("medium")

    # For scatter plots, we want to increase the marker size.
    if scatter_plot:
        for handle in handles:
            # We may have lines in the legend which we don't want to touch here.
            if isinstance(handle, matplotlib.collections.PathCollection):
                handle.set_alpha(1.0)
                handle.set_sizes([10.0])


def plot_line_count_hist(season, plot_output_path, plot_output_format="png"):

    fig = plt.figure()
    ax = fig.add_subplot(111)

    characters = ["Tyrion", "Jon", "Robert"]
    for character_num, character in enumerate(characters):

        for episode in season:

            # Maybe the character didn't appear in this episode.
            try:
                character_lines = episode.characters[character].lines
            except KeyError:
                character_lines = []

            num_lines = len(character_lines)
            ax.scatter(episode.episode_num, num_lines, c=colors[character_num])

        ax.scatter(-50, -50, c=colors[character_num], label=character)

    ax.set_xlabel(r"$\mathbf{Episode \: Number}$")
    ax.set_ylabel(r"$\mathbf{Number \: Lines}$")

    ax.set_xlim([0.8, 11.2])
    ax.set_ylim([-1, 65])

    #ax.xaxis.set_minor_locator(plt.MultipleLocator(0.1))

    adjust_legend(ax, location="lower left", scatter_plot=True)

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
                character_lines = episode.characters[character].lines
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

    seasons = [1]
    episodes = np.arange(1, 11)
    debug=False
    season = []

    # Parse all the scripts in the Season.
    for season_num in seasons:
        for episode_num in tqdm(episodes):
            episode = Episode(season_num, episode_num)
            txt_file_path = f"/home/jseiler/screenplay-analysis/scripts/s{season_num:02}e{episode_num:02}.txt"


            parse_episode(txt_file_path, episode, debug=debug)

            #episode.summarise_episode()

            season.append(episode)

    # Then let's do some plotting!

    # This is a histogram of the number of lines said by the character across the Season.
    plot_line_count_hist(season, "./plots")

    # Wordcloud of the words said by characters.
    plot_wordcloud_character(season, "./plots")
