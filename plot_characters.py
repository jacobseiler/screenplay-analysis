import math
import os
from typing import Dict, List, Optional

import matplotlib
import matplotlib.patheffects as PathEffects
import networkx as nx
import numpy as np
from matplotlib import pyplot as plt
from tqdm import tqdm

import containers.character_utils as c_utils
import containers.episode_utils as e_utils
from containers.character import Character
from containers.episode import Episode
from script_tools.parse_script import parse_all_eps
from wordcloud import STOPWORDS, WordCloud

colors = ["r", "b", "g", "c", "m"]


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


def plot_line_count_hist(
    characters: Dict[str, Character],
    episodes: List[Episode],
    characters_to_plot: Optional[List[str]] = None,
    plot_output_path: str = "./plots",
    plot_output_format: str = ".png"
):
    """
    Plots the number of lines spoken by the characters as a function of
    episode.

    Parameters
    ----------
    characters
        The information related to all the characters analysed.  May contain
        characters that will not be plotted, as specified by
        ``characters_to_plot``.  Keys are the character's name.

    episodes
        The information related to all the episodes that will be plotted.

    characters_to_plot : optional, list of str
        Specifies which characters are to be plotted.  Shouldn't be too many,
        otherwise the plot will look yucky.  If not specified, will use the
        keys of ``characters``; however if this list is greater than 3
        characters, will default to ``["Tyrion", "Jon", "Daenerys"]``.

    plot_output_path : optional, str
        The base path where the plot will be saved.

    plot_output_format : optional, str
        The format the plot is saved as.

    TODO
    ----
    I think this should be changed to like a stacked hist. Maybe this would
    require is to be a cumulative plot.
    """

    if characters_to_plot is None:
        characters_to_plot = characters.keys()

        if len(characters_to_plot) > 5:
            print(
                "Number of characters in the ``characters`` dictionary is "
                "too large.  Defaulting to only plotting 3 characters."
            )
            print("Specify ``characters_to_plot`` directly when calling to override.")
            characters_to_plot = ["Tyrion", "Jon", "Daenerys"]

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

            ax.bar(
                x_pos,
                lines_in_ep,
                width=bar_width,
                label=label,
                color=colors[character_num]
            )

            # Remember the episode numbers so we can add to the x-axis later.
            if character_num == 0:
                xticklabels.append(episode.episode_num)

    # The histogram has been made. Now let's go through and add some text to prettify.
    season_labels, num_eps_season = e_utils.determine_num_episodes_season(episodes)

    for season_idx in range(len(num_eps_season)):

        # Place a dotted line for reference to show the end of Season.
        # Need to know the total number of episodes before this season, so use cumsum.
        line_loc = np.cumsum(num_eps_season)[season_idx] + (bar_width*2.5)
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
        x_loc -= 0.9

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
    ax.set_xticklabels(xticklabels, fontsize=30)

    ax.yaxis.set_major_locator(plt.MultipleLocator(10))
    ax.set_yticklabels(np.arange(-10, max_lines+5, 10), fontsize=30)

    adjust_legend(ax, location="upper left", scatter_plot=True)
    fig.tight_layout()

    output_file = "{0}/line_count{1}".format(plot_output_path, plot_output_format)
    fig.savefig(output_file)
    print("Saved file to {0}".format(output_file))
    plt.close()


def plot_wordcloud_character(episodes, plot_output_path, plot_output_format="png"):

    stopwords = set(STOPWORDS)
    additional_stopwords = ["will"]
    for word in additional_stopwords:
        stopwords.add(word)

    characters = ["Tyrion", "Jon", "Robert"]
    for character_num, character in enumerate(characters):

        all_words = []
        fig = plt.figure()
        ax = fig.add_subplot(111)

        for episode in episodes:

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


