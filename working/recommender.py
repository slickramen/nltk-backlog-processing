"""
Basic python implementation of recommender system. The final system will be implemented in C#.

Each user has a few maps of "skills" aligning to the different areas we want to recommend tasks based off
"""

from stemmed import categorise_task
from py.sample import SAMPLE_TASKS
from py.language_dict import PLAIN_IMPLEMENTATION_KEYWORDS as P_I
from py.language_dict import PLAIN_CONCEPT_KEYWORDS as P_C
from py.language_dict import PLAIN_STACK_KEYWORDS as P_S


class User:
    """
    Basic dummy user class.
    Implements hashmaps for skills.
    """

    def __init__(self, name):
        self.name = name
        self.stack_skills = dict.fromkeys(P_S.keys(), 0)
        self.implementation_skills = dict.fromkeys(P_I.keys(), 0)
        self.concept_skills = dict.fromkeys(P_C.keys(), 0)


class Task:
    def __init__(self, name, stack, impl, concept):
        self.name = name
        self.stack_skills = stack
        self.implementation_skills = impl
        self.concept_skills = concept

    def __str__(self):
        return f"name: {self.name}\nstack: {self.stack_skills}\nimpl: {self.implementation_skills}\nconcept: {self.concept_skills}\n---\n"


def fetch_task_pool():
    task_list = []

    for title, description in SAMPLE_TASKS:
        task_list.append(categorise_task(title, description))

    pooled_tasks = []

    for task in task_list:
        processed_task = Task(
            task["title"],
            task["stack_layer"],
            task["implementation_types"],
            task["core_concepts"],
        )
        pooled_tasks.append(processed_task)

        print(processed_task)

    return pooled_tasks


def print_user_skills(user):
    print(user.name)

    sorted_stack = dict(
        sorted(user.stack_skills.items(), key=lambda item: item[1], reverse=True)
    )
    sorted_impl = dict(
        sorted(
            user.implementation_skills.items(), key=lambda item: item[1], reverse=True
        )
    )
    sorted_conc = dict(
        sorted(user.concept_skills.items(), key=lambda item: item[1], reverse=True)
    )

    print(sorted_stack)
    print(sorted_impl)
    print(sorted_conc)


# Sample functions for consuming and fetching relevant tasks
def consume_task(user, task_list, task_index):
    task = task_list[task_index]

    task_stack = task.stack_skills

    if task_stack == "fullstack":
        user.stack_skills["frontend"] += 1
        user.stack_skills["backend"] += 1
    else:
        user.stack_skills[f"{task_stack}"] += 1

    for imp in task.implementation_skills:
        user.implementation_skills[f"{imp}"] += 1

    for concept in task.concept_skills:
        user.concept_skills[f"{concept}"] += 1


def allocate_tasks(users, task_list, n_per_user=3):
    """
    Offers each user up to n tasks they are the best fit for.
    A task can only be offered to one user.
    """

    def score_user_for_task(user, task):
        score = 0.0
        weak_skills = []

        # tech stack
        stack = task.stack_skills
        stacks_to_check = ["frontend", "backend"] if stack == "fullstack" else [stack]
        stack_score = 0
        for s in stacks_to_check:
            if s in user.stack_skills:
                level = user.stack_skills[s]
                stack_score += 1 / (1 + level)
                if level == 0:
                    weak_skills.append(s)
        score += stack_score / len(stacks_to_check)

        # implementation
        if task.implementation_skills:
            impl_score = 0
            for impl in task.implementation_skills:
                if impl in user.implementation_skills:
                    level = user.implementation_skills[impl]
                    impl_score += 1 / (1 + level)
                    if level == 0:
                        weak_skills.append(impl)
            score += impl_score / len(task.implementation_skills)

        # concepts
        if task.concept_skills:
            concept_score = 0
            for concept in task.concept_skills:
                if concept in user.concept_skills:
                    level = user.concept_skills[concept]
                    concept_score += 1 / (1 + level)
                    if level == 0:
                        weak_skills.append(concept)
            score += concept_score / len(task.concept_skills)

        reason = (
            f"gaps in: {', '.join(weak_skills)}"
            if weak_skills
            else "general skill development"
        )
        return score, reason

    all_pairs = [
        (score, reason, user, task)
        for user in users
        for task in task_list
        for score, reason in [score_user_for_task(user, task)]
    ]
    all_pairs.sort(key=lambda x: x[0], reverse=True)

    claimed_tasks = set()
    offers = {user.name: [] for user in users}

    for score, reason, user, task in all_pairs:
        if task in claimed_tasks:
            continue
        if len(offers[user.name]) >= n_per_user:
            continue
        offers[user.name].append((score, reason, task))
        claimed_tasks.add(task)

    for user in users:
        print(f"\n{user.name}'s offers:")
        for score, reason, task in offers[user.name]:
            print(f"  [{score:.4f}] {task.name} ({reason})")


if __name__ == "__main__":
    new_user = User("John Doe")
    new_user2 = User("Jane Doe")
    new_user3 = User("Jim Doe")

    task_pool = fetch_task_pool()

    consume_task(new_user, task_pool, 6)
    consume_task(new_user, task_pool, 3)
    consume_task(new_user, task_pool, 1)
    consume_task(new_user, task_pool, 2)
    consume_task(new_user, task_pool, 7)
    consume_task(new_user, task_pool, 4)
    consume_task(new_user, task_pool, 3)

    consume_task(new_user2, task_pool, 4)

    consume_task(new_user3, task_pool, 2)

    allocate_tasks([new_user, new_user2, new_user3], task_pool, 3)
