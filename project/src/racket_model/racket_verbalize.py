import csv
from pathlib import Path

import pynini
from nemo_text_processing.text_normalization.en.taggers.cardinal import (
    CardinalFst,
)
from nemo_text_processing.text_normalization.en.taggers.decimal import (
    DecimalFst,
)
from pynini.lib import pynutil
from pynini.lib import utf8

CHAR = utf8.VALID_UTF8_CHAR
WHITE_SPACE = pynini.union(" ", "\t", "\n", "\r", "\u00A0").optimize()
NOT_SPACE = pynini.difference(CHAR, WHITE_SPACE).optimize()

maybe_delete_space = pynutil.delete(pynini.closure(WHITE_SPACE))
delete_space = pynutil.delete(pynini.closure(WHITE_SPACE, lower=1))
insert_space = pynutil.insert(" ")
delete_extra_space = pynini.cross(pynini.closure(WHITE_SPACE, 1), " ")
sigma = pynini.closure(CHAR)
