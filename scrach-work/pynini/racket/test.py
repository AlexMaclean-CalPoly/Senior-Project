from normalize import InverseNormalizer
from racket_fst import racket_fst


class RacketVerablize:
    def verbalize(self, raw_tokens):
        tokens = [entry['tokens'] for entry in raw_tokens]
        stack = [[]]
        for token in tokens:
            top = stack[-1]
            ty, text = token['type'], token['text']
            if ty == 'atom':
                top.append(token['text'])
            elif ty == 'op' and text == 'of':
                new = [] if token.get('group', '0') == '1' else [top.pop()]
                top.append(new)
                stack.append(new)
            elif ty == 'op' and text == 'next':
                stack.pop()

        return '\n'.join(self.print_sexp(entry) for entry in stack[0])

    @staticmethod
    def print_sexp(sexp):
        if isinstance(sexp, list):
            return f'({" ".join(RacketVerablize.print_sexp(entry) for entry in sexp)})'
        else:
            return sexp



def main():
    pin = InverseNormalizer(racket_fst(), RacketVerablize())
    while True:
        try:
            exp_str = input('exp: ')
            if exp_str == 'q':
                quit(0)
            o = pin.inverse_normalize(exp_str, verbose=True)
            print(o)

        except Exception:
            print('error')


if __name__ == '__main__':
    main()
