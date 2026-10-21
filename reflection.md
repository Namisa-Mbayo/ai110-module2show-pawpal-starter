# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
The three core actions a user should be able to perform are (a) add a pet, (b) assign and customize a task, and (c) be able to see the schedule/plan for the day.
I included four classes in my initial design: `Owner`, `Pet`, `Task`, `Scheduler`. `Owner` and `Pet`. The `Owner` class is responsible for adding their pet information, task preferences (later to be specified), and time avaible each day. The `Pet` class is responsible for holding information about a pet and what tasks are assigned to them. The `Task` class is responsible for holding the details about each task and determining whether it has been completed. The `Scheduler` class is responsible for generating a detailed plan from the tasks, explaining the reasoning for the generated plan.

# str(uuid.uuid4()) in app.py

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
I added a `ScheduledItem` class because the scheduled time for a task wasn't saved anywhere. With this new class, I will now know what time each task is at. This also makes it easier to the `Scheduler` class to gather information about the specific placements of a task.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?
I thought about what constraints would matter to me the most when deciding what the scheduler should consider. I chose to weigh in the time an owner had available to them and the priority of tasks. For preferences, it was too vague to add as a consideration so I converted in into blocked time slots that the owner was not available to complete any tasks.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?
For `Scheduler.filter_by_time_available`, if a task that is high priority is too long to fit in the schedule it gets dropped, but lower priority tasks can still make it in. It keeps it simple by allowing the owner to complete as many high priority tasks as they can before moving on to the lower priority tasks.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?
I mostly used the AI to helo me understand UML diagrams and classes. I would ask it to explain to me why certain methods were in a specific class. Like, "why is `addTask()` in `Pet` and not `Task`?" and that is because `Pet` holds the initial `self.tasks`, so the method lives on the class that owns the collection.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?
The AI suggested that I use Python's IntEnum to create Priority Class for ranking. I found it to be too complex so I decided to use a dictionary to store the priority ranking. I had the AI create a test to see if that would work, and it was accepted, but it failed when I tried to sort it. To fix it I just inversed the dictionary. So, before it was {"low":1} and it transitioned into {1:"low"}. This gave me the number for the logic and the word for users.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?
I tested the "For which pet?" dropdown function. Before, it stored the pet itself which meant everytime I selected it from the menu, it was actually a copy of the pet. This made it so anytime new tasks were added, they disappeared because they weren't stored in the original pet value.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?
I am 4/5 confident that my scheduler works correctly. If I had more time I'd check if any tasks runs past the `day_end` attribute stated by the owner. I'd also check for if a task had been scheduled during a blocked time slot, I feel those edge cases would be where a bug is most likely to be hidden.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
I was really satisfied with how well my `Scheduler` class flowed, especially since that was the one I had trouble with making sense of initially.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
I actually really liked my code before we had to add additional filtering and sorting methods since I had those in the beginning. So, I'd probably take them out.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
The trick to identifying classes is to read the requirements and pick out the nouns that represent things your system needs to track or change. Verbs become methods and adjectives become attributes.