def plot_scene_network_graph(
    characters: Dict[str, Character],
    episodes: List[Episode],
    output_fname: str,
    characters_to_plot: List[str] = None,
    plot_method: str = "networkx",
    pos: Optional[Dict[str, np.array]] = None,
) -> Dict[str, np.array]:
    """
    Plots a graph showing how characters interact with each other.

    Parameters
    ----------

    characters : dict with keys of character name and values of :py:class:`~containers.Character:` instances
        Characters where the :py:attr:`~Character.scene_appearance_dict` attribute has been updated (generally through
        :py:func:`~generate_scene_interactions_for_graph`).

    episodes : list of :py:class:`~containers.Episode` instances
        The episodes that are being plotted.

    output_fname : string
        The name of the file being saved

    characters_to_plot : list of strings, optional
        Specifies the names of characters to plot.  If not specified, will plot all characters in ``characters``.

    plot_method : {"networkx", "bokeh"}
        Specifies whether to plot a static graph using Networkx ("networkx") or an interactive one using Bokeh
        ("bokeh").  The "bokeh" option has not been developed in a long time.

    pos : dict with keys of character name and values of an array of ``[x,y]`` coordinate pairs
        The coordinates of each character node.  If not specified, then the positions will be generated using
        ``networkx.spring_layout``.

    Returns
    -------

    pos : dict with keys of character name and values of an array of ``[x,y]`` coordinate pairs
        The coordinates of each character node.
    """

    allowed_plot_methods = ["networkx", "bokeh"]
    if plot_method not in allowed_plot_methods:
        print(f"Selected plot_method for the scene network graph is {plot_method}. "
              f"The only allowed methods are {allowed_plot_methods}")
        raise ValueError

    characters = c_utils.determine_character_death(characters)

    episode_keys = [episode.key for episode in episodes]

    if plot_method == "bokeh":
        from bokeh.io import save, output_file
        from bokeh.models import Plot, Range1d, MultiLine, Circle, HoverTool, BoxZoomTool, ResetTool, TapTool, PanTool
        from bokeh.models.graphs import from_networkx, EdgesAndLinkedNodes
        from bokeh.palettes import Spectral4

    if characters_to_plot is None:
        characters_to_plot = characters.keys()

    G = nx.Graph()

    # When we calculate weights or sizes, we want to normalize by the total number of
    # scenes across all episodes.
    tot_num_scenes = 0
    for episode in episodes:
        tot_num_scenes += episode.num_scenes

    # Now for each character, the weight of the edges will be scaled by the number of
    # times they appear with the other character.
    node_size = {}
    for character_name in characters_to_plot:

        G.add_node(character_name)
        node_size[character_name] = (characters[character_name].num_scenes / \
                                        tot_num_scenes*10000 * np.sqrt(len(episodes)))

        if characters[character_name].num_scenes > 0:
            node_size[character_name] += 1000

        appearance_dict = characters[character_name].scene_appearance_dict
        for other_character_name in appearance_dict.keys():

            # Only consider those characters in the plotting list.
            if other_character_name not in characters_to_plot:
                continue

            # Character A and B appear in scenes with other characters. So let's weight
            # the edges by the fraction of scenes A&B appear together, relative to the
            # other characters they appear with.
            A_in_B = appearance_dict[other_character_name]
            num_scenes_A = characters[character_name].num_scenes
            num_scenes_B = characters[other_character_name].num_scenes

            frac_scenes_A = characters[character_name].num_scenes / tot_num_scenes
            frac_scenes_B = characters[other_character_name].num_scenes / tot_num_scenes

            if num_scenes_A == 0 or num_scenes_B == 0:
                continue

            weight = A_in_B / (num_scenes_A * num_scenes_B) / tot_num_scenes

            weight *= 250 * math.pow(len(episodes), 1.9)

            if weight > 10:
                weight = 10

            # print(f"{character_name} -> {other_character_name}: {weight}")
            # print(f"{character_name} -> {other_character_name}: {weight/tot_num_scenes}")

            G.add_edge(character_name, other_character_name,
                       weight=weight)

    # If we're plotting using solely networkx, it uses an MPL axis.
    if plot_method == "networkx":
        fig = plt.figure(figsize=(20,20))
        ax = fig.add_subplot(111)

        # We first now draw all the nodes (i.e., characters) and their labels.
        if not pos:
            pos = nx.spring_layout(G)

        # We need to ensure that all the nodes have the correct sizes. Use the ordering of
        # the nodes that's used to plot.
        node_size_list = []
        for character_name in G.nodes():
            node_size_list.append(node_size[character_name])

        # If character has died by the last episode we're plotting, then display their node in different color.
        node_colors = [
            "#fdae6b" if characters[character_name].episode_death in episode_keys else "#3182bd"
            for character_name in G.nodes()
        ]

        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_size_list, ax=ax)

        # For each character, we want the size of their label to be relative to the size of
        # their node.
        label_size_list = []

        print(node_size_list)
        valid_nodes = np.where(np.array(node_size_list) > 0)[0]
        print(valid_nodes)
        min_node_size = min(np.array(node_size_list)[valid_nodes]) + 100
        max_node_size = max(node_size_list) + 100

        label_size_bins = np.logspace(np.log10(min_node_size), np.log10(max_node_size), num=7)
        label_size_binned = np.digitize(node_size_list, label_size_bins)

        for char_num, character_name in enumerate(G.nodes()):
            labels = {}
            labels[character_name] = character_name

            # Only print labels for non-zero sized nodes.
            if node_size_list[char_num] > 0:
                bbox_dict = dict(fc="grey", alpha=0.75)
                nx.draw_networkx_labels(G, pos, labels, font_size=12 + label_size_binned[char_num],
                                        font_color="white", ax=ax, bbox=bbox_dict)

    # Otherwise, need a specific Bokeh axis.
    elif plot_method == "bokeh":
        plot = Plot(plot_width=400, plot_height=400, x_range=Range1d(-2.1,2.1),
                    y_range=Range1d(-2.1,2.1))

    # We now want to go through each edge, and build an edge attributes dictionary and a
    # list of unique weights.  Furthermore, for the Bokeh plot, we want to add extra
    # attributes to each node that we will show on Hover/etc
    edge_attrs = {}
    all_weights = []
    for (node1, node2, data) in G.edges(data=True):
        edge_attrs[(node1, node2)] = data["weight"]
        all_weights.append(data["weight"])

        if plot_method == "bokeh":
            G.nodes[node1]["name"] = node1
            G.nodes[node2]["name"] = node2

    # Explicitly set these weights (needed for Bokeh referencing later).
    nx.set_edge_attributes(G, edge_attrs, "weight")
    unique_weights = list(set(all_weights))

    # If we're only plotting with networkx, go through and manually plot.
    if plot_method == "networkx":
        for weight in unique_weights:

            weighted_edges = [(node1,node2) for (node1,node2,edge_attr) in G.edges(data=True) \
                                if edge_attr['weight']==weight]

            width = weight
            nx.draw_networkx_edges(G, pos, edgelist=weighted_edges, width=width,
                                   edge_color="#D3D3D3", ax=ax)

        fig.tight_layout()

        ax.set_facecolor('k')
        ax.text(0.7, 0.9, f"{episode_keys[-1]}", color="w", size=75, transform=ax.transAxes)
        fig.savefig(output_fname)
        print(f"Saved to {output_fname}")
        plt.close()

    # Otherwise, need to get fancy.
    elif plot_method == "bokeh":

        # Convert the networkx Graph to a bokeh renderer.
        graph_renderer = from_networkx(G, nx.spring_layout, scale=2, center=(0,0))

        # Add a hover tool to show the character name.
        node_hover_tool = HoverTool(tooltips=[("Character", "@name")])
        plot.add_tools(node_hover_tool, PanTool(), TapTool(), BoxZoomTool(), ResetTool())

        # Draw the nodes as circles.
        graph_renderer.node_renderer.glyph = Circle(size=15, fill_color=Spectral4[0])
        graph_renderer.node_renderer.selection_glyph = Circle(size=15, fill_color=Spectral4[2])

        # First draw the edges in grey.
        graph_renderer.edge_renderer.glyph = MultiLine(line_color="#CCCCCC",
                                                       line_alpha=0.8, line_width="weight")

        # Then on selected, show the edges weighted by the previously defined values based on
        # the relative scene appearances.
        graph_renderer.edge_renderer.selection_glyph = MultiLine(line_color=Spectral4[2],
                                                       line_alpha=0.8, line_width="weight")

        graph_renderer.selection_policy = EdgesAndLinkedNodes()

        plot.renderers.append(graph_renderer)

        output_file(output_fname)
        save(plot)

        print(f"Saved file to {output_fname}")

    return pos


