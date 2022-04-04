import tokenize


class RewriteRule:
    def __init__(self, before, after):
        pass


class TokenGroup:
    def __init__(self, *options, is_optional=False):


funs = [
    RewriteRule(before=[TokenGroup('def', 'define'),
                        TokenGroup(['a', 'function'], is_optional=True),
                        'id',
                        TokenGroup('of', 'taking')],
                after=[
                    (tokenize.NAME, 'def'),
                    (tokenize.NAME, 'id'),
                    (tokenize.OP, '(')
                ])
]


def parse_rule(rule: RewriteRule):
