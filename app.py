import logging
from datetime import time

import streamlit as st

from pawpal import CareTask, PawPalAssistant

LOGGER = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.markdown(
    "Plan pet-care tasks using a local retrieval-augmented assistant. PawPal+ searches its "
    "care notes before planning and uses matching guidance in task ordering and explanations."
)

st.subheader("Pet and owner")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

time_col, start_col = st.columns(2)
with time_col:
    available_minutes = st.number_input(
        "Time available today (minutes)", min_value=0, max_value=1440, value=60
    )
with start_col:
    start_time = st.time_input("Plan starts at", value=time(8, 0))

st.markdown("### Tasks")
st.caption("Set task duration and priority. The assistant retrieves matching care notes.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

title_col, duration_col, priority_col = st.columns(3)
with title_col:
    task_title = st.text_input("Task title", value="Morning walk", key="task_title")
with duration_col:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with priority_col:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    if not task_title.strip():
        st.warning("Enter a task title before adding it.")
    else:
        st.session_state.tasks.append(
            {
                "title": task_title.strip(),
                "duration_minutes": int(duration),
                "priority": priority,
            }
        )
        st.success(f"Added {task_title.strip()}.")

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()
st.subheader("Generate a grounded schedule")
st.caption(
    "Owner priority comes first. Retrieved-note relevance breaks ties between tasks "
    "with the same priority."
)

if st.button("Generate schedule"):
    if not st.session_state.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        try:
            care_tasks = [
                CareTask(
                    title=task["title"],
                    duration_minutes=task["duration_minutes"],
                    priority=task["priority"],
                )
                for task in st.session_state.tasks
            ]
            plan = PawPalAssistant().generate_schedule(
                pet_name=pet_name,
                species=species,
                tasks=care_tasks,
                available_minutes=int(available_minutes),
                start_time=start_time,
            )
            st.success(plan.response)
            if owner_name.strip():
                st.caption(
                    f"Prepared for {owner_name.strip()}. Review the plan before following it."
                )

            if plan.scheduled:
                st.markdown("### Today's plan")
                for item in plan.scheduled:
                    st.markdown(
                        f"**{item.start_time}–{item.end_time} — {item.task.title}** "
                        f"({item.task.duration_minutes} min, {item.task.priority} priority)"
                    )
                    st.write(item.explanation)
                    if item.evidence:
                        st.caption(
                            f"Retrieved: {item.evidence.note.title} "
                            f"({item.evidence.note.source}; relevance {item.evidence.score:.0%})"
                        )

            if plan.deferred:
                st.markdown("### Not scheduled")
                for task in plan.deferred:
                    st.write(
                        f"- {task.title} ({task.duration_minutes} min, {task.priority} priority) "
                        "— not enough time remains in today's limit."
                    )

            st.info(
                "PawPal+ provides general planning support, not veterinary advice. "
                "Follow your veterinarian's instructions for medical care."
            )
        except (RuntimeError, ValueError) as error:
            LOGGER.exception("Schedule generation failed")
            st.error(f"Could not generate the schedule: {error}")
