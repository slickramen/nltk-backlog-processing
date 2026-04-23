"""
Basic python implementation of recommender system. The final system will be implemented in C#.

Each user has a few maps of "skills" aligning to the different areas we want to recommend tasks based off
"""

from py.language_dict import PLAIN_IMPLEMENTATION_KEYWORDS as P_I
from py.language_dict import PLAIN_CONCEPT_KEYWORDS as P_C
from py.language_dict import PLAIN_STACK_KEYWORDS as P_S

"""
Basic dummy user class.

Implements hashmaps for skills.
"""
class User:
    def __init__(self, name):
        self.name = name
        self.stack_skills           = dict.fromkeys(P_S.keys(), 0)
        self.implementation_skills  = dict.fromkeys(P_I.keys(), 0)
        self.concept_skills         = dict.fromkeys(P_C.keys(), 0)



if __name__ == "__main__":
    new_user = User("John Doe")

    print(new_user.name)
    print(new_user.stack_skills)
    print(new_user.implementation_skills)
    print(new_user.concept_skills)