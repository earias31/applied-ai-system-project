# PawPal+ Model Card

## System overview

PawPal+ is a local, deterministic retrieval-augmented pet-care planner. It searches a small JSON collection of notes using species filters and keyword overlap, then uses the best matching note in the task explanation and to break ties between tasks with equal priority. Owner-entered priority remains the primary ordering rule. This is not a generative language model and it does not provide veterinary care.

## Limitations and potential biases
The knowlage is self implimented, and is just general for basic pets like dogs and cats. In adition, stuff for species is more broad and relies on owner imput.  Somtimes keywords arent exactly correct. The current task list does not account for things like reoccuring needs, emergancies, deadlines, etc. 
## Misuse risks and safeguards

Someone could treat the schedule or a retrieved note as veterinary advice, use it to change medication instructions, or rely on an incomplete plan for urgent or specialized care. PawPal+ includes a medication-safety note, displays a reminder to follow veterinary instructions, shows the note used, and explicitly reports when no matching note was found. It also validates task and schedule inputs and logs retrieval and planning failures.

These are limited safeguards, not misuse-proofing. Keyword matching may fail to recognize a rephrased medical question, and the app cannot determine whether a task is urgent. Users should follow their veterinarian's instructions and contact a veterinary professional for medical questions or emergencies. Future improvements should use a reviewed source collection, broaden safety tests for paraphrased medical requests, and make provenance and uncertainty prominent in the interface.

## Reliability testing and what surprised me

The latest run of the automated suite passed **8 of 8 tests**. Tests cover species-aware retrieval, retrieved-evidence tie-breaking, owner-priority ordering, time limits, missing evidence, the medication safety note, invalid inputs, and a missing knowledge-base file. Logging and explicit error messages help identify retrieval, loading, and schedule-generation failures.

One surprising result during testing was that the phrase “Morning walk” initially retrieved a cat activity note: the shared word “activity,” introduced through synonym expansion, created a misleading cross-species match. I narrowed the cat note's keywords and added a regression assertion that a dog-walking note is not returned for a cat. This shows that a passing test suite checks the cases it covers; it does not establish that all retrieval results are accurate.

## Human review

Owners should review the schedule, retrieved note, and source label before using the plan. The tests verify program behavior and not actual vet advice.
## Collaboration with AI

I used an AI coding assistant to help design and implement the retriever, planner, app integration, tests, diagrams, and documentation. I accepted the suggestion to retrieve local pet-care notes before scheduling and use the retrieved note in the plan's explanation, so retrieval changes the application's behavior rather than merely displaying search results.

A thing I did not keep the initial diagram suggestion as written. It was over complicated and honestly a bit wordy. I had to go back amd fourth a bit to get something usable.
