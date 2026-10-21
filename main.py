from datetime import date, time

from pawpal_system import PRIORITY_LABELS, Task, Pet, Owner, Scheduler


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

    mochi.add_task(Task("t1", "Morning walk", "exercise", duration_minutes=30, priority=3, frequency="daily"))
    mochi.add_task(Task("t2", "Training", "enrichment", duration_minutes=15, priority=2, frequency="daily"))
    luna.add_task(Task("t3", "Feeding", "food", duration_minutes=10, priority=3, frequency="daily"))
    luna.add_task(Task("t4", "Play session", "enrichment", duration_minutes=20, priority=1, frequency="daily"))

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

    print("\nToday's Schedule")
    for item in scheduler.get_schedule():
        print(f"  {item.start_time:%H:%M}-{item.end_time:%H:%M}  {item.task.name} ({item.pet.name})")


if __name__ == "__main__":
    main()
