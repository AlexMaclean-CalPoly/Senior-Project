"""
Based off of: https://github.com/corticph/prefix-beam-search/blob/master/prefix_beam_search.py
"""

import re
from collections import defaultdict, Counter

import numpy as np


def beam_search(ctc, lm, alphabet, beam_width=25, alpha=0.30, beta=5, prune=0.001):
    """
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

    def sorter(l):
        return A_next[l] * (len(get_words(l)) + 1) ** beta

    alphabet = alphabet + ['%']
    # just add an imaginative zero'th step (will make indexing more intuitive)
    ctc = np.vstack((np.zeros(ctc.shape[1]), ctc))
    timestep_count = ctc.shape[0]

    O = ''
    Pb, Pnb = defaultdict(Counter), defaultdict(Counter)
    Pb[0][O] = 1
    Pnb[0][O] = 0
    A_prev = [O]

    for t in range(1, timestep_count):
        print(f"{t}/{timestep_count}")
        pruned_alphabet = [alphabet[i] for i in np.where(ctc[t] > prune)[0]]
        for l in A_prev:

            if len(l) > 0 and l[-1] == '>':
                Pb[t][l] = Pb[t - 1][l]
                Pnb[t][l] = Pnb[t - 1][l]
                continue

            for c in pruned_alphabet:
                c_ix = alphabet.index(c)

                if c == '%':
                    Pb[t][l] += ctc[t][-1] * (Pb[t - 1][l] + Pnb[t - 1][l])

                else:
                    l_plus = l + c
                    if len(l) > 0 and c == l[-1]:
                        Pnb[t][l_plus] += ctc[t][c_ix] * Pb[t - 1][l]
                        Pnb[t][l] += ctc[t][c_ix] * Pnb[t - 1][l]

                    elif len(l.replace(' ', '')) > 0 and c in (' ', '>'):
                        lm_prob = lm(l_plus.strip(' >')) ** alpha
                        Pnb[t][l_plus] += lm_prob * ctc[t][c_ix] * (Pb[t - 1][l] + Pnb[t - 1][l])
                    else:
                        Pnb[t][l_plus] += ctc[t][c_ix] * (Pb[t - 1][l] + Pnb[t - 1][l])

                    if l_plus not in A_prev:
                        Pb[t][l_plus] += ctc[t][-1] * (Pb[t - 1][l_plus] + Pnb[t - 1][l_plus])
                        Pnb[t][l_plus] += ctc[t][c_ix] * Pnb[t - 1][l_plus]

        A_next = Pb[t] + Pnb[t]
        A_prev = sorted(A_next, key=sorter, reverse=True)[:beam_width]

    return A_prev[0].strip('>')


def get_words(l):
    return re.findall(r'\w+[\s|>]', l)
