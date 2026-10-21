"""PawPal+ core classes.

Classes follow diagrams/uml_draft.mmd.
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

    def __post_init__(self) -> None:
        """Reject invalid values as soon as the task is created."""
        if self.duration_minutes <= 0:
            raise ValueError(f"duration_minutes must be positive, got {self.duration_minutes}")
        if self.priority not in PRIORITY_LABELS:
            raise ValueError(f"priority must be one of {list(PRIORITY_LABELS)}, got {self.priority}")
        if self.frequency not in FREQUENCIES:
            raise ValueError(f"frequency must be one of {FREQUENCIES}, got {self.frequency!r}")

    def is_due_on(self, day: date) -> bool:
        """Return True if this task should be scheduled on the given day.

        - "once": due only on start_date
        - "daily": due every day from start_date on
        - "weekly": due every 7 days from start_date, i.e. (day - start_date).days % 7 == 0
        Never due before start_date.
        """
        if day < self.start_date:
            return False
        if self.frequency == "once":
            return day == self.start_date
        if self.frequency == "daily":
            return True
        return (day - self.start_date).days % 7 == 0  # weekly


@dataclass
class Pet:
    """A pet and the care tasks it needs."""

    pet_id: str
    name: str
    species: str
    breed: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task for this pet. Raises ValueError if its task_id is already used."""
        if any(existing.task_id == task.task_id for existing in self.tasks):
            raise ValueError(f"{self.name} already has a task with id {task.task_id!r}")
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet, matched by task_id. Raises ValueError if not found."""
        for i, existing in enumerate(self.tasks):
            if existing.task_id == task.task_id:
                del self.tasks[i]
                return
        raise ValueError(f"{self.name} has no task with id {task.task_id!r}")

    def get_tasks(self) -> list[Task]:
        """Return a copy of this pet's tasks, so callers can't change the pet's list by accident."""
        return list(self.tasks)


@dataclass
class Owner:
    """A pet owner, the part of the day they are free, and their pets."""

    owner_id: str
    name: str
    day_start: time = time(7, 0)  # earliest time a task can be scheduled
    day_end: time = time(21, 0)  # latest time a task can finish
    blocked_time_slots: list[TimeSlot] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Reject a day window or blocked slot whose start isn't before its end."""
        if self.day_start >= self.day_end:
            raise ValueError(f"day_start ({self.day_start}) must be before day_end ({self.day_end})")
        for start, end in self.blocked_time_slots:
            if start >= end:
                raise ValueError(f"blocked slot start ({start}) must be before its end ({end})")

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner. Raises ValueError if its pet_id is already used."""
        if any(existing.pet_id == pet.pet_id for existing in self.pets):
            raise ValueError(f"{self.name} already has a pet with id {pet.pet_id!r}")
        self.pets.append(pet)

    def get_pets(self) -> list[Pet]:
        """Return a copy of this owner's pets, so callers can't change the owner's list by accident."""
        return list(self.pets)

    def get_all_tasks(self) -> list[Task]:
        """Return the tasks of every pet this owner has, combined into one list."""
        return [task for pet in self.pets for task in pet.get_tasks()]

    def get_available_minutes(self) -> int:
        """Return the free minutes between day_start and day_end, minus blocked_time_slots.

        Blocked slots are trimmed to the day window, and overlapping slots are
        merged first so the same minutes are never subtracted twice.
        """
        # Trim each slot to the day window, dropping any that fall completely outside it.
        trimmed = []
        for start, end in self.blocked_time_slots:
            start, end = max(start, self.day_start), min(end, self.day_end)
            if start < end:
                trimmed.append((start, end))

        # Merge overlapping or touching slots, e.g. 9-11 and 10-12 become 9-12.
        merged: list[TimeSlot] = []
        for start, end in sorted(trimmed):
            if merged and start <= merged[-1][1]:
                merged[-1] = (merged[-1][0], max(merged[-1][1], end))
            else:
                merged.append((start, end))

        blocked = sum(minutes_between(start, end) for start, end in merged)
        return minutes_between(self.day_start, self.day_end) - blocked


