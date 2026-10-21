from datetime import date, time

from pawpal_system import Pet, ScheduledItem, Task, to_datetime


def make_task(task_id: str = "t1", duration_minutes: int = 30) -> Task:
    return Task(task_id, "Morning walk", "exercise", duration_minutes=duration_minutes, priority=3)


def make_pet() -> Pet:
    return Pet(pet_id="p1", name="Mochi", species="dog", breed="Shiba Inu")


def test_mark_done_changes_status():
    task = make_task()
    day = date(2026, 10, 21)
    item = ScheduledItem(
        task=task,
        pet=make_pet(),
        start_time=to_datetime(day, time(7, 0)),
        end_time=to_datetime(day, time(7, 30)),
    )
    assert item.is_done is False

    item.mark_done()

    assert item.is_done is True


def test_add_task_increases_task_count():
    pet = make_pet()
    assert len(pet.get_tasks()) == 0

    pet.add_task(make_task("t1"))
    assert len(pet.get_tasks()) == 1

    pet.add_task(make_task("t2"))
    assert len(pet.get_tasks()) == 2
