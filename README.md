# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```bash
Today's Schedule
  07:00-07:10  Feeding (Luna)
  07:10-07:40  Morning walk (Mochi)
  07:40-07:55  Training (Mochi)
  07:55-08:15  Play session (Luna)

```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```bash
test_mark_done_changes_status PASSED
test_add_task_increases_task_count PASSED
test_sort_by_time_returns_chronological_order PASSED
test_daily_task_is_scheduled_again_the_next_day_after_done PASSED
test_find_conflicts_flags_items_at_the_same_time PASSED
test_filter_items_by_status_and_pet_name PASSED
test_filter_by_time_available_skips_long_task_and_keeps_going PASSED
7 passed in 0.04s
```

Description:

These tests check the main scheduling rules: what gets scheduled and in what order, when it repeats, and when the user is warned about a conflict

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature           | Method(s)                            | Notes                       |
|-------------------|--------------------------------------|-----------------------------|
| Task sorting      | `Scheduler.sort_by_time`         | by earliest to latest start time                 |
| Filtering         | `Scheduler.filter_by_time_available` | skip tasks if time runs out |
| Conflict handling | `ScheduledItem.conflicts_with`       | checks for overlapping time slots      |
| Recurring tasks   | `Task.is_due_on`                     | daily vs. weekly            |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. **Start the app** with `streamlit run app.py`. The page opens with three sections: **Owner**, **Pets**, and **Build Schedule**.
2. **Set up the owner.** Enter a name (e.g. *Jordan*), set when the day starts and ends (default 07:00–21:00), and tick *"I'm busy for part of the day"* to block out work hours (e.g. 09:00–17:00). Click **Save owner**. The line below updates to show the free time left, here **360 free minutes**.
3. **Add pets.** Enter a name, species, and breed and click **Add pet**. Repeat for each pet (e.g. *Mochi*, a Shiba Inu dog, and *Luna*, a Tabby cat).
4. **Add care tasks.** Once a pet exists, a **Tasks** form appears. Pick the pet, then enter the task name, duration, priority (low / medium / high), how often it repeats (once / daily / weekly), and the start date. Click **Add task**. For example: *Morning walk* (30 min, high) and *Training* (15 min, medium) for Mochi, and *Feeding* (10 min, high) and *Play* (20 min, low) for Luna. Each pet's tasks are listed below the form with a **Remove** button.
5. **Generate the schedule.** Under **Build Schedule**, pick a date and click **Generate schedule**. The scheduler takes every task due that day, puts the highest priority first (shorter first on ties), drops anything that doesn't fit the free time, and places each task at the earliest open slot around the busy hours. The example gives 07:00 Feeding → 07:10 Morning walk → 07:40 Training → 07:55 Play.
6. **Read the summary.** Three numbers at the top show how many tasks are planned, how many are done, and the total care time. A green box says *"No time conflicts"* when nothing overlaps.
7. **Filter and check off tasks.** Use the **Pet** dropdown and the **All / To do / Done** buttons to narrow the table, which always stays in time order. Tick the **Done** box on a row when a task is finished; the progress count updates.
8. **Book a task at a fixed time.** Open *"Book a task at a fixed time"*, pick a task and a time (e.g. Training at 07:00), and click **Book**. Because that overlaps Feeding and the Morning walk, the green box turns into a yellow **⚠️ time conflicts** warning listing each overlapping pair.
9. **See why.** The **Why this plan** panel explains the result: how many tasks were due, how many free minutes there were, and a yellow note for any task that was skipped (e.g. *"Skipped Long hike (Mochi): needs 90 min, only 80 min left in the budget."*).
