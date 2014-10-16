from __future__ import unicode_literals

from grammarparser import GrammarParser


def music_grammar_parser(self, sentence):
    """
    Invokes grammar parsing based on the grammar defined within this
    class and returns the result.
    An exception is raised if the parser could not find a good match
    to the grammar.  This probably means the user intended something
    else, or the grammar is not good enough.
    """
    # Extend this list to support more music outcome application commands
    volume = "(volume)"
    mute = "(mute)"
    shuffle = "(shuffle)"
    reset = "(reset)"
    info = "(info)"
    navi = "(skip|back|next|previous)"
    obj = " (track|playlist)"
    decl = "[set|make] "
    cmd = "(back|skip|stop|pause|resume|play|reset|clear|preview|quit|exit|info|mute|unmute|louder|quieter|volume|shuffle|sink|scan|disconnect)"
    x = " (.+)"
    num = " (\d+)"
    onoff = " (on|off)"
    search = "(insert|append|find|search|play)"  # Special command for building music queries
    year = " (year)" 
    to = " (to)"
    by = " (by)"
    frm = " (from)"
    artist = " (artist)"
    album = " (album)"
    genre = " (genre)"
    track = " (track)"

    # The grammar set for music outcomes.  The ordering is important because
    # of greedy regexp matching when using wildcards.  There, ensure that
    # more specific queries are put at the top of the list first to avoid
    # getting false matches
    grammar = [
        ("^"+search+artist+x+"$", 'V_N_x', [] ),
        ("^"+search+track+x+frm+album+x+"$", 'V_N_x_IN_N_x', [] ),
        ("^"+search+track+x+by+artist+x+"$", 'V_N_x_IN_N_x', [] ),
        ("^"+search+track+x+by+x+"$", 'V_N_x_IN_x', ['artist'] ),
        ("^"+search+track+x+frm+x+"$", 'V_N_x_IN_x', ['album'] ),
        ("^"+search+track+x+artist+x+"$", 'V_N_x_N_x', [] ),
        ("^"+search+track+x+"$", 'V_N_x', [] ),
        ("^"+search+genre+x+"$", 'V_N_x', [] ),
        ("^"+search+album+x+by+x+"$", 'V_N_x_IN_x', [ 'artist' ] ),
        ("^"+search+album+x+"$", 'V_N_x', [] ),
        ("^"+search+year+x+to+x+"$", 'V_N_x_IN_x', ['year_to'] ),
        ("^"+search+year+x+"$", 'V_N_x', [] ),
        ("^"+search+x+by+artist+x+"$", 'V_x_IN_N_x', ['query'] ),
        ("^"+search+x+by+x+"$", 'V_x_IN_x', ['query', 'artist'] ),
        ("^"+search+x+frm+album+x+"$", 'V_x_IN_N_x', ['query'] ),
        ("^"+search+x+frm+genre+x+"$", 'V_x_IN_N_x', ['query'] ),
        ("^"+search+x+frm+year+x+to+x+"$", 'V_x_IN_N_x_IN_x', ['query'] ),
        ("^"+search+x+frm+year+x+"$", 'V_x_IN_N_x', ['query']),
        ("^"+search+x+year+x+to+x+"$", 'V_x_N_x_IN_x', ['query', 'year_to']),
        ("^"+search+x+year+x+"$", 'V_x_N_x', ['query'] ),
        ("^"+search+x+artist+x+"$", 'V_x_N_x', ['query'] ),
        ("^"+search+x+album+x+"$", 'V_x_N_x', ['query'] ),
        ("^"+search+x+genre+x+"$", 'V_x_N_x', ['query'] ),
        ("^"+search+x+frm+x+"$", 'V_x_IN_x', ['track', 'album']),
        ("^"+search+x+"$", 'V_x', ['query']),
        ("^"+decl+volume+num+"$", 'V_x', ['volume']),
        ("^"+volume+num+"$", 'V_x', ['volume']),
        ("^"+info+obj+"$", 'V_x', ['object']),
        ("^"+navi+num+"$", 'V_x', ['number']),
        ("^"+reset+num+"$", 'V_x', ['position']),
        ("^"+shuffle+onoff+"$", 'V_x', ['state']),
        ("^"+decl+shuffle+onoff+"$", 'V_x', ['state']),
        ("^"+mute+onoff+"$", 'V_x', ['state']),
        ("^"+decl+mute+onoff+"$", 'V_x', ['state']),
        ("^"+cmd+"$", 'V', [])
    ]

    # Create grammar parser and parse the sentence
    return GrammarParser(grammar).parse(sentence)
