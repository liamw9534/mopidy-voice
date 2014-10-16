from __future__ import unicode_literals

import gobject
import pygst
pygst.require('0.10')
gobject.threads_init()

import gst
import os
import time
import logging
import googlesink

logger = logging.getLogger(__name__)


class SpeechToText():

    hysteresis = 1.0
    last_time = -1

    def __init__(self, audiosrc, rate, base_dir, db_name, callback):
        self.is_playing = False
        self.callback = callback
        self._init_gsr(audiosrc, rate, base_dir, db_name)

    def is_playing(self):
        return self.is_playing

    def play(self):
        if (self.isPlaying is False):
            self.pipeline.set_state(gst.STATE_PLAYING)
            self.isPlaying = True

    def pause(self):
        if (self.is_playing):
            self.pipeline.set_state(gst.STATE_PAUSED)
            self.is_playing = False

    def exit(self):
        self.pipeline = None

    def _init_gsr(self, audiosrc, base_dir=None, db_name=None):
        pipeline =  ' %s ! audioconvert channels=1 !' % audiosrc
        pipeline += ' audioresample rate=8000 !'
        if (base_dir and db_name):
            pipeline += ' vader name=vad auto-threshold=true !'
            pipeline += ' pocketsphinx name=sphinx !'
        pipeline += ' flacenc ! google-speech-to-text name=google'
        self.pipeline = gst.parse_launch(pipeline)

        if (base_dir and db_name):
            hmm = base_dir
            lm = base_dir + self.NAME + '.lm'
            dic = base_dir + self.NAME + '.dic'
            sphinx = self.pipeline.get_by_name('sphinx')
            if (os.path.exists(hmm)):
                sphinx.set_property('hmm', hmm[:-1]) # FIXME: Remove trailing '/'
            if (os.path.exists(lm)):
                sphinx.set_property('lm', lm)
            if (os.path.exists(dic)):
                sphinx.set_property('dict', dic)
            sphinx.connect('partial_result', self._sphinx_partial)
            sphinx.connect('result', self._sphinx_result)
            sphinx.set_property('configured', True)

        google = self.pipeline.get_by_name('google')
        google.connect('result', self._google_result)

    def _check_hysteresis(self):
        now = time.time()
        if (self.last_time == -1):
            self.last_time = now - self.hysteresis
        delta = now - self.last_time
        self.last_time = now
        return True if delta >= self.hysteresis else False

    def _sphinx_partial(self, asr, text, uttid):
        self.callback('partial', text)

    def _sphinx_result(self, asr, text, uttid):
        if (self._check_hysteresis()):
            self.callback('result', text)

    def _google_result(self, items):
        if (self._check_hysteresis()):
            self.callback('result', items[0])
