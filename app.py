import uuid
from datetime import date, time, timedelta

import streamlit as st

from pawpal_system import (
    FREQUENCIES,
    PRIORITY_LABELS,
    Owner,
    Pet,
    ScheduledItem,
    Scheduler,
    Task,
    to_datetime,
)

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Plan your pets' care around your day.")

# Streamlit reruns this whole script on every click, so the Owner (and with it every
# pet and task) lives in session_state to survive reruns. Create it only once.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(owner_id="o1", name="Jordan")
owner: Owner = st.session_state.owner


def new_id() -> str:
    """Return a short unique id for a new pet or task."""
    return uuid.uuid4().hex[:8]


# --- Owner -------------------------------------------------------------------
st.subheader("Owner")
with st.form("owner_form"):
    name = st.text_input("Owner name", value=owner.name)
    col1, col2 = st.columns(2)
    with col1:
        day_start = st.time_input("Day starts", value=owner.day_start)
    with col2:
        day_end = st.time_input("Day ends", value=owner.day_end)

    has_block = bool(owner.blocked_time_slots)
    block_start, block_end = owner.blocked_time_slots[0] if has_block else (time(9, 0), time(17, 0))
    blocked = st.checkbox("I'm busy for part of the day (e.g. work)", value=has_block)
    col3, col4 = st.columns(2)
    with col3:
        block_start = st.time_input("Busy from", value=block_start)
    with col4:
        block_end = st.time_input("Busy until", value=block_end)

    if st.form_submit_button("Save owner"):
        try:
            # Owner checks its times when it's created, so build a new one and keep the pets.
            st.session_state.owner = Owner(
                owner_id=owner.owner_id,
                name=name,
                day_start=day_start,
                day_end=day_end,
                blocked_time_slots=[(block_start, block_end)] if blocked else [],
                pets=owner.pets,
            )
            st.rerun()
        except ValueError as e:
            st.error(str(e))

st.write(f"**{owner.name}** has **{owner.get_available_minutes()} free minutes** today.")

# --- Pets --------------------------------------------------------------------
st.subheader("Pets")
with st.form("pet_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        pet_name = st.text_input("Pet name")
    with col2:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with col3:
        breed = st.text_input("Breed")
    if st.form_submit_button("Add pet"):
        if pet_name.strip():
            owner.add_pet(Pet(pet_id=new_id(), name=pet_name.strip(), species=species, breed=breed.strip()))
            st.rerun()
        else:
            st.error("Give your pet a name.")

pets = owner.get_pets()
if not pets:
    st.info("No pets yet. Add one above.")

# --- Tasks -------------------------------------------------------------------
if pets:
    st.subheader("Tasks")
    with st.form("task_form", clear_on_submit=True):
        # Store the pet's id, not the Pet itself: Streamlit can hand back a copy of a
        # widget's value, and a task added to a copy would be lost.
        pets_by_id = {p.pet_id: p for p in pets}
        pet_id = st.selectbox("For which pet?", list(pets_by_id), format_func=lambda i: pets_by_id[i].name)
        col1, col2 = st.columns(2)
        with col1:
            task_name = st.text_input("Task", placeholder="Morning walk")
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
            category = st.text_input("Category", placeholder="exercise")
        with col2:
            # Values are 1/2/3; the user sees low/medium/high.
            priority = st.selectbox(
                "Priority", options=list(PRIORITY_LABELS), format_func=PRIORITY_LABELS.get, index=2
            )
            frequency = st.selectbox("Repeats", FREQUENCIES, index=1)
            start_date = st.date_input("Starting", value=date.today())
        if st.form_submit_button("Add task"):
            if not task_name.strip():
                st.error("Give the task a name.")
            else:
                try:
                    pets_by_id[pet_id].add_task(
                        Task(
                            task_id=new_id(),
                            name=task_name.strip(),
                            category=category.strip() or "general",
                            duration_minutes=int(duration),
                            priority=priority,
                            frequency=frequency,
                            start_date=start_date,
                        )
                    )
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))

    for pet in pets:
        st.markdown(f"**{pet.name}** ({pet.breed or pet.species})")
        tasks = pet.get_tasks()
        if not tasks:
            st.caption("No tasks yet.")
        for task in tasks:
            col1, col2 = st.columns([5, 1])
            with col1:
                st.write(
                    f"{task.name} · {task.duration_minutes} min · "
                    f"{PRIORITY_LABELS[task.priority]} priority · {task.frequency}"
                )
            with col2:
                if st.button("Remove", key=f"remove_{task.task_id}"):
                    pet.remove_task(task)
                    st.rerun()

# --- Schedule ----------------------------------------------------------------
st.divider()
st.subheader("Build Schedule")
plan_date = st.date_input("Plan for", value=date.today())

