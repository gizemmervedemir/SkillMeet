# utils.py

from ml.train_model import find_similar_users  # Optional ML import


def calculate_match_score(user, candidate):
    """
    Calculates a match score between two users based on:

    - Mutual skill exchange:
        * Skills the user wants to learn and the candidate can teach
        * Skills the user can teach and the candidate wants to learn
    - City match (bonus)

    Scoring:
    - Skill match is more important → weighted ×2
    - City match adds +1 if both are in the same city

    Returns:
        int: Total matching score
    """

    # Parse and clean user skills
    user_teach = set(s.strip().lower() for s in user.skills_can_teach.split(',') if s.strip())
    user_learn = set(s.strip().lower() for s in user.skills_want_to_learn.split(',') if s.strip())

    # Parse and clean candidate skills
    candidate_teach = set(s.strip().lower() for s in candidate.skills_can_teach.split(',') if s.strip())
    candidate_learn = set(s.strip().lower() for s in candidate.skills_want_to_learn.split(',') if s.strip())

    # Mutual matches
    teach_match = user_learn & candidate_teach
    learn_match = user_teach & candidate_learn

    skill_score = len(teach_match) + len(learn_match)
    city_score = 1 if user.city.strip().lower() == candidate.city.strip().lower() else 0

    # Total weighted score
    total_score = skill_score * 2 + city_score

    return total_score


def get_ml_suggestions(user_id, top_n=5):
    """
    Uses a machine learning model to find top N similar users for the given user ID.

    Returns:
        List of dictionaries like: [{"id": 4, "score": 0.85}, ...]
    """
    return find_similar_users(user_id, top_n=top_n)