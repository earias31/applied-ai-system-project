"""Local retrieval-augmented pet-care planning."""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path

LOGGER = logging.getLogger(__name__)
DEFAULT_KNOWLEDGE_PATH = Path(__file__).parent / "knowledge" / "pet_care_notes.json"
PRIORITY_ORDER = {"high": 3, "medium": 2, "low": 1}
SYNONYMS = {
    "walk": {"exercise", "activity"},
    "feed": {"feeding", "food"},
    "feeding": {"feed", "food"},
    "brush": {"groom", "grooming", "coat"},
    "groom": {"brush", "grooming", "coat"},
    "litter": {"clean", "box"},
    "medicine": {"medication", "dose", "prescription"},
    "medication": {"medicine", "dose", "prescription"},
}


@dataclass(frozen=True)
class CareTask:
    title: str
    duration_minutes: int
    priority: str

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("Task title cannot be empty.")
        if self.duration_minutes < 1:
            raise ValueError("Task duration must be at least one minute.")
        if self.priority not in PRIORITY_ORDER:
            raise ValueError("Priority must be low, medium, or high.")


@dataclass(frozen=True)
class CareNote:
    title: str
    species: tuple[str, ...]
    keywords: frozenset[str]
    guidance: str
    source: str


@dataclass(frozen=True)
class RetrievedNote:
    note: CareNote
    score: float


@dataclass(frozen=True)
class PlannedTask:
    task: CareTask
    start_time: str
    end_time: str
    explanation: str
    evidence: RetrievedNote | None


@dataclass(frozen=True)
class CarePlan:
    pet_name: str
    species: str
    available_minutes: int
    scheduled: tuple[PlannedTask, ...]
    deferred: tuple[CareTask, ...]
    response: str


class CareNoteRetriever:
    """Find relevant local notes using species filtering and keyword overlap."""

    def __init__(self, knowledge_path: Path = DEFAULT_KNOWLEDGE_PATH) -> None:
        try:
            raw_notes = json.loads(knowledge_path.read_text(encoding="utf-8"))
            self.notes = tuple(self._parse_note(item) for item in raw_notes)
            if not self.notes:
                raise ValueError("The pet-care knowledge base contains no notes.")
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as error:
            LOGGER.exception("Could not load pet-care knowledge from %s", knowledge_path)
            raise RuntimeError(f"Could not load pet-care knowledge: {error}") from error

    @staticmethod
    def _parse_note(item: object) -> CareNote:
        if not isinstance(item, dict):
            raise ValueError("Each knowledge-base entry must be an object.")
        try:
            title = item["title"]
            species = item["species"]
            keywords = item["keywords"]
            guidance = item["guidance"]
            source = item["source"]
        except KeyError as error:
            raise ValueError(f"Knowledge-base entry is missing {error.args[0]!r}.") from error
        if (
            not isinstance(title, str)
            or not isinstance(species, list)
            or not all(isinstance(value, str) for value in species)
            or not isinstance(keywords, list)
            or not all(isinstance(value, str) for value in keywords)
            or not isinstance(guidance, str)
            or not isinstance(source, str)
        ):
            raise ValueError("Knowledge-base entry fields have invalid types.")
        return CareNote(
            title=title,
            species=tuple(value.lower() for value in species),
            keywords=frozenset(word for value in keywords for word in _tokenize(value)),
            guidance=guidance,
            source=source,
        )

    def retrieve(
        self, task_title: str, species: str, limit: int = 1
    ) -> tuple[RetrievedNote, ...]:
        if limit < 1:
            raise ValueError("Retrieval limit must be at least one.")
        task_terms = set(_tokenize(task_title))
        expanded_terms = task_terms | {
            synonym
            for term in task_terms
            for synonym in SYNONYMS.get(term, set())
        }
        if not expanded_terms:
            return ()

        candidates: list[RetrievedNote] = []
        for note in self.notes:
            if species.lower() not in note.species and "all" not in note.species:
                continue
            matched_terms = expanded_terms & note.keywords
            if matched_terms:
                score = len(matched_terms) / len(expanded_terms)
                candidates.append(RetrievedNote(note=note, score=score))
        candidates.sort(key=lambda result: (-result.score, result.note.title))
        results = tuple(candidates[:limit])
        LOGGER.info(
            "Retrieved %d note(s) for task=%r species=%s",
            len(results),
            task_title,
            species,
        )
        return results


class PawPalAssistant:
    """Build a time-limited plan whose explanations use retrieved care notes."""

    def __init__(self, retriever: CareNoteRetriever | None = None) -> None:
        self.retriever = retriever or CareNoteRetriever()

    def generate_schedule(
        self,
        pet_name: str,
        species: str,
        tasks: list[CareTask],
        available_minutes: int,
        start_time: time = time(8, 0),
    ) -> CarePlan:
        if not pet_name.strip():
            raise ValueError("Pet name cannot be empty.")
        if species.lower() not in {"dog", "cat", "other"}:
            raise ValueError("Species must be dog, cat, or other.")
        if not 0 <= available_minutes <= 1440:
            raise ValueError("Available time must be between 0 and 1440 minutes.")
        if not tasks:
            raise ValueError("Add at least one task before generating a schedule.")

        evidence_by_task: dict[int, RetrievedNote] = {}
        for index, task in enumerate(tasks):
            results = self.retriever.retrieve(task.title, species)
            if results:
                evidence_by_task[index] = results[0]
        ordered_tasks = sorted(
            enumerate(tasks),
            key=lambda item: (
                -PRIORITY_ORDER[item[1].priority],
                -evidence_by_task[item[0]].score if item[0] in evidence_by_task else 0,
                item[0],
            ),
        )

        current_time = datetime.combine(date.today(), start_time)
        remaining_minutes = available_minutes
        scheduled: list[PlannedTask] = []
        deferred: list[CareTask] = []

        for index, task in ordered_tasks:
            if task.duration_minutes > remaining_minutes:
                deferred.append(task)
                continue

            end_time = current_time + timedelta(minutes=task.duration_minutes)
            evidence = evidence_by_task.get(index)
            if evidence:
                explanation = (
                    f"Scheduled as a {task.priority}-priority task. "
                    f"Retrieved guidance informed its placement: {evidence.note.guidance}"
                )
            else:
                explanation = (
                    f"Scheduled as a {task.priority}-priority task based on your input. "
                    "No matching care note was found, so no additional care guidance was used."
                )
            scheduled.append(
                PlannedTask(
                    task=task,
                    start_time=current_time.strftime("%H:%M"),
                    end_time=end_time.strftime("%H:%M"),
                    explanation=explanation,
                    evidence=evidence,
                )
            )
            current_time = end_time
            remaining_minutes -= task.duration_minutes

        if scheduled:
            response = (
                f"Daily care plan for {pet_name} ({species}): "
                f"{len(scheduled)} task(s) fit within {available_minutes} available minutes."
            )
        else:
            response = (
                f"No tasks fit within the {available_minutes} minutes available for "
                f"{pet_name} ({species})."
            )
        if deferred:
            response += f" {len(deferred)} task(s) were left unscheduled due to the time limit."
        LOGGER.info(
            "Generated plan for pet=%r scheduled=%d deferred=%d available_minutes=%d",
            pet_name,
            len(scheduled),
            len(deferred),
            available_minutes,
        )
        return CarePlan(
            pet_name=pet_name,
            species=species,
            available_minutes=available_minutes,
            scheduled=tuple(scheduled),
            deferred=tuple(deferred),
            response=response,
        )


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())
