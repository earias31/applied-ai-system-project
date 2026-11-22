# PawPal+ Model Card

## System overview

PawPal+ is a local, deterministic retrieval-augmented pet-care planner. It searches a small JSON collection of notes using species filters and keyword overlap, then uses the best matching note in the task explanation and to break ties between equally prioritized tasks. Owner-entered priority remains the primary ordering rule. PawPal+ does not use a generative language model and is not a veterinary-care system.

## Limitations and potential biases

- The knowledge base is small, hand-written, and limited to general notes for dogs, cats, and other pets. Its coverage and accuracy have not been independently validated against veterinary references.
- Keyword matching and a small synonym list can miss paraphrases or match a word without understanding the task's meaning. A retrieval score is a keyword-overlap score, not a calibrated measure of truth or confidence.
- Species categories and notes are broad. The planner does not reliably account for an individual pet's age, health, breed, disability, or other circumstances.
- The schedule uses the owner's task durations, priorities, and available time. It does not account for task dependencies, deadlines, recurring needs, travel time, or emergencies, so a plan may be incomplete or unsuitable.
- A relevant note appearing in a plan does not prove that the resulting recommendation is appropriate for a specific animal.

## Misuse risks and safeguards

Someone could mistake a schedule or retrieved note for veterinary advice, use it to change medication instructions, or rely on an incomplete plan for urgent or specialized care. PawPal+ includes a medication-safety note, displays a reminder to follow veterinary instructions, shows the note used, reports when no matching note was found, validates inputs, and logs retrieval and planning failures.

These are limited safeguards, not misuse-proofing. Keyword matching may fail to recognize a rephrased medical question, and the app cannot determine whether a task is urgent. Users should follow their veterinarian's instructions and contact a veterinary professional for medical questions or emergencies. Future improvements should use a reviewed source collection, broaden safety tests for paraphrased medical requests, and make provenance and uncertainty prominent in the interface.

## Reliability testing and what surprised me

The latest automated test run passed **8 of 8 tests**. Tests cover species-aware retrieval, retrieved-evidence tie-breaking, owner-priority ordering, time limits, missing evidence, the medication safety note, invalid inputs, and a missing knowledge-base file. Logging and explicit errors help identify retrieval, loading, and schedule-generation failures.

One surprising result during testing was that “Morning walk” initially retrieved a cat activity note: the shared word “activity,” introduced through synonym expansion, caused a misleading match. I narrowed the cat note's keywords and added a regression assertion that dog-walking guidance is not returned for a cat. This showed me that tests only measure the cases they cover; passing tests do not establish that all retrieval results are accurate.

## Human review

Owners should review the schedule, retrieved note, and source label before using the plan. The tests verify program behavior, not veterinary correctness. No independent veterinary review or user study has been conducted.

## Collaboration with AI

I used an AI coding assistant to help design and implement the retriever, planner, app integration, tests, diagrams, and documentation. I accepted the suggestion to retrieve local pet-care notes before scheduling and use those notes in task explanations, so retrieval changes the application's behavior rather than merely displaying search results.

I revised the initial diagram suggestion instead of using it as written. It included extra ingestion, evaluator, and guardrail components that were not implemented in the starter app, so I simplified it to show the retriever, local knowledge, planner, owner, and tests that fit the actual system. I also kept retrieval deterministic and local rather than adding an external language-model service; that was a better fit for a reproducible project with no API setup.
