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


class SearchState:
    def __init__(self, Pb=None, Pnb=None, A=None):
        self.Pb = Counter(Pb)
        self.Pnb = Counter(Pnb)
        self.A = A


class BeamSearch:
    def __init__(self, lm, alphabet, beam_width=25, alpha=0.30, beta=5, prune=0.001):
        self.alphabet = alphabet + ["_"]
        self.lm = lm
        self.beam_width = beam_width
        self.alpha = alpha
        self.beta = beta
        self.prune = prune

    def __call__(self, ctc: np.ndarray, state: SearchState):
        for ctc_t in ctc:
            state = self._process(ctc_t, state)
        return state

    def _process(self, ctc_t, state: SearchState):
        next_state = SearchState()
        pruned_alphabet = [
            (i, self.alphabet[i]) for i in np.where(ctc_t > self.prune)[0]
        ]

        for prefix in state.A:
            for ch_i, chr in pruned_alphabet:

                if chr == "_":
                    next_state.Pb[prefix] += ctc_t[-1] * (
                        state.Pb[prefix] + state.Pnb[prefix]
                    )

                else:
                    prefix_new = prefix + chr
                    if len(prefix) > 0 and chr == prefix[-1]:
                        next_state.Pnb[prefix_new] += ctc_t[ch_i] * state.Pb[prefix]
                        next_state.Pnb[prefix] += ctc_t[ch_i] * state.Pnb[prefix]
                    elif len(prefix.replace(" ", "")) > 0 and chr == " ":
                        lm_prob = self.lm(prefix_new) ** self.alpha
                        next_state.Pnb[prefix_new] += (
                            lm_prob
                            * ctc_t[ch_i]
                            * (state.Pb[prefix] + state.Pnb[prefix])
                        )
                    else:
                        next_state.Pnb[prefix_new] += ctc_t[ch_i] * (
                            state.Pb[prefix] + state.Pnb[prefix]
                        )

                    if prefix_new not in state.A:
                        next_state.Pb[prefix_new] += ctc_t[-1] * (
                            state.Pb[prefix_new] + state.Pnb[prefix_new]
                        )
                        next_state.Pnb[prefix_new] += (
                            ctc_t[ch_i] * state.Pnb[prefix_new]
                        )

        A_next = next_state.Pb + next_state.Pnb
        next_state.A = [
            item[0]
            for item in sorted(A_next.items(), key=self._sorter, reverse=True)[
                : self.beam_width
            ]
        ]
        return next_state

    def _sorter(self, item):
        l, score = item
        return score * (len(self._get_words(l)) + 1) ** self.beta

    @staticmethod
    def _get_words(l):
        return re.findall(r"\w+[\s|>]", l)

    @staticmethod
    def start_state():
        return SearchState(Pb={"": 1}, Pnb={"": 0}, A=[""])
