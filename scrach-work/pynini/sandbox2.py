import pynini
from pynini.lib import pynutil

text = '({()'

fst = pynini.closure(
    pynini.cross('(', '([1000]') | pynini.cross(')', ')[1001]') |
    pynini.cross('{', '{[1010]') | pynini.cross('}', '}[1011]')) + pynutil.insert(pynini.closure(pynini.union(')[1001]', '}[1011]')))

parens = pynini.PdtParentheses()
parens.add_pair(1000, 1001)
parens.add_pair(1010, 1011)

p2 = pynini.compose(text, fst)
p3 = pynini.pdt_expand(pynini.project(p2, 'output'), parens=parens)

for path in p3.paths().items():
    print(path)