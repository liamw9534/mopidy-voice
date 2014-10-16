************
Mopidy-Voice
************

.. image:: https://pypip.in/version/Mopidy-Voice/badge.png?latest
    :target: https://pypi.python.org/pypi/Mopidy-Voice/
    :alt: Latest PyPI version

.. image:: https://pypip.in/download/Mopidy-Voice/badge.png
    :target: https://pypi.python.org/pypi/Mopidy-Voice/
    :alt: Number of PyPI downloads

.. image:: https://travis-ci.org/liamw9534/mopidy-voice.png?branch=master
    :target: https://travis-ci.org/liamw9534/mopidy-voice
    :alt: Travis CI build status

.. image:: https://coveralls.io/repos/liamw9534/mopidy-voice/badge.png?branch=master
   :target: https://coveralls.io/r/liamw9534/mopidy-voice?branch=master
   :alt: Test coverage

`Mopidy <http://www.mopidy.com/>`_ extension for voice control.


Installation
============

Install by running::

    pip install Mopidy-Voice

Or, if available, install the Debian/Ubuntu package from `apt.mopidy.com
<http://apt.mopidy.com/>`_.


Introduction
============

The ``mopidy-voice`` extension integrates voice control into Mopidy by utilizing any available audio
input device (e.g., ``alsasrc``, ``pulsesrc``) that allows a user's voice to be sampled and
processed digitally for voice control purposes.

The voice recognition engine is built using a GStreamer pipeline which operates two separate recognition
engines in parallel::

- PocketSphinx Engine - this is used for simple commands only that can be resolved quickly without
	any additional external search operations.  For example, track navigation functions such as
	pause, resume, stop, play, etc.

- Google Speech To Text Engine - this is used for more complex utterances requiring the power of
	Google's search engine which can use probabilistic inference to improve accuracy of search
	terms.  This is especially useful when referring to album, track or artist names.


Both engines run in parallel continuously aided by a VAD (Voice Activity Detector) which filters based
on a signal-to-noise threshold.


Vocabulary and Grammar
----------------------

A simple grammar parser is implemented with some fairly basic rules.

Stand alone Commands
~~~~~~~~~~~~~~~~~~~~

The following commands may be spoken stand alone to perform the stated function:

- back: skip backwards to the previous track
- skip: skip forward to the next track
- stop: stop playback at the current track
- pause: pause current playback
- resume: resume from paused state
- play: start playback from the last played track
- reset, clear: remove all entries from the current tracklist and stop playback
- info: request an audio announcement of the current playing track(*) 
- mute, unmute: mute or unmute the volume
- louder, quieter: increase or decrease the volume level by some amount

(*) Audio announcements are not supported by this extension.  An internal event is
	raised by this command which may be acted upon by another extension for performing
	audio announcements.

Commands taking a single parameter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- volume [0..100]: set the volume level to the spoken integer as a percentage
- shuffle [on | off]: set the shuffle function on or off as spoken
- mute [on | off]: set the mute function on or off as spoken
- skip [number]: skip forwards by the number of tracks stated
- back [number]: skip backwards by the number of tracks stated


Music search commands
~~~~~~~~~~~~~~~~~~~~~

The following command set is intended to allow the current tracklist to be assigned with tracks
based on a number of search criteria.  It works by firstly uttering a keyword followed by the search criteria.

The allowed keywords are:

- insert: executes the search and inserts the results to the beginning of the current tracklist
- append, search, find: executes the search and appends the results to the end of the current tracklist
- play: executes the search and appends the results to the end of the current tracklist and skips playback to the first
	new track found

Any of the above keywords may be used in conjunction with one of the following search terms:

1. <keyword> [artist|track|album]: the search term may be either an artist, track or album.
2. <keyword> [track] from [album]: the search term is a track from a particular album.
3. <keyword> [track] genre [genre]: the search term is a track from a particular music genre.
4. <keyword> [track] album [album]: the search term is a track from a particular album.
5. <keyword> [track] artist [album]: the search term is a track by a particular artist.
6. <keyword> [artist|track|album] year [year]: the search term is an artist, track or album from a particular year.
7. <keyword> [artist|track|album] year [year] to [year]: the search term is an artist, track or album from a particular range of years.
8. <keyword> [artist|track|album] from year [year]: the search term is an artist, track or album from a particular year.
9. <keyword> [artist|track|album] from year [year] to [year]: the search term is an artist, track or album from a particular range of years.
10. <keyword> [artist|track|album] from genre [genre]: the search term is an artist, track or album from a particular music genre.
11. <keyword> [track] from album [album]: the search term is a track from a particular album.
12. <keyword> [track|album] by [artist]: the search term is a track or album by a particular artist.
13. <keyword> [track|album] by artist [artist]: the search term is a track or album by a particular artist.
14. <keyword> year [year]: the search term is the most popular tracks from a particular year.
15. <keyword> year [year] to [year]: the search term is the most popular tracks from a particular range of years.
16. <keyword> album [album]: the search term is all tracks from a particular album.
17. <keyword> album [album] by [artist]: the search term is all tracks from a particular album by a particular artist.
18. <keyword> genre [genre]: the search term is the most popular tracks from a particular genre.
19. <keyword> track [track]: the search term is a particular track.
20. <keyword> track [track] artist [artist]: the search term is a particular track by a particular artist.
21. <keyword> track [track] from [album]: the search term is a particular track from a particular album.
22. <keyword> track [track] by [artist]: the search term is a particular track by a particular artist.
23. <keyword> track [track] by artist [artist]: the search term is a particular track by a particular artist.
24. <keyword> track [track] from album [album]: the search term is a particular track from a particular album.
25. <keyword> artist [artist]: the search term is the most popular tracks by a particular artist.


Examples
~~~~~~~~

To illustrate how a search can be performed consider the following examples:

- "Play artist Coldplay" => Adds the most popular Coldplay tracks to the end of your tracklist and skips to the first one found.
- "Append album X and Y" => Adds the tracks from album X & Y to the end of your tracklist.
- "Play year 1984" => Adds the most popular tracks from 1984 to the end of your tracklist and start playing the first one found.


Combining Utterances
~~~~~~~~~~~~~~~~~~~~

It is not presently possible to combine vocal terms together.  Each term must be spoken distinctly and
separately from one another.


Configuration
=============

Extension
---------

Add the following section to your Mopidy configuration file following installation::

    [voice]
    enabled = true
    audiosource = autoaudiosrc
    max_search_results = 10
    use_pocketsphinx = true
    model_dir = /home/mopidy/pocketsphinx_model
    model_name = mopidy


For capturing spoken utterances it is necessary to have an microphone connected to your system.  This
must be nominated by setting the ``audiosource`` property.  It can be any valid GStreamer element that
provides a sound source.

For all search based commands, the search result limit is applied as defined in ``max_search_results``.

The use of the PocketSphinx Voice Recognition engine is optional and can be set using ``use_pocketsphinx`.
If ``use_pocketsphinx`` is enabled, then it is necessary to have the correct install path and recognition
model defined via ``model_dir`` and ``model_name``.

A usable model comes with this extension but you can add your own if you wish and have the know how.


Project resources
=================

- `Source code <https://github.com/liamw9534/mopidy-voice>`_
- `Issue tracker <https://github.com/liamw9534/mopidy-voice/issues>`_
- `Download development snapshot <https://github.com/liamw9534/mopidy-voice/archive/master.tar.gz#egg=mopidy-voice-dev>`_


Changelog
=========


v0.1.0 (UNRELEASED)
----------------------------------------

- Under development - in proof of concept/prototyping phase.
