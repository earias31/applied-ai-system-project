from pathlib import Path

import pytest

from pawpal import CareNoteRetriever, CareTask, PawPalAssistant


@pytest.fixture
def assistant() -> PawPalAssistant:
    return PawPalAssistant()


def test_retriever_finds_species_relevant_walk_note() -> None:
    retriever = CareNoteRetriever()

    dog_results = retriever.retrieve("Morning walk", "dog")
    cat_results = retriever.retrieve("Morning walk", "cat")

    assert dog_results
    assert dog_results[0].note.title == "Dog walking routine"
    assert not cat_results


def test_retrieved_relevance_breaks_equal_priority_tie(
    assistant: PawPalAssistant,
) -> None:
    plan = assistant.generate_schedule(
        pet_name="Mochi",
        species="dog",
        tasks=[
            CareTask("Organize toy basket", 10, "medium"),
            CareTask("Morning walk", 10, "medium"),
        ],
        available_minutes=30,
    )

    assert [item.task.title for item in plan.scheduled] == [
        "Morning walk",
        "Organize toy basket",
    ]
    assert "Retrieved guidance informed its placement" in plan.scheduled[0].explanation


def test_owner_priority_overrides_retrieval_relevance(
    assistant: PawPalAssistant,
) -> None:
    plan = assistant.generate_schedule(
        pet_name="Mochi",
        species="dog",
        tasks=[
            CareTask("Morning walk", 10, "low"),
            CareTask("Call the groomer", 10, "high"),
        ],
        available_minutes=30,
    )

    assert [item.task.title for item in plan.scheduled] == [
        "Call the groomer",
        "Morning walk",
    ]


def test_schedule_respects_time_limit_and_reports_deferred_task(
    assistant: PawPalAssistant,
) -> None:
    plan = assistant.generate_schedule(
        pet_name="Mochi",
        species="dog",
        tasks=[
            CareTask("Morning walk", 20, "high"),
            CareTask("Feed breakfast", 10, "medium"),
        ],
        available_minutes=25,
    )

    assert [item.task.title for item in plan.scheduled] == ["Morning walk"]
    assert [task.title for task in plan.deferred] == ["Feed breakfast"]
    assert "left unscheduled due to the time limit" in plan.response


def test_unknown_task_is_not_given_invented_care_guidance(
    assistant: PawPalAssistant,
) -> None:
    plan = assistant.generate_schedule(
        pet_name="Mochi",
        species="dog",
        tasks=[CareTask("Organize toy basket", 5, "low")],
        available_minutes=10,
    )

    assert plan.scheduled[0].evidence is None
    assert "No matching care note was found" in plan.scheduled[0].explanation


def test_medication_task_uses_safety_note(assistant: PawPalAssistant) -> None:
    plan = assistant.generate_schedule(
        pet_name="Mochi",
        species="dog",
        tasks=[CareTask("Medication reminder", 5, "high")],
        available_minutes=10,
    )

    item = plan.scheduled[0]
    assert item.evidence is not None
    assert item.evidence.note.title == "Medication safety"
    assert "cannot recommend changing a dose or timing" in item.explanation


def test_rejects_invalid_plan_inputs(assistant: PawPalAssistant) -> None:
    with pytest.raises(ValueError, match="at least one task"):
        assistant.generate_schedule("Mochi", "dog", [], 30)

    with pytest.raises(ValueError, match="between 0 and 1440"):
        assistant.generate_schedule(
            "Mochi", "dog", [CareTask("Walk", 10, "high")], 1441
        )


def test_reports_invalid_knowledge_base_path() -> None:
    with pytest.raises(RuntimeError, match="Could not load pet-care knowledge"):
        CareNoteRetriever(Path("missing-pet-care-notes.json"))
