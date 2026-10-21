"""PawPal+ core classes.

Skeleton generated from diagrams/uml_draft.mmd. Methods are stubs (no logic yet).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta

# Display text for each priority number (higher number = more important).
PRIORITY_LABELS = {1: "low", 2: "medium", 3: "high"}

# A (start, end) pair of clock times, e.g. (time(9, 0), time(17, 0)) for 9am to 5pm.
TimeSlot = tuple[time, time]

# How often a task repeats.
FREQUENCIES = ("once", "daily", "weekly")


def to_datetime(day: date, t: time) -> datetime:
    """Combine a date and a clock time so you can add timedeltas to it."""
    return datetime.combine(day, t)


def minutes_between(start: time, end: time) -> int:
    """Return the number of minutes from start to end on the same day."""
    any_day = date.min  # the date doesn't matter, only the difference between the times
    return int((to_datetime(any_day, end) - to_datetime(any_day, start)).total_seconds() // 60)


@dataclass
class Task:
    """A single pet care activity, such as a walk, feeding, or medication."""

    task_id: str
    name: str
    category: str
    duration_minutes: int
    priority: int  # 1, 2, or 3 (a key of PRIORITY_LABELS)
    frequency: str = "once"  # one of FREQUENCIES
    start_date: date = field(default_factory=date.today)  # first day the task is due

    def is_due_on(self, day: date) -> bool:
        """Return True if this task should be scheduled on the given day.

        - "once": due only on start_date
        - "daily": due every day from start_date on
        - "weekly": due every 7 days from start_date, i.e. (day - start_date).days % 7 == 0
        Never due before start_date.
        """
        pass

    def conflicts_with(self, other_task: Task) -> bool:
        """Return True if this task conflicts with other_task."""
        pass


@dataclass
class Pet:
    """A pet and the care tasks it needs."""

    pet_id: str
    name: str
    species: str
    breed: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet."""
        pass

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet."""
        pass

    def get_tasks(self) -> list[Task]:
        """Return all of this pet's tasks."""
        pass


@dataclass
class Owner:
    """A pet owner, the part of the day they are free, and their pets."""

    owner_id: str
    name: str
    day_start: time = time(7, 0)  # earliest time a task can be scheduled
    day_end: time = time(21, 0)  # latest time a task can finish
    blocked_time_slots: list[TimeSlot] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        pass

    def get_pets(self) -> list[Pet]:
        """Return all of this owner's pets."""
        pass

    def get_all_tasks(self) -> list[Task]:
        """Return the tasks of every pet this owner has, combined into one list."""
        pass

    def get_available_minutes(self) -> int:
        """Return the free minutes between day_start and day_end, minus blocked_time_slots.

        Use minutes_between() to measure the day window and each blocked slot.
        """
        pass


@dataclass
class ScheduledItem:
    """A task placed at a specific time slot for a specific pet."""

    task: Task
    pet: Pet
    start_time: datetime
    end_time: datetime
    is_done: bool = False

    def mark_done(self) -> None:
        """Mark this scheduled item as completed."""
        pass


@dataclass
class Scheduler:
    """Builds and holds one day's schedule across all of an owner's pets."""

    scheduler_id: str
    date: date
    scheduled_items: list[ScheduledItem] = field(default_factory=list)
    reasoning_notes: str = ""

    def generate_plan(self, owner: Owner) -> None:
        """Build the day's schedule from all of the owner's pets' tasks.

        Uses owner.get_available_minutes() as one shared time budget, places
        tasks between owner.day_start and owner.day_end, and avoids
        owner.blocked_time_slots.

        Starts from an empty plan, so calling it again replaces the previous
        plan instead of adding to it.
        """
        self.scheduled_items = []
        self.reasoning_notes = ""
        # TODO: sort, filter, and assign times to the owner's due tasks.

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered from highest to lowest priority."""
        pass

    def filter_by_time_available(self, tasks: list[Task], minutes: int) -> list[Task]:
        """Return the tasks that fit within the given number of minutes.

        Expects tasks already sorted by priority (see sort_by_priority). Walks the
        list in order: if a task fits in the minutes left, keep it and subtract its
        duration; if it doesn't fit, skip it and keep going, so smaller tasks
        further down can still use the remaining time.
        """
        pass

    def assign_times_and_build_schedule(
        self, tasks: list[Task], day_start: time, day_end: time, blocked_times: list[TimeSlot]
    ) -> list[ScheduledItem]:
        """Give each task a start/end time between day_start and day_end that avoids blocked_times.

        Convert times with to_datetime(self.date, ...) and add
        timedelta(minutes=task.duration_minutes) to get each end time.
        """
        pass

    def get_schedule(self) -> list[ScheduledItem]:
        """Return the scheduled items in time order."""
        pass

    def explain(self) -> str:
        """Return a human-readable explanation of why the plan looks the way it does."""
        pass
