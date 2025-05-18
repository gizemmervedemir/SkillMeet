def calculate_match_score(user, candidate):
    """
    Calculates a matching score between two users based on:
    - Skills user wants to learn and candidate can teach
    - Skills user can teach and candidate wants to learn
    - Whether both users are in the same city

    Weights:
    - Skill match: high importance (×2)
    - City match: low importance (+1)
    """

    user_teach = set(s.strip().lower() for s in user.skills_can_teach.split(',') if s.strip())
    user_learn = set(s.strip().lower() for s in user.skills_want_to_learn.split(',') if s.strip())

    candidate_teach = set(s.strip().lower() for s in candidate.skills_can_teach.split(',') if s.strip())
    candidate_learn = set(s.strip().lower() for s in candidate.skills_want_to_learn.split(',') if s.strip())

    # Mutual skill exchange:
    mutual_teach = user_learn & candidate_teach
    mutual_learn = user_teach & candidate_learn

    skill_score = len(mutual_teach) + len(mutual_learn)
    city_score = 1 if user.city.strip().lower() == candidate.city.strip().lower() else 0

    total_score = skill_score * 2 + city_score  # Emphasize skill compatibility

    return total_score