import os
import joblib
import pandas as pd
from django.conf import settings

from accounts.models import CustomUser

# Paths
MODEL_PATH = os.path.join(settings.BASE_DIR, 'accounts/ml/model.pkl')
VECTORIZER_PATH = os.path.join(settings.BASE_DIR, 'accounts/ml/vectorizer.pkl')


def load_model_and_vectorizer():
    """Load the trained model and vectorizer from disk."""
    if not os.path.exists(MODEL_PATH) or not os.path.exists(VECTORIZER_PATH):
        raise FileNotFoundError("Model or vectorizer file not found. Please train the model first.")

    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
    return model, vectorizer


def recommend_users_for(user_id, top_n=5):
    """Use the trained ML model to find top-N recommended users for a given user."""
    user = CustomUser.objects.get(id=user_id)
    model, vectorizer = load_model_and_vectorizer()

    # Get all candidates except the current user
    candidates = CustomUser.objects.exclude(id=user.id)

    data = []
    raw_texts = []

    for candidate in candidates:
        sender_skills = f"{user.skills_can_teach or ''} {user.skills_want_to_learn or ''}"
        candidate_skills = f"{candidate.skills_can_teach or ''} {candidate.skills_want_to_learn or ''}"
        combined = f"{sender_skills} || {candidate_skills}"

        raw_texts.append(combined)
        data.append({
            "id": candidate.id,
            "username": candidate.username,
            "city": candidate.city
        })

    if not data:
        return []

    X = vectorizer.transform(raw_texts)
    probs = model.predict_proba(X)[:, 1]  # probability of class '1' (good match)

    # Add scores to data
    for i in range(len(data)):
        data[i]['score'] = round(probs[i], 4)

    # Sort by predicted score
    data.sort(key=lambda x: x['score'], reverse=True)

    return data[:top_n]