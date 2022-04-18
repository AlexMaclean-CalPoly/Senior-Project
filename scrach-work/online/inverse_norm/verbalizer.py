import ast
import tokenize
from typing import List

from black import format_str, FileMode



class PyVerbalizer:
    def verbalize(self, tokens_dict: List[dict]):
        tokens = []
        for token_dict in tokens_dict:
            entry = token_dict['tokens']

            token_type = entry['type']
            token_text = entry['text']

            tokens.append((int(token_type),
                           ast.literal_eval(f'"{token_text}"')))

        return format_str(tokenize.untokenize(tokens), mode=FileMode())

#
# class StringVerbalizer:
#     def verbalize(self, tokens_dict: List[dict]):
#         tokens = []
#         for token_dict in tokens_dict:
#             entry = token_dict['tokens']
#             token_ty, token_string = entry.popitem()
#             tokens.append(token_string)
#
#         return f'"{" ".join(tokens)}"'
#
# class IdentityVerbalizer:
#     def verbalize(self, token):
#         return token
