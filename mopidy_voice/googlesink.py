from __future__ import unicode_literals

import gobject
import pygst
pygst.require('0.10')
import gst

import sys
import logging
import requests
import json

logger = logging.getLogger(__name__)


class GoogleSpeechToTextSink(gst.Element):

    __gstdetails__ = (
        'google-speech-to-text',
        'Sink',
        'Sink that receives a FLAC coded stream and sends it to Google Speech to Text',
        'Liam Wickins <liamw9534@gmail.com>')

    _sinktemplate = gst.PadTemplate ('sink',
        gst.PAD_SINK,
        gst.PAD_ALWAYS,
        gst.caps_from_string('audio/x-flac, endianness=1234, rate=8000, channels=1, width=16'))

    def __init__(self):

        super(GoogleSpeechToTextSink, self).__init__()

        self.last_timestamp = None
        self.sinkpad = gst.Pad(self._sinktemplate)
        self.sinkpad.set_setcaps_function(self._sink_setcaps)
        self.sinkpad.set_chain_function(self._sink_chain)
        self.add_pad(self.sinkpad)
        gobject.signal_new('result', self,
                           gobject.SIGNAL_RUN_LAST,
                           gobject.TYPE_NONE,
                           (gobject.TYPE_PYOBJECT,))
        self.fd = None
        self.timer_event = None
        self.timeout = 0.8   # TODO: Should be a property

    def _sink_setcaps(self, pad, caps):
        return True

    def _sink_chain(self, pad, buf):

        logger.debug('Received data len: %s timestamp: %s', len(buf), buf.timestamp)
        try:
            if (self.fd is None):
                self.fd = open('google.flac', 'w')
            self.fd.write(buf)
        except:
            logger.error('Unable to write FLAC audio file:', sys.exc_info()[0])
        self._register_timeout()
        return gst.FLOW_OK

    def _register_timeout(self):
        if (self.timer_event):
            gobject.source_remove(self.timer_event)
        self.timer_event = gobject.timeout_add(int(self.timeout * 1000.0),
                                               self._inactivity_timeout_callback)

    def _inactivity_timeout_callback(self):
        if (self.fd is not None):
            self.fd.close()
            self.fd = None
            response = self._google_api_transaction('google.flac')
            self.emit('result', response)
        return False

    def _google_api_transaction(self, filename):

        url = u'https://www.google.com/speech-api/v1/recognize?client=chromium&lang=en-QA&maxresults=10'
        headers = { 'Content-Type': 'audio/x-flac; rate=8000;' }
        fd = open(filename, 'r')
        files = { 'file': (filename, fd) }

        try:
            r = requests.post(url, files=files, headers=headers)
            text = r.text
        except:
            logger.error('Failed to post request:', sys.exc_info())

        try:
            resp = json.loads(text)
            if ('status' in resp.keys() and resp['status'] == 0):
                if ('hypotheses' in resp.keys() and len(resp['hypotheses']) > 0):
                    return [resp['hypotheses'][i]['utterance'].upper() for i in range(0,len(resp['hypotheses']))]
        except:
            logger.error('Was not able to process API response:', sys.exc_info()[0])
            logger.error('Raw text for debug:', text)

        return None


gobject.type_register(GoogleSpeechToTextSink)
gst.element_register (GoogleSpeechToTextSink, 'google-speech-to-text', gst.RANK_MARGINAL)
