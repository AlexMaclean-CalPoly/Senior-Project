"""
Based off of: https://github.com/corticph/prefix-beam-search/blob/master/prefix_beam_search.py

        Performs prefix beam search on the output of a CTC network.
        Args:
            ctc (np.ndarray): The CTC output. Should be a 2D array (timesteps x alphabet_size)
            lm (func): Language model function. Should take as input a string and output a probability.
            alphabet (list): list of characters
            beam_width (int): The beam width. Will keep the 'k' most likely candidates at each timestep.
            alpha (float): The language model weight. Should usually be between 0 and 1.
            beta (float): The language model compensation term. The higher the 'alpha', the higher the 'beta'.
            prune (float): Only extend prefixes with chars with an emission probability higher than 'prune'.
        Returns:
            string: The decoded CTC output.
"""

import re
from collections import Counter

import numpy as np


class BeamSearch:
    def __init__(self, lm, alphabet, beam_width=25, alpha=0.30, beta=5, prune=0.001):
        self.alphabet = alphabet + ['_']
        self.lm = lm

        self.beam_width = beam_width
        self.alpha = alpha
        self.beta = beta
        self.prune = prune

        self.Pb_prev, self.Pnb_prev = Counter(), Counter()
        self.Pb_prev[''] = 1
        self.Pnb_prev[''] = 0
        self.A_prev = ['']

    def process(self, ctc):
        for ctc_t in ctc:
            Pb_t, Pnb_t = Counter(), Counter()
            # print(f"{t}")
            pruned_alphabet = [(i, self.alphabet[i]) for i in np.where(ctc_t > self.prune)[0]]
            for prefix in self.A_prev:
                for c_ix, chr in pruned_alphabet:

                    if chr == '_':
                        Pb_t[prefix] += ctc_t[-1] * (self.Pb_prev[prefix] + self.Pnb_prev[prefix])

                    else:
                        prefix_new = prefix + chr
                        if len(prefix) > 0 and chr == prefix[-1]:
                            Pnb_t[prefix_new] += ctc_t[c_ix] * self.Pb_prev[prefix]
                            Pnb_t[prefix] += ctc_t[c_ix] * self.Pnb_prev[prefix]

                        elif len(prefix.replace(' ', '')) > 0 and chr == ' ':
                            lm_prob = self.lm_score(prefix_new) ** self.alpha
                            Pnb_t[prefix_new] += lm_prob * ctc_t[c_ix] * (self.Pb_prev[prefix] + self.Pnb_prev[prefix])
                        else:
                            Pnb_t[prefix_new] += ctc_t[c_ix] * (self.Pb_prev[prefix] + self.Pnb_prev[prefix])

                        if prefix_new not in self.A_prev:
                            Pb_t[prefix_new] += ctc_t[-1] * (self.Pb_prev[prefix_new] + self.Pnb_prev[prefix_new])
                            Pnb_t[prefix_new] += ctc_t[c_ix] * self.Pnb_prev[prefix_new]

            A_next = Pb_t + Pnb_t
            self.A_prev = [item[0] for item in sorted(A_next.items(), key=self.sorter, reverse=True)[:self.beam_width]]
            self.Pb_prev, self.Pnb_prev = Pb_t, Pnb_t

        return self.A_prev[0]

    def lm_score(self, tokens):
        return self.lm(tokens)

    def sorter(self, item):
        l, score = item
        return score * (len(self._get_words(l)) + 1) ** self.beta

    @staticmethod
    def _get_words(l):
        return re.findall(r'\w+[\s|>]', l)
