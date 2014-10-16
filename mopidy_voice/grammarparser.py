from __future__ import unicode_literals

import re


class GrammarParser():

    def __init__(self, grammar):
        """Create the grammar rule function mappings and store the grammar"""
        self.rules = {
          'V_N_x': self.V_N_x,                  # eg Search artist Coldplay
          'V_N_x_IN_x': self.V_N_x_IN_x,
          'V_N_x_IN_N_x': self.V_N_x_IN_N_x,
          'V_x_IN_x': self.V_x_IN_x,
          'V_x_IN_N_x': self.V_x_IN_N_x,
          'V_x_IN_N_x_IN_x': self.V_x_IN_N_x_IN_x,
          'V_x_IN_x_IN_x': self.V_x_IN_x_IN_x,
          'V_x_N_x': self.V_x_N_x,
          'V_x_N_x_IN_x': self.V_x_N_x_IN_x, 
          'V_x': self.V_x,
          'V': self.V
        }
        self.grammar = grammar

    def V_N_x(self, result, context):
        return { 'intent': result[0], 'entities': {result[1]: result[2]} }
    def V_N_x_IN_x(self, result, context):
        return { 'intent': result[0], 'entities': {result[1]: result[2],
                                                   context[0]: result[4]} }
    def V_N_x_IN_N_x(self, result, context):
        return { 'intent': result[0], 'entities': {result[1]: result[2],
                                                   result[4]: result[5]} }
    def V_x_IN_x(self, result, context):
        return { 'intent': result[0], 'entities': {context[0]: result[1],
                                                   context[1]: result[3]} }
    def V_x_IN_N_x(self, result, context):
        return { 'intent': result[0], 'entities': {context[0]: result[1],
                                                   result[3]: result[4]} }
    def V_x_IN_N_x_IN_x(self, result, context):
        return { 'intent': result[0], 'entities': {context[0]: result[1],
                                                   result[3]: result[4],
                                                   context[1]: result[6]} }
    def V_x_IN_x_IN_x(self, result, context):
        return { 'intent': result[0], 'entities': {context[0]: result[1],
                                                   result[2]: result[3],
                                                   context[1]: result[5]} }
    def V_x_N_x(self, result, context):
        return { 'intent': result[0], 'entities': {context[0]: result[1],
                                                   result[2]: result[3]} }
    def V_x_N_x_IN_x(self, result, context):
        return { 'intent': result[0], 'entities': {context[0]: result[1],
                                                   result[2]: result[3],
                                                   context[1]: result[5]} }
    def V_x(self, result, context):
        return { 'intent': result[0], 'entities': {context[0]: result[1]} }
    def V(self, result, context):
        return { 'intent': result, 'entities': None }

    def parse(self, sent):
        """Parser for a sentence in the provided grammar"""
        for r, func, context in self.grammar:
            # Use the domain-specific regular-expression on the sentence
            result = re.findall(r, sent)
            if (result and func in self.rules.keys()):
                # A valid pattern-match was found
                return self.rules[func](result[0], context)
            # Returns none if no valid pattern-match was returned
            return None
