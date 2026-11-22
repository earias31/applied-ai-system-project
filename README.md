# PawPal+ — RAG Pet-Care Planner

## Original project: PawPal+ (Modules 1–3)

PawPal+ began as a pet-care planning app to help owners organize tasks such as walks, feeding, and grooming. Its original goal was to collect pet details and care tasks, then produce a daily plan based on task duration, priority, and the owner's available time.

## Title and summary

PawPal+ is a Streamlit app that builds a time-limited pet-care schedule and explains its choices using Retrieval-Augmented Generation (RAG). It searches a small local collection of pet-care planning notes for each task; relevant notes influence the ordering of equally prioritized tasks and are used to generate task-specific explanations.

The current assistant is fully local and deterministic: it uses keyword-based retrieval and a grounded response generator, with no paid API or external model required. It does not provide veterinary advice or invent guidance when no note matches.

## Architecture overview

The system diagram is in [diagrams/architecture.mmd](diagrams/architecture.mmd). The Streamlit app collects the pet, tasks, available time, and schedule start time. `PawPalAssistant` asks `CareNoteRetriever` to search [pet_care_notes.json](knowledge/pet_care_notes.json) for each task, then creates a schedule. Owner priority determines the main ordering; retrieved-note relevance breaks ties. The generated plan includes task times, explanations, evidence titles, and any tasks that did not fit. Automated tests cover retrieval, planning, and safety behavior.

## Setup instructions

Requirements: Python 3.10 or newer and `pip`. From the project directory:

1. Create a virtual environment:

   ```bash
   python -m venv .venv
   ```

2. Activate it:

   **Windows PowerShell**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   **Windows Command Prompt**
   ```bat
   .venv\Scripts\activate.bat
   ```

   **macOS or Linux**
   ```bash
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Run the tests:

   ```bash
   python -m pytest
   ```

5. Launch the app:

   ```bash
   python -m streamlit run app.py
   ```

6. Open the local URL printed by Streamlit. Enter the pet and owner details, add care tasks with durations and priorities, set the time available, then select **Generate schedule**. Review the retrieved note and explanation shown for each scheduled task.

No API key or network access is needed after dependencies are installed. Logs for retrieval, schedule generation, and errors are written to the terminal.

## Reproducible execution evidence

Run the end-to-end examples from the project root after installing the requirements:

```console
> python -m examples.run_demo
=== Dog schedule with limited time ===
Input: Mochi (dog), 25 minutes from 08:00
  - Morning walk: 20 min, high priority
  - Feed breakfast: 10 min, medium priority
Output: Daily care plan for Mochi (dog): 1 task(s) fit within 25 available minutes. 1 task(s) were left unscheduled due to the time limit.
  08:00-08:20 Morning walk
    Scheduled as a high-priority task. Retrieved guidance informed its placement: Keep the walk at the time and duration you entered; activity needs vary by pet.
    Evidence: Dog walking routine (75% keyword relevance)
  Deferred: Feed breakfast (time limit)

=== Cat schedule with matched and unmatched tasks ===
Input: Luna (cat), 40 minutes from 08:00
  - Organize supply shelf: 10 min, medium priority
  - Feed breakfast: 10 min, medium priority
  - Brush fur: 15 min, medium priority
Output: Daily care plan for Luna (cat): 3 task(s) fit within 40 available minutes.
  08:00-08:10 Feed breakfast
    Scheduled as a medium-priority task. Retrieved guidance informed its placement: Keep to the feeding schedule and instructions you already follow; this planner does not infer portions or meal frequency.
    Evidence: Feeding routine (100% keyword relevance)
  08:10-08:25 Brush fur
    Scheduled as a medium-priority task. Retrieved guidance informed its placement: Use the grooming task and duration you entered; coat and grooming needs vary.
    Evidence: Grooming routine (80% keyword relevance)
  08:25-08:35 Organize supply shelf
    Scheduled as a medium-priority task based on your input. No matching care note was found, so no additional care guidance was used.

=== Medication safety guardrail ===
Input: Rex (dog), 10 minutes from 08:00
  - Medication reminder: 5 min, high priority
Output: Daily care plan for Rex (dog): 1 task(s) fit within 10 available minutes.
  08:00-08:05 Medication reminder
    Scheduled as a high-priority task. Retrieved guidance informed its placement: Follow the medication instructions provided by your veterinarian. This planner cannot recommend changing a dose or timing.
    Evidence: Medication safety (80% keyword relevance)
```

These runs demonstrate that retrieved notes inform ordering and explanations, no extra care guidance is invented for an unmatched task, time limits defer work, and medication guidance retains a veterinary safety warning. The displayed percentages are keyword-overlap relevance scores, not calibrated confidence.

## Design decisions

- **Local knowledge and retrieval:** Bundled JSON notes and standard-library keyword matching keep setup reproducible and usable offline.
- **Grounded planning:** Retrieval runs for each task. The owner's priority remains the primary ordering rule; evidence relevance breaks ties. The generated explanation uses the matching note, so retrieval influences both scheduling and the response.
- **Graceful evidence gaps:** A task can still be scheduled from the owner's input when no note matches, but the explanation explicitly says no additional care guidance was used.
- **Safety boundary:** Medication-related notes direct users to their veterinarian rather than offering dosing changes. The assistant is a planning aid, not a medical system.
- **Trade-off:** Keyword retrieval is simple and transparent, but it can miss paraphrases or return a shallow match. The local notes are limited and are not a substitute for authoritative veterinary sources.

## Reliability and guardrail results

Re-run the automated checks with:

```console
> python -m pytest -q
........                                                                 [100%]
8 passed
```

The 8 tests check species-aware retrieval, evidence-based tie-breaking, owner-priority ordering, time limits, missing-evidence behavior, medication safety guidance, invalid inputs, and knowledge-base load errors.

The app also logs retrieval and schedule-generation activity and records exceptions when knowledge loading or schedule generation fails. These checks cover core code behavior, not veterinary accuracy or browser interactions. Retrieval scores are keyword-overlap measures, not calibrated AI confidence; retrieved notes and plans should still be reviewed by the owner.

## Portfolio artifact

**Code:** [PawPal+ on GitHub](https://github.com/earias31/ai110-module2show-pawpal-starter)

**What this project says about me as an AI engineer:** I care about building AI features that demonstrably affect application behavior, not just adding an AI label. I chose a small, testable RAG workflow, made evidence and missing matches visible, and added guardrails around medical topics. I also recognize that passing tests and keyword scores do not prove advice is correct, so human review and better-validated knowledge sources remain important.
