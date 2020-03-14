*******************
screenplay-analysis
*******************

.. figure:: got.gif

Description
===========

This repo contains code intended to read and parse various scripts (television, movies, plays, etc).  For now, it has
only been formatted to run on Game of Thrones scripts through the
`Genius website <https://genius.com/albums/Game-of-thrones>`_.  However, it contains the foundations for extending to
other scripts with (hopefully) minimal fuss.  Please fork and adjust it to your heart's desire!

Disclaimer
----------

Majority of this code was a tool to procrastinate writing my PhD thesis during mid-2019.  It was meant as an exercise
to get me used to working with Python classes and as such, the code flow is extremely rough.  Enjoy!

Using the Game of Thrones Visualization
=======================================

If you're crazy enough to want to run this code, here's some steps to get you going.

.. code::

    $ git clone https://github.com/jacobseiler/screenplay-analysis
    $ cd screenplay-analysis
    $ pip install -r requirements.txt
    $ python plot_characters.py

This will produce a histogram specifying the number of lines spoken by Jon, Tyrion, and Daenerys throughout the series.
More importantly, it will output a number of images to the ``cumu_plots`` directory showing the interactions between
the major characters and (some) minor characters based on scenes.

A Word on Definitions
---------------------

The character interactions attempt to encapsulate how often different characters interact with each other throughout
the series.  It is hence necessary to decide on a definition of "interact"; is an interaction when two people verbally
talk to each other?  When they appear near each other on-screen?  When they mention someone else's name? For technical
reasons, I define here an "interaction" as two characters **speaking in the same scene**.  Critically, this cuts out a
large number of interactions where characters are often present in the scene but don't speak. For example, the data for
**The Mountain** is most certainly incorrect because he spends his time being a zombie with no voice.

Following on from this definition, I also need to define what a "scene" is.  Is a scene an unbroken length of dialogue
in the same location?  If so, what about when we cut to different parts of Winterfell or when a line or two of dialogue
is spoken before jumping to another location? Is the entire Battle of the Blackwater a single "scene"?  What about the
Long Night where the wildlings assault the wall? The White Walkers attack on Winterfell?  In an attempt to cut down on
the effort on my part, I simply defer to the script itself.  When the script says "scene change" or "cut to", that
marks a "scene" for me.  This loses some accuracy but the only other approach would be to watch the entire series
again, and I don't think I care THAT much...

Note
~~~~
I made the executive decision and made The Long Night (s04e09) a single scene.  Otherwise all of the Night's Watch
characters would have their data all biased.

Character Interactions
----------------------

Here I'll briefly describe some basic decisions made for the character interaction plots.  This is basically just a
place for me to pontificate and act like people care about what I've written.

Node Colour
~~~~~~~~~~~

Alive characters a blue, when a character dies, their node turns orange.

Node Size
~~~~~~~~~

The size of each character node is dictated by the number of scenes that a character is in.

Node Label
~~~~~~~~~~

The size of each character node is dictated by the number of scenes that a character is in. To allow the label to scale
closely with the size of the node, I bin the node size into log-spaced bins and then assign a label based on the bin
the node falls in.  *shrug* It seemed to look ok.

Edge Weight
~~~~~~~~~~~

Ok, here's where the big decision came in. What is the best way to weight an edge between Character A and B? While it
is tempting to simply say "The weight of the edge is given by the number of times A and B are in a scene together",
this would cause the popular characters to quickly dominate the graph.  Furthermore, characters that die early would
hence have very small edge weights.  This would lose a lot of the subtlety and interconnectedness of the series.

Instead, I have chosen the edge weight to encapsulate **how often A and B appear together relative to the number of
scenes that A and B appear in**.  That is, if A and B **only appear in scenes together**, then they will be given very
thick edges.  This is what occurs during the early seasons when characters are initially introduced; **Melisandre**
and **Stannis** initially have a very thick edge that connect them.  As time progresses, and they appear in scenes with
other characters, this thickness decreases until reaches a more stable level.  This behaviour allows you to see how the
interactions between two characters, in addition to how they're interacting in a global sense, evolves over time. For
example, even by **s08e06**, the link between **Tormund** and **Ygritte** is still appreciable!


<script src="http://vjs.zencdn.net/4.0/video.js"></script>

<video id="pelican-installation" class="video-js vjs-default-skin" controls
preload="auto" width="683" height="384" poster="/static/screencasts/pelican-installation.png"
data-setup="{}">
<source src="/static/screencasts/pelican-installation.mp4" type='video/mp4'>
</video>

