"""Run three reproducible end-to-end PawPal+ RAG examples."""

from pawpal import CareTask, PawPalAssistant


EXAMPLES = (
    {
        "title": "Dog schedule with limited time",
        "pet_name": "Mochi",
        "species": "dog",
        "available_minutes": 25,
        "tasks": [
            CareTask("Morning walk", 20, "high"),
            CareTask("Feed breakfast", 10, "medium"),
        ],
    },
    {
        "title": "Cat schedule with matched and unmatched tasks",
        "pet_name": "Luna",
        "species": "cat",
        "available_minutes": 40,
        "tasks": [
            CareTask("Organize supply shelf", 10, "medium"),
            CareTask("Feed breakfast", 10, "medium"),
            CareTask("Brush fur", 15, "medium"),
        ],
    },
    {
        "title": "Medication safety guardrail",
        "pet_name": "Rex",
        "species": "dog",
        "available_minutes": 10,
        "tasks": [CareTask("Medication reminder", 5, "high")],
    },
)


def main() -> None:
    assistant = PawPalAssistant()
    for example in EXAMPLES:
        print(f"\n=== {example['title']} ===")
        print(
            f"Input: {example['pet_name']} ({example['species']}), "
            f"{example['available_minutes']} minutes from 08:00"
        )
        for task in example["tasks"]:
            print(
                f"  - {task.title}: {task.duration_minutes} min, "
                f"{task.priority} priority"
            )

        plan = assistant.generate_schedule(
            pet_name=example["pet_name"],
            species=example["species"],
            tasks=example["tasks"],
            available_minutes=example["available_minutes"],
        )
        print(f"Output: {plan.response}")
        for item in plan.scheduled:
            print(f"  {item.start_time}-{item.end_time} {item.task.title}")
            print(f"    {item.explanation}")
            if item.evidence:
                print(
                    f"    Evidence: {item.evidence.note.title} "
                    f"({item.evidence.score:.0%} keyword relevance)"
                )
        for task in plan.deferred:
            print(f"  Deferred: {task.title} (time limit)")


if __name__ == "__main__":
    main()
