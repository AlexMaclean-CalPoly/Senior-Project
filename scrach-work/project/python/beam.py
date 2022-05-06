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
from collections import defaultdict, Counter

import numpy as np


class BeamSearch:
    def __init__(self, lm, alphabet, beam_width=25, alpha=0.30, beta=5, prune=0.001):
        self.alphabet = alphabet + ['_']
        self.lm = lm

        self.beam_width = beam_width
        self.alpha = alpha
        self.beta = beta
        self.prune = prune

        self.Pb, self.Pnb = defaultdict(Counter), defaultdict(Counter)
        self.Pb[0][''] = 1
        self.Pnb[0][''] = 0
        self.A_prev = ['']
        self.A_next = None

    def process(self, ctc):
        offset = len(self.Pb)
        timestep_count = ctc.shape[0]

        for ctc_t, t in zip(ctc, range(offset, timestep_count + offset)):
            # print(f"{t}")
            pruned_alphabet = [self.alphabet[i] for i in np.where(ctc_t > self.prune)[0]]
            for prefix in self.A_prev:
                for chr in pruned_alphabet:
                    c_ix = self.alphabet.index(chr)

                    if chr == '_':
                        self.Pb[t][prefix] += ctc_t[-1] * (self.Pb[t - 1][prefix] + self.Pnb[t - 1][prefix])

                    else:
                        prefix_new = prefix + chr
                        if len(prefix) > 0 and chr == prefix[-1]:
                            self.Pnb[t][prefix_new] += ctc_t[c_ix] * self.Pb[t - 1][prefix]
                            self.Pnb[t][prefix] += ctc_t[c_ix] * self.Pnb[t - 1][prefix]

                        elif len(prefix.replace(' ', '')) > 0 and chr == ' ':
                            lm_prob = self.lm_score(prefix_new) ** self.alpha
                            self.Pnb[t][prefix_new] += lm_prob * ctc_t[c_ix] * (self.Pb[t - 1][prefix] + self.Pnb[t - 1][prefix])
                        else:
                            self.Pnb[t][prefix_new] += ctc_t[c_ix] * (self.Pb[t - 1][prefix] + self.Pnb[t - 1][prefix])

                        if prefix_new not in self.A_prev:
                            self.Pb[t][prefix_new] += ctc_t[-1] * (self.Pb[t - 1][prefix_new] + self.Pnb[t - 1][prefix_new])
                            self.Pnb[t][prefix_new] += ctc_t[c_ix] * self.Pnb[t - 1][prefix_new]

            self.A_next = self.Pb[t] + self.Pnb[t]
            # print(self.A_prev)
            self.A_prev = sorted(self.A_next, key=self.sorter, reverse=True)[:self.beam_width]

        return self.A_prev[0]

    def lm_score(self, tokens):
        return self.lm(tokens)

    def sorter(self, l):
        return self.A_next[l] * (len(self._get_words(l)) + 1) ** self.beta

    @staticmethod
    def _get_words(l):
        return re.findall(r'\w+[\s|>]', l)
