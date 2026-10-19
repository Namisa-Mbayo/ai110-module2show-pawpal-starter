"""PawPal+ core classes.

Skeleton generated from diagrams/uml_draft.mmd. Methods are stubs (no logic yet).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time


@dataclass
class Task:
    """A single pet care activity, such as a walk, feeding, or medication."""

    task_id: str
    name: str
    category: str
    duration_minutes: int
    priority: str  # "low", "medium", or "high"
    is_recurring: bool = False
    is_done: bool = False

    def mark_done(self) -> None:
        """Mark this task as completed."""
        pass

    def conflicts_with(self, other_task: Task) -> bool:
        """Return True if this task overlaps in time with other_task."""
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
    """A pet owner, their daily time budget, and their pets."""

    owner_id: str
    name: str
    available_minutes_per_day: int
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        pass

    def get_pets(self) -> list[Pet]:
        """Return all of this owner's pets."""
        pass


@dataclass
class Scheduler:
    """A schedule of tasks for one pet on one day, with reasoning."""

    scheduler_id: str
    date: date
    scheduled_tasks: list[Task] = field(default_factory=list)
    reasoning_notes: str = ""

    def generate_plan(self, pet: Pet, available_minutes: int) -> None:
        """Build the day's schedule from the pet's tasks within the time available."""
        pass

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered from highest to lowest priority."""
        pass

    def filter_by_time_available(self, tasks: list[Task], minutes: int) -> list[Task]:
        """Return the tasks that fit within the given number of minutes."""
        pass

    def add_task(self, task: Task, start_time: time) -> None:
        """Schedule a task at the given start time."""
        pass

    def get_schedule(self) -> list[Task]:
        """Return the scheduled tasks in order."""
        pass

    def explain(self) -> str:
        """Return a human-readable explanation of why the plan looks the way it does."""
        pass