if st.button("Generate schedule", type="primary"):
    scheduler = Scheduler(scheduler_id=new_id(), date=plan_date)
    scheduler.generate_plan(owner)
    st.session_state.scheduler = scheduler

if "scheduler" in st.session_state:
    scheduler: Scheduler = st.session_state.scheduler
    schedule = scheduler.get_schedule()  # sorted with sort_by_time
    st.markdown(f"### Today's Schedule · {scheduler.date:%A, %B %d}")

    # --- At a glance ---
    done_count = len(scheduler.filter_items(is_done=True))
    planned_minutes = sum(item.task.duration_minutes for item in schedule)
    col1, col2, col3 = st.columns(3)
    col1.metric("Tasks planned", len(schedule))
    col2.metric("Done", f"{done_count} / {len(schedule)}")
    col3.metric("Care time", f"{planned_minutes} min", help=f"{owner.get_available_minutes()} free minutes today")

    # --- Conflicts (Scheduler.find_conflicts) ---
    conflicts = scheduler.find_conflicts()
    if conflicts:
        st.warning(
            f"**{len(conflicts)} time conflict{'s' if len(conflicts) > 1 else ''}**\n\n"
            + "\n".join(f"- {c.removeprefix('Conflict: ')}" for c in conflicts),
            icon="⚠️",
        )
    elif schedule:
        st.success("No time conflicts: every task has its own slot.", icon="✅")

    if not schedule:
        st.info("Nothing scheduled. Add tasks that are due on this day.", icon="📭")
    else:
        # --- Filters (Scheduler.filter_items, which also sorts by time) ---
        col1, col2 = st.columns(2)
        with col1:
            pet_filter = st.selectbox("Pet", ["All pets"] + sorted({i.pet.name for i in schedule}))
        with col2:
            status_filter = st.segmented_control(
                "Status", ["All", "To do", "Done"], default="All", key="status_filter"
            ) or "All"
        items = scheduler.filter_items(
            is_done={"All": None, "To do": False, "Done": True}[status_filter],
            pet_name=None if pet_filter == "All pets" else pet_filter,
        )

        if not items:
            st.info("No tasks match these filters.", icon="🔍")
        else:
            # One row per item; only the Done column can be edited.
            rows = [
                {
                    "Done": item.is_done,
                    "Time": f"{item.start_time:%H:%M} – {item.end_time:%H:%M}",
                    "Task": item.task.name,
                    "Pet": item.pet.name,
                    "Priority": PRIORITY_LABELS[item.task.priority].capitalize(),
                    "Minutes": item.task.duration_minutes,
                    "Repeats": item.task.frequency.capitalize(),
                }
                for item in items
            ]
            edited = st.data_editor(
                rows,
                key=f"schedule_{pet_filter}_{status_filter}",  # fresh editor state per filter
                hide_index=True,
                width="stretch",
                disabled=["Time", "Task", "Pet", "Priority", "Minutes", "Repeats"],
                column_config={
                    "Done": st.column_config.CheckboxColumn("Done", help="Tick when finished", width="small"),
                    "Minutes": st.column_config.NumberColumn("Minutes", format="%d min"),
                },
            )
            changed = False
            for item, row in zip(items, edited):
                if row["Done"] and not item.is_done:
                    item.mark_done()
                    changed = True
                elif not row["Done"] and item.is_done:
                    item.is_done = False  # un-ticked by mistake
                    changed = True
            if changed:
                st.rerun()

    # --- Book at a fixed time (Scheduler.add_item); overlaps show up as warnings above ---
    all_tasks = {(pet.pet_id, task.task_id): (pet, task) for pet in owner.get_pets() for task in pet.get_tasks()}
    if all_tasks:
        with st.expander("Book a task at a fixed time (e.g. a vet visit)"):
            with st.form("book_form"):
                key = st.selectbox(
                    "Task",
                    list(all_tasks),
                    format_func=lambda k: f"{all_tasks[k][1].name} ({all_tasks[k][0].name})",
                )
                at = st.time_input("At", value=time(7, 0))
                if st.form_submit_button("Book"):
                    pet, task = all_tasks[key]
                    start = to_datetime(scheduler.date, at)
                    scheduler.add_item(
                        ScheduledItem(task, pet, start, start + timedelta(minutes=task.duration_minutes))
                    )
                    st.rerun()
            st.caption("Booked items are kept until you generate the schedule again.")

    # --- Why this plan (Scheduler.reasoning_notes) ---
    with st.expander("Why this plan", expanded=True):
        st.caption("Tasks are placed highest priority first, each at the earliest free time.")
        for note in scheduler.reasoning_notes.splitlines():
            if note.startswith(("Skipped", "Couldn't")):
                st.warning(note, icon="⏭️")
            else:
                st.info(note, icon="ℹ️")