def plot_cumulative_scene_network_graphs(
    episodes: List[Episode],
    plot_output_dir: str = "./",
    plot_main_char: bool = True,
    plot_minor_char: bool = False,
    chars_to_remove: Optional[List[str]] = None,
    name_for_ffmpeg: bool = False,
    plot_method: str = "bokeh",
) -> None:
    """
    Given N episodes, plots N graphs depicting the number of interactions between characters.  That is, if passed 3
    episodes, plots a graph of interactions for episodes {1, 2, 3}, {1, 2}, and {1].

    Importantly, the position of the nodes (i.e., characters) are defined for the first iteration (i.e., using ALL
    episodes) and then reused for all others.

    Parameters
    ----------

    episodes : list of :py:class:`~containers.Episode:` class instances
        The episodes that we're plotting interactions for.

    plot_output_dir : optional, str
        Directory where the plots will be saved.

    plot_main_char : optional, bool
        If specified, will generate (and plot) interactions for main characters.  Main characters are defined in
        :py:func:`~character_utils.determine_character_classes`.

    plot_minor_char : optional, bool
        If specified, will generate (and plot) interactions for minor characters.  Minor characters are defined in
        :py:func:`~character_utils.determine_character_classes`.

    chars_to_remove : optional, list of strings
        Removes the specified characters from analysis.

    name_for_ffmpeg : optional
        If specified, then the names of the images will be adjusted to be in sequential numerical order rather than
        ``sXXeXX.png``.

    Saves
    -----

    Saves all of the interaction graphs as ``{plot_output_dir}/scene_graph_{episode_key}.png` where ``episode_key`` is
    the key of the episode (e.g., ``s01e02``, ``s04e05``, etc).
    """

    # First, let's create a network graph using ALL episodes. From this, we will fix the
    # position of the nodes (characters) and use those same positions for all future
    # plots.
    characters = generate_scene_interactions_for_graph(
            episodes, plot_main_char, plot_minor_char, chars_to_remove
    )

    # Now plot the network graph and remember the positions.
    final_episode_key = episodes[-1].key

    file_extensions: Dict[str, str] = {"networkx": "png", "bokeh": "html"}
    file_extension: str = file_extensions[plot_method]

    if name_for_ffmpeg:
        output_fname = f"{plot_output_dir}/scene_graph_{len(episodes)}.{file_extension}"
    else:
        output_fname = f"{plot_output_dir}/scene_graph_{final_episode_key}.{file_extension}"
    node_pos = plot_scene_network_graph(
        characters, episodes, output_fname, plot_method=plot_method, pos=None
    )
    exit()

    # When plotting the other episodes, we will want to plot ALL characters, regardless of
    # if they appear in the episodes. For characters we don't appear, their node/edge size
    # will be 0, but still included to keep the sizing of the graph correct.
    all_characters = characters

    # Ok we have all the positions. Now iterate cumulatively through all the episodes and
    # do a plot.
    for episode_idx in range(len(episodes) - 1):
        these_episodes = episodes[0:episode_idx+1]

        characters = generate_scene_interactions_for_graph(
            these_episodes,
            plot_main_char,
            plot_minor_char,
            chars_to_remove
        )

        # For those characters that don't appear in the episode (but appear by final
        # episode plotted), add them to the ``characters`` dict with zeroed values.
        for character_name in all_characters:
            if character_name not in characters.keys():
                characters[character_name] = Character(character_name)

        # Now plot the network graph.
        final_episode_key = these_episodes[-1].key
        if name_for_ffmpeg:
            output_fname = f"{plot_output_dir}/scene_graph_{len(these_episodes)}.png"
        else:
            output_fname = f"{plot_output_dir}/scene_graph_{final_episode_key}.png"
        _ = plot_scene_network_graph(
            characters, these_episodes, output_fname, plot_method="networkx", pos=node_pos
        )


