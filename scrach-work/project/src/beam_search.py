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

import numpy as np
import re
from collections import Counter
from typing import Callable, Optional


class SearchState:
    Pb: Counter[str]
    Pnb: Counter[str]
    A: Optional[list[str]]

    def __init__(self, Pb=None, Pnb=None, A=None):
        self.Pb = Counter(Pb)
        self.Pnb = Counter(Pnb)
        self.A = A


class BeamSearch:
    START_STATE: SearchState = SearchState(Pb={"": 1}, Pnb={"": 0}, A=[""])

    def __init__(
        self,
        lm: Callable[[str], float],
        alphabet: list[str],
        beam_width: int = 25,
        alpha: float = 0.30,
        beta: float = 5,
        prune: float = 0.001,
    ):
        self.alphabet = alphabet + ["_"]
        self.lm = lm
        self.beam_width = beam_width
        self.alpha = alpha
        self.beta = beta
        self.prune = prune

    def __call__(
        self, ctc: np.ndarray, state: SearchState, space: bool = False
    ) -> SearchState:
        initial = state
        for ctc_t in ctc:
            state = self._process(ctc_t, state)
        if space and initial.A == state.A:
            space = np.zeros(len(self.alphabet))
            space[self.alphabet.index(" ")] = 1
            state = self._process(space, state)
        return state

    def _process(self, t: np.ndarray, prev: SearchState) -> SearchState:
        nxt = SearchState()
        print(np.where(t > self.prune))
        pruned_alphabet = [(i, self.alphabet[i]) for i in np.where(t > self.prune)[0]]

        for l in prev.A:
            for ch_i, c in pruned_alphabet:
                p_c = t[ch_i]

                if c == "_":
                    nxt.Pb[l] += p_c * (prev.Pb[l] + prev.Pnb[l])

                else:
                    l_new = l + c
                    if len(l) > 0 and c == l[-1]:
                        nxt.Pnb[l_new] += p_c * prev.Pb[l]
                        nxt.Pnb[l] += p_c * prev.Pnb[l]
                    elif len(l.replace(" ", "")) > 0 and c == " ":
                        lm_prob = self.lm(l_new) ** self.alpha
                        nxt.Pnb[l_new] += lm_prob * p_c * (prev.Pb[l] + prev.Pnb[l])
                    else:
                        nxt.Pnb[l_new] += p_c * (prev.Pb[l] + prev.Pnb[l])

                    if l_new not in prev.A:
                        nxt.Pb[l_new] += t[-1] * (prev.Pb[l_new] + prev.Pnb[l_new])
                        nxt.Pnb[l_new] += p_c * prev.Pnb[l_new]

        A_next = nxt.Pb + nxt.Pnb
        nxt.A = [
            item[0]
            for item in sorted(A_next.items(), key=self._sorter, reverse=True)[
                : self.beam_width
            ]
        ]
        return nxt

    def _sorter(self, item: tuple[str, int]):
        l, score = item
        return score * (len(self._get_words(l)) + 1) ** self.beta

    @staticmethod
    def _get_words(l: str) -> list:
        return re.findall(r"\w+[\s|>]", l)
