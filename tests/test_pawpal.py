from datetime import date, time, timedelta

from pawpal_system import Owner, Pet, ScheduledItem, Scheduler, Task, to_datetime

DAY = date(2026, 10, 21)  # fixed date so tests don't depend on today


def make_task(task_id: str = "t1", duration_minutes: int = 30) -> Task:
    return Task(task_id, "Morning walk", "exercise", duration_minutes=duration_minutes, priority=3)


def make_pet() -> Pet:
    return Pet(pet_id="p1", name="Mochi", species="dog", breed="Shiba Inu")


def make_item(task: Task, pet: Pet, hour: int, minute: int = 0) -> ScheduledItem:
    """Book task for pet at hour:minute on DAY, lasting the task's duration."""
    start = to_datetime(DAY, time(hour, minute))
    return ScheduledItem(task, pet, start, start + timedelta(minutes=task.duration_minutes))


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


def test_sort_by_time_returns_chronological_order():
    pet = make_pet()
    evening = make_item(make_task("t1", 30), pet, 17, 0)
    morning = make_item(make_task("t2", 30), pet, 7, 0)
    long_at_8 = make_item(make_task("t3", 30), pet, 8, 0)
    short_at_8 = make_item(make_task("t4", 10), pet, 8, 0)
    scheduler = Scheduler("s1", DAY)

    result = scheduler.sort_by_time([evening, long_at_8, morning, short_at_8])

    # Same start time: the one that ends first comes first.
    assert result == [morning, short_at_8, long_at_8, evening]


def test_daily_task_is_scheduled_again_the_next_day_after_done():
    # A daily task isn't copied when it's completed: completion is stored on that day's
    # ScheduledItem, and the same Task is due again tomorrow via is_due_on().
    pet = make_pet()
    walk = Task("t1", "Morning walk", "exercise", duration_minutes=30, priority=3, frequency="daily", start_date=DAY)
    pet.add_task(walk)
    owner = Owner("o1", "Jordan")
    owner.add_pet(pet)

    today = Scheduler("s1", DAY)
    today.generate_plan(owner)
    today.get_schedule()[0].mark_done()

    tomorrow = Scheduler("s2", DAY + timedelta(days=1))
    tomorrow.generate_plan(owner)
    next_day_items = tomorrow.get_schedule()

    assert len(next_day_items) == 1
    assert next_day_items[0].task is walk
    assert next_day_items[0].start_time.date() == DAY + timedelta(days=1)
    assert next_day_items[0].is_done is False
    assert len(pet.get_tasks()) == 1  # no duplicate task was created


def test_find_conflicts_flags_items_at_the_same_time():
    pet = make_pet()
    scheduler = Scheduler("s1", DAY)
    scheduler.add_item(make_item(make_task("t1", 30), pet, 7, 0))
    scheduler.add_item(make_item(make_task("t2", 10), pet, 7, 0))  # same start time
    scheduler.add_item(make_item(make_task("t3", 30), pet, 7, 30))  # starts as the first ends: fine

    warnings = scheduler.find_conflicts()

    assert len(warnings) == 1
    assert "07:00" in warnings[0]


def test_filter_items_by_status_and_pet_name():
    mochi = make_pet()
    luna = Pet(pet_id="p2", name="Luna", species="cat", breed="Tabby")
    scheduler = Scheduler("s1", DAY)
    mochi_walk = make_item(make_task("t1"), mochi, 7, 0)
    luna_feed = make_item(make_task("t2"), luna, 8, 0)
    mochi_play = make_item(make_task("t3"), mochi, 17, 0)
    for item in (mochi_walk, luna_feed, mochi_play):
        scheduler.add_item(item)
    mochi_walk.mark_done()

    assert scheduler.filter_items(is_done=True) == [mochi_walk]
    assert scheduler.filter_items(is_done=False) == [luna_feed, mochi_play]
    assert scheduler.filter_items(pet_name="luna") == [luna_feed]
    assert scheduler.filter_items(is_done=False, pet_name="Mochi") == [mochi_play]


def test_filter_by_time_available_skips_long_task_and_keeps_going():
    scheduler = Scheduler("s1", DAY)
    meds = Task("t1", "Vet meds", "health", duration_minutes=10, priority=3)
    hike = Task("t2", "Long hike", "exercise", duration_minutes=60, priority=3)
    feeding = Task("t3", "Feeding", "food", duration_minutes=15, priority=2)
    brushing = Task("t4", "Brushing", "grooming", duration_minutes=10, priority=1)

    kept = scheduler.filter_by_time_available([meds, hike, feeding, brushing], minutes=40)

    # The hike doesn't fit in the 30 min left after meds, but smaller tasks after it still do.
    assert kept == [meds, feeding, brushing]
