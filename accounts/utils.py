def calculate_match_score(user, candidate):
    # Ortak beceri takası kontrolü
    user_teach = set(user.skills_can_teach.lower().split(','))
    user_learn = set(user.skills_want_to_learn.lower().split(','))

    candidate_teach = set(candidate.skills_can_teach.lower().split(','))
    candidate_learn = set(candidate.skills_want_to_learn.lower().split(','))

    mutual_teach = user_learn & candidate_teach
    mutual_learn = user_teach & candidate_learn

    skill_score = len(mutual_teach) + len(mutual_learn)
    city_score = 1 if user.city.lower() == candidate.city.lower() else 0

    return skill_score * 2 + city_score  # Ağırlıklandırma: beceriler > şehir