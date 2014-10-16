from __future__ import unicode_literals

import logging
import pykka

from mopidy import service
from mopidy.utils.jsonrpc import private_method
from musicgrammar import music_grammar_parser
from speech2text import SpeechToText

logger = logging.getLogger(__name__)

VOICE_SERVICE_NAME = 'voice'


class VoiceRecognitionManager(pykka.ThreadingActor, service.Service):
    """
    VoiceRecognitionManager 

    It implements a mopidy Service and posts events to any classes
    mixing in the ServiceListener interface.

    Some of the use-cases supported are:

    - Continuously monitor the audio source for voice commands
    - Translate voice commands to Mopidy operations such as
    search, play, stop, next, previous, etc
    """
    name = VOICE_SERVICE_NAME
    public = True

    def __init__(self, config, core):
        super(VoiceRecognitionManager, self).__init__()
        self.config = dict(config[self.name])
        self.core = core
        self.speech2text = None

    def _speech_to_text_result(self, res_type, tag, text):
        if (res_type == 'partial'):  # We don't support partial results
            return
        service.ServiceListener.send('voice_recognition_result',
                                     service=self.name,
                                     utterance=text.lower())
        self._music_command_handler(text.lower())

    def _music_command_handler(self, utterance):
        result = music_grammar_parser(utterance)
        if result is None:
            return

        intent = result['intent']
        entities = result['entities']
        logger.info('Got command: %s -> %s', intent, entities)

        if intent in ['play'] and entities is None:
            self._music_control_play()
        elif intent in ['pause']:
            self._music_control_pause()
        elif intent in ['resume']:
            self._music_control_resume()
        elif intent in ['stop', 'reset']:
            self._music_control_stop()
        elif intent in ['skip', 'next']:
            self._music_control_next()
        elif intent in ['back', 'previous']:
            self._music_control_previous()
        elif intent in ['mute'] and 'state' in entities:
            state = True if entities['state'] == 'on' else False
            self._music_control_set_mute(state)
        elif intent in ['mute']:
            self._music_control_set_mute(True)
        elif intent in ['unmute']:
            self._music_control_set_mute(False)
        elif intent in ['insert', 'append', 'search', 'find', 'play'] and \
            entities is not None:
            self._music_search(intent, entities)
        elif intent in ['reset']:
            self._music_reset()
        elif intent in ['clear']:
            self._music_clear()
        elif intent in ['shuffle'] and 'state' in entities:
            state = True if entities['state'] == 'on' else False
            self._music_shuffle(state)
        elif intent in ['repeat'] and 'state' in entities:
            state = True if entities['state'] == 'on' else False
            self._music_repeat(state)
        else:
            logger.warn('Unrecognised intent: %s', intent)

    def _music_shuffle(self, shuffle):
        self.core.tracklist.shuffle = shuffle

    def _music_repeat(self, repeat):
        self.core.tracklist.repeat = repeat

    def _music_clear(self):
        self.core.tracklist.clear()

    def _music_reset(self):
        tl_tracks = self.core.tracklist.slice(0, 1)
        if (len(tl_tracks) > 0):
            self.core.playback.change_track(tl_tracks[0])

    def _music_search(self, intent, query):
        if 'query' in query:
            query['any'] = query.pop('query')
        result = self.core.library.search(query=query).get()
        tracks = result.tracks
        if (len(tracks) == 0):
            return
        at_position = 0 if intent is 'insert' else None
        sz = min(self.config['max_search_results'], len(tracks))
        tl_tracks = self.core.tracklist.add(tracks=tracks[0:sz],
                                            at_position=at_position).get()
        if (intent is 'play' and len(tl_tracks) > 0):
            self.core.change_track(tl_track=tl_tracks[0])

    def _music_control_play(self):
        self.core.playback.play()

    def _music_control_stop(self):
        self.core.playback.stop()

    def _music_control_pause(self):
        self.core.playback.pause()

    def _music_control_resume(self):
        self.core.playback.pause()

    def _music_control_next(self):
        self.core.playback.next()

    def _music_control_set_mute(self, mute):
        self.core.playback.mute = mute

    def _music_control_previous(self):
        self.core.playback.previous()

    @private_method
    def on_start(self):
        """
        Activate the service
        """
        if (self.speech2text is not None):
            return

        # Create speech to text instance based on configured audio source
        # and provide our local callback handler for detected results
        use_pocketsphinx = self.config['use_pocketsphinx']
        model_dir = self.config['model_dir'] if use_pocketsphinx else None
        model_name = self.config['model_name'] if use_pocketsphinx else None
        self.speech2text = SpeechToText(self.config['audiosource'],
                                        model_dir,
                                        model_name,
                                        self._speech_to_text_result)
        self.speech2text.play()

        # Notify listeners
        self.state = service.ServiceState.SERVICE_STATE_STARTED
        service.ServiceListener.send('service_started', service=self.name)
        logger.info('VoiceRecognitionManager started')

    @private_method
    def on_stop(self):
        """
        Put the service into idle mode.
        """
        if (self.speech2text is None):
            return

        # Clean up
        self.speech2text.pause()
        self.speech2text.exit()
        self.speech2text = None

        # Notify listeners
        self.state = service.ServiceState.SERVICE_STATE_STOPPED
        service.ServiceListener.send('service_stopped', service=self.name)
        logger.info('VoiceRecognitionManager stopped')

    @private_method
    def on_failure(self, *args):
        pass

    @private_method
    def stop(self, *args, **kwargs):
        return pykka.ThreadingActor.stop(self, *args, **kwargs)

    def set_property(self, name, value):
        """
        Set a property by name/value.  The property setting is
        not persistent and will force the extension to be
        restarted.
        """
        if (name in self.config):
            self.config[name] = value
            service.ServiceListener.send('service_property_changed',
                                         service=self.name,
                                         props={ name: value })
            self.on_stop()
            self.on_start()

    def get_property(self, name):
        """
        Get a property by name.  If name is ``None`` then
        the entire property dictionary is returned.
        """
        if (name is None):
            return self.config
        else:
            try:
                value = self.config[name]
                return { name: value }
            except:
                return None

    def enable(self):
        """
        Enable the service
        """
        self.on_start()

    def disable(self):
        """
        Disable the service
        """
        self.on_stop()