@dataclass
class ScheduledItem:
    """A task placed at a specific time slot for a specific pet."""

    task: Task
    pet: Pet
    start_time: datetime
    end_time: datetime
    is_done: bool = False

    def __post_init__(self) -> None:
        """Reject a time slot that ends before it starts or doesn't match the task's duration."""
        if self.start_time >= self.end_time:
            raise ValueError(f"start_time ({self.start_time}) must be before end_time ({self.end_time})")
        if self.end_time - self.start_time != timedelta(minutes=self.task.duration_minutes):
            raise ValueError(
                f"{self.task.name} lasts {self.task.duration_minutes} min, "
                f"but its slot is {self.start_time:%H:%M}-{self.end_time:%H:%M}"
            )

    def mark_done(self) -> None:
        """Mark this scheduled item as completed."""
        self.is_done = True

    def conflicts_with(self, other: ScheduledItem) -> bool:
        """Return True if this item's time overlaps with other's.

        Items that only touch (one ends exactly when the other starts) don't conflict.
        """
        return self.start_time < other.end_time and other.start_time < self.end_time


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
        notes = []

        all_tasks = owner.get_all_tasks()
        due = [task for task in all_tasks if task.is_due_on(self.date)]
        budget = owner.get_available_minutes()
        notes.append(f"{len(due)} of {len(all_tasks)} tasks are due today; {budget} free minutes available.")

        ordered = self.sort_by_priority(due)
        chosen = self.filter_by_time_available(ordered, budget)

        # Explain anything the time budget left out.
        minutes_left = budget
        for task in ordered:
            if any(task is kept for kept in chosen):
                minutes_left -= task.duration_minutes
            else:
                pet = self._pet_for(owner, task)
                notes.append(
                    f"Skipped {task.name} ({pet.name}): needs {task.duration_minutes} min, "
                    f"only {minutes_left} min left in the budget."
                )

        self.scheduled_items = self.assign_times_and_build_schedule(chosen, owner)

        # Explain anything that fit the budget but not into a single free gap.
        for task in chosen:
            if not any(item.task is task for item in self.scheduled_items):
                pet = self._pet_for(owner, task)
                notes.append(
                    f"Couldn't place {task.name} ({pet.name}): no free {task.duration_minutes}-min "
                    f"gap between blocked times."
                )

        self.reasoning_notes = "\n".join(notes)

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered from highest to lowest priority.

        Ties are broken by duration, shortest first, so more tasks fit in the time left.
        """
        return sorted(tasks, key=lambda task: (-task.priority, task.duration_minutes))

    def filter_by_time_available(self, tasks: list[Task], minutes: int) -> list[Task]:
        """Return the tasks that fit within the given number of minutes.

        Expects tasks already sorted by priority (see sort_by_priority). Walks the
        list in order: if a task fits in the minutes left, keep it and subtract its
        duration; if it doesn't fit, skip it and keep going, so smaller tasks
        further down can still use the remaining time.
        """
        kept = []
        minutes_left = minutes
        for task in tasks:
            if task.duration_minutes <= minutes_left:
                kept.append(task)
                minutes_left -= task.duration_minutes
        return kept

    def assign_times_and_build_schedule(self, tasks: list[Task], owner: Owner) -> list[ScheduledItem]:
        """Give each task a start/end time between owner.day_start and owner.day_end.

        Tasks are placed in the order given, each at the earliest time that doesn't
        overlap owner.blocked_time_slots or a task already placed. A task with no
        free gap long enough is left out.
        """
        day_end = to_datetime(self.date, owner.day_end)
        busy = [
            (to_datetime(self.date, start), to_datetime(self.date, end))
            for start, end in owner.blocked_time_slots
        ]
        items = []

        for task in tasks:
            length = timedelta(minutes=task.duration_minutes)
            start = to_datetime(self.date, owner.day_start)
            while start + length <= day_end:
                end = start + length
                clashes = [b_end for b_start, b_end in busy if start < b_end and b_start < end]
                if not clashes:
                    items.append(ScheduledItem(task, self._pet_for(owner, task), start, end))
                    busy.append((start, end))
                    break
                start = max(clashes)  # jump past whatever is in the way and try again

        return sorted(items, key=lambda item: item.start_time)

    def get_schedule(self) -> list[ScheduledItem]:
        """Return a copy of the scheduled items in time order."""
        return sorted(self.scheduled_items, key=lambda item: item.start_time)

    def explain(self) -> str:
        """Return a human-readable explanation of why the plan looks the way it does."""
        lines = [f"Plan for {self.date:%A, %B %d}:"]
        schedule = self.get_schedule()
        if not schedule:
            lines.append("  No tasks scheduled.")
        for item in schedule:
            lines.append(
                f"  {item.start_time:%H:%M}-{item.end_time:%H:%M}  {item.task.name} for {item.pet.name} "
                f"[{PRIORITY_LABELS[item.task.priority]} priority]"
            )
        lines.append("")
        lines.append("Why:")
        lines.append("  Tasks are placed highest priority first, each at the earliest free time.")
        lines.extend(f"  {note}" for note in self.reasoning_notes.splitlines())
        return "\n".join(lines)

    def _pet_for(self, owner: Owner, task: Task) -> Pet:
        """Return the owner's pet that this exact task object belongs to."""
        for pet in owner.get_pets():
            if any(existing is task for existing in pet.tasks):
                return pet
        raise ValueError(f"{task.name!r} doesn't belong to any of {owner.name}'s pets")