def generate_scene_interactions_for_graph(
    episodes: List[Episode],
    use_main_char: bool = True,
    use_minor_char: bool = False,
    chars_to_remove: Optional[List[str]] = None
) -> Dict[str, Character]:
    """
    Generates the number of scene interactions between characters.  This is the number of times that each character
    appears in a scene with each other character.

    Parameters
    ----------

    episodes : list of :py:class:`~containers.Episode:` class instances
        The episodes that we're plotting interactions for.

    use_main_char, use_minor_char : optional, bool
        If specified, will generate interactions for main and minor characters characters.  Characters "classes" are
        defined in :py:func:`~character_utils.determine_character_classes`.

    chars_to_remove : optional, list of strings
        Removes the specified characters from analysis.

    Returns
    -------

    characters_to_return : dict with keys of character name and values of :py:class:`~containers.Character:` instances
        Character information for characters of the specified classes (main/minor). These character instances include
        the :py:attr:`~Character.scene_appearance_dict` attribute updated.
    """

    if not chars_to_remove:
        chars_to_remove = []

    characters = c_utils.init_characters_in_episodes(episodes)

    # Determine the scene interactions for all characters.
    c_utils.determine_scene_interaction(episodes, characters)

    # Then determine those characters that we want to plot.
    characters_to_plot = c_utils.determine_character_classes(
        characters, use_main_char, use_minor_char
    )

    # Want to return only those characters asked for. Can't hash a list so have to iterate
    # manually.
    characters_to_return = {
        character_name: characters[character_name]
        for character_name in characters_to_plot if character_name not in chars_to_remove
    }

    return characters_to_return


