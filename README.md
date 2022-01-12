# Senior Project: Vocal Programming

All work for my senior project completing courses CSC-491 and CSC-492 during 2022 Winter and Spring terms with advisor John Clements at Cal Poly SLO.

## Overall Goals (from [Proposal](proposal/proposal.pdf))

For this project I'm interested in addressing the voice code problem in the speech to text system and the programming language as opposed to just adding a layer between them. Speech to text systems could be specialized for programming so that they resolve noisy input in a way that makes sense given the context of the program, as opposed to natural English language. For example, in a normal context the utterance "wī" would likely mean "why", however in programming "y" seems like a more appropriate choice (especially if that id is in scope or it is preceded by "x"). Existing systems get around this by using a phonetic alphabet, so a command word like "yap" means "y". If the model used by speech to text system were modified, it might be possible to use the normal alphabet and reduce the barrier to entry. A better model would also reduce the error rate, especially in more noisy environments.

On the language design side of the problem, I'm interested in writing a language with voice in mind that can then be compiled into another high level language. Developing this language would require augmenting normal compilation with natural language processing and program synthesis. The surface syntaxes of existing languages are designed to be easy to type and looks good on a screen, but those are not the same concerns when designing a language for voice. A language for vocal programming might have new forms to specify programs in a less line-by-line manner, allow developers some leeway with regard to specific wording, or use a much less symbol heavy surface syntax.

In short, I want to build a system that can be told something like "define a function factorial that takes an int n if n equals zero return one otherwise return n times factorial of n minus one." and produces a program in a language like Racket, JavaScript, or Python.

## Contents

* [Proposal](proposal/proposal.pdf)
