from datetime import date, time, timedelta

from pawpal_system import PRIORITY_LABELS, Owner, Pet, ScheduledItem, Scheduler, Task, to_datetime


def print_items(title: str, items: list[ScheduledItem]) -> None:
    """Print a heading and one line per scheduled item."""
    print(f"\n{title}")
    if not items:
        print("  (none)")
    for item in items:
        status = "done" if item.is_done else "todo"
        print(
            f"  {item.start_time:%H:%M}-{item.end_time:%H:%M}  {item.task.name} ({item.pet.name}) "
            f"[{PRIORITY_LABELS[item.task.priority]}, {status}]"
        )


def print_warnings(warnings: list[str]) -> None:
    """Print each conflict warning, or a note that there are none."""
    if not warnings:
        print("  No conflicts.")
    for warning in warnings:
        print(f"  WARNING: {warning}")


def main() -> None:
    owner = Owner(
        owner_id="o1",
        name="Jordan",
        day_start=time(7, 0),
        day_end=time(21, 0),
        blocked_time_slots=[(time(9, 0), time(17, 0))],  # at work
    )

    mochi = Pet(pet_id="p1", name="Mochi", species="dog", breed="Shiba Inu")
    luna = Pet(pet_id="p2", name="Luna", species="cat", breed="Tabby")

    # Added deliberately out of order: low priority first, high priority last, and a
    # long hike that won't fit before work, so the scheduler places tasks out of time order.
    luna.add_task(Task("t1", "Brushing", "grooming", duration_minutes=15, priority=1, frequency="daily"))
    mochi.add_task(Task("t2", "Training", "enrichment", duration_minutes=30, priority=2, frequency="daily"))
    luna.add_task(Task("t3", "Play session", "enrichment", duration_minutes=20, priority=1, frequency="daily"))
    mochi.add_task(Task("t4", "Long hike", "exercise", duration_minutes=90, priority=3, frequency="daily"))
    luna.add_task(Task("t5", "Feeding", "food", duration_minutes=10, priority=3, frequency="daily"))

    owner.add_pet(mochi)
    owner.add_pet(luna)

    print(f"Owner: {owner.name} ({owner.get_available_minutes()} free minutes today)")
    for pet in owner.get_pets():
        print(f"  - {pet.name}, a {pet.breed} {pet.species}")
        for task in pet.get_tasks():
            print(
                f"      * {task.name}: {task.duration_minutes} min, "
                f"{PRIORITY_LABELS[task.priority]} priority, {task.frequency}"
            )

    scheduler = Scheduler(scheduler_id="s1", date=date.today())
    scheduler.generate_plan(owner)

    # --- Sorting ---------------------------------------------------------------
    # The scheduler already keeps its items in time order, so mix up a copy on purpose
    # (alphabetical by task name) to show sort_by_time putting them back.
    jumbled = sorted(scheduler.scheduled_items, key=lambda item: item.task.name)
    print_items("Jumbled (alphabetical by task name)", jumbled)
    print_items("Today's Schedule (sort_by_time)", scheduler.sort_by_time(jumbled))

    # --- Filtering -------------------------------------------------------------
    # Pretend the first two things this morning are already finished.
    for item in scheduler.get_schedule()[:2]:
        item.mark_done()

    print_items("Done (filter_items is_done=True)", scheduler.filter_items(is_done=True))
    print_items("Still to do (filter_items is_done=False)", scheduler.filter_items(is_done=False))
    print_items("Luna only (filter_items pet_name='luna')", scheduler.filter_items(pet_name="luna"))
    print_items(
        "Mochi, still to do (filter_items is_done=False, pet_name='Mochi')",
        scheduler.filter_items(is_done=False, pet_name="Mochi"),
    )
    print_items("Unknown pet (filter_items pet_name='Rex')", scheduler.filter_items(pet_name="Rex"))

    # --- Conflict detection ----------------------------------------------------
    print("\nConflict check on the generated plan:")
    print_warnings(scheduler.find_conflicts())

    # Book Mochi's meds by hand at 07:00, the same time as Luna's Feeding.
    meds = Task("t6", "Medication", "health", duration_minutes=5, priority=3, frequency="once")
    mochi.add_task(meds)
    meds_start = to_datetime(scheduler.date, time(7, 0))
    scheduler.add_item(ScheduledItem(meds, mochi, meds_start, meds_start + timedelta(minutes=5)))

    print_items("Schedule after booking Medication at 07:00", scheduler.get_schedule())
    print("\nConflict check after booking:")
    print_warnings(scheduler.find_conflicts())


if __name__ == "__main__":
    main()