if __name__ == "__main__":

    output_dir = "./cumu_plots"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_dir = "./plots"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Parse all the episodes we desire.
    season_nums = np.arange(1, 9)
    episode_nums = np.arange(1, 11)
    debug = False

    episodes = parse_all_eps(season_nums, episode_nums, debug)

    # Build a network graph of the scene interactions for each cumulative episode. That
    # is, create a graph that is s01e01, s01e01 + s01e02, s01e01 + s01e02 + s01e03, etc.
    plot_cumulative_scene_network_graphs(
        episodes,
        "./cumu_plots",
        plot_main_char=True,
        plot_minor_char=True,
        name_for_ffmpeg=True
    )

    # Instead of breaking into episodes, can also distribute as characters.
    characters = c_utils.init_characters_in_episodes(episodes)
    c_utils.determine_lines_per_episode(episodes, characters)

    # Determine the characters each character is in a scene with.
    c_utils.determine_scene_interaction(episodes, characters)
    characters_to_plot = c_utils.determine_character_classes(characters, main_char=True,
                                                             minor_char=False)

    # Let's remove some characters to make the plots look nicer.
    #to_remove = ["The Mountain"]
    to_remove = []
    for character_name in to_remove:
        if character_name in characters_to_plot:
            characters_to_plot.remove(character_name)

    # Then let's do some plotting!

    # This is a histogram of the number of lines said by the character across the Season.
    plot_line_count_hist(characters, episodes, characters_to_plot=None)

    # Wordcloud of the words said by characters.
    # plot_wordcloud_character(episodes, "./plots")
