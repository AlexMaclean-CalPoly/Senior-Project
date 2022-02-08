# Mid-Quarter Update

## Implementation Plan

During this quarter I want to implement a system that integrates existing language server autocompletion
with part of an existing voice recognition system, to improve accuracy.

The first stage of the system will be a pre-trained acoustic model from
[Nvidia's NeMo](https://docs.nvidia.com/deeplearning/nemo/user-guide/docs/en/main/starthere/intro.html).
NeMo lets me extract the intermediate result of the acoustic model which is an array of probabilities
for each letter occurring at that point in the input.

In existing systems this acoustic model output is combined with a language model to produce the
final transcriptions. I plan to do the same thing, but I will supplement an existing language model
with the information from using the LSP to provide autocompletion.

The new model could be as simple as taking an unweighted mean of an existing language model prediction
and a simple autocompletion prediction where each suggested completion is given an equal weight. It could also be
much more complex and use training on code scraped from GitHub to weight the autocompletion predictions more
accurately. I hope to get closer to the latter, but that will depend on time.

I'm planning on using this [python language server](https://github.com/python-lsp/python-lsp-server)
because it seems to have very good autocompletion support. I'll also implement my system in
python because that's the language NeMo is written in.

## Schedule

Here is what I've actually ended up doing so far and what I plan to do next.

- [x] **Week 01**: Write proposal and do a little research on the existing
    solutions to the problem.
- [x] **Week 02**: Find a modular extensible speech recognition system. Do some more
    research on the existing voice-to-code systems.
- [x] **Week 03**: Get CMU Sphinx running on my machine with custom test data. Figure out
    if it will work for this project (Nope).
- [x] **Week 04**: Find an alternative to CMU Sphinx (NeMo), get it running and tested. Begin
    implementing a language server client and research the protocol.
- [x] **Week 05**: Write a basic language client implementing a subset of the
    JSON-RPC language server protocol. Figure out how to get this client running
    with a couple different language servers.
- [ ] **Week 06**: Determine if the algorithm to reconcile the acoustic model and
    language is modular enough to work in my system (If not find a way to re-implement
    the functionality).
- [ ] **Week 07**: Get the bare minimum system up and running. It likely won't be very
    pretty or implement the language model autocompletion combination in an elegant way.
- [ ] **Week 08**: Figure out how to get NeMo to run on live speech as opposed to a WAV file.
    (This one might be really easy or really hard depending on if NeMo has implemented it)
- [ ] **Week 09**: Implement a better algorithm for reconciling the autocompletion and
    language model. perhaps do some training on scraped code.
- [ ] **Week 10**: Polish the system up and do any catch up from previous weeks.
