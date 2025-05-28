import sys
import os
import django
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

# Proje ana klasör yolunu sys.path'e ekle
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(BASE_DIR)

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SkillMeet.settings')
django.setup()

from accounts.models import CustomUser, MatchFeedback


def load_feedback_data():
    """Veritabanından MatchFeedback verilerini çek ve dataframe oluştur."""
    feedbacks = MatchFeedback.objects.all()
    rows = []

    for fb in feedbacks:
        sender = fb.sender
        receiver = fb.receiver

        sender_skills = f"{sender.skills_can_teach or ''} {sender.skills_want_to_learn or ''}"
        receiver_skills = f"{receiver.skills_can_teach or ''} {receiver.skills_want_to_learn or ''}"
        combined_text = f"{sender_skills} || {receiver_skills}"

        label = 1 if fb.rating >= 4 else 0  # 4 ve üzeri iyi eşleşme
        rows.append((combined_text, label))

    return pd.DataFrame(rows, columns=['text', 'label'])


def train_and_save_model():
    df = load_feedback_data()
    if df.empty:
        print("❌ MatchFeedback tablosunda veri yok. Eğitim yapılamıyor.")
        return

    # TF-IDF vektörizasyonu
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(df['text'])
    y = df['label']

    # Eğitim/test verisi ayırma
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Model eğitimi
    model = LogisticRegression()
    model.fit(X_train, y_train)

    # Değerlendirme raporu
    y_pred = model.predict(X_test)
    print("🔍 Değerlendirme Raporu:")
    print(classification_report(y_test, y_pred))

    # Model ve vectorizer'ı diske kaydet (model_utils.py ile uyumlu dosya yolları)
    os.makedirs(os.path.join(BASE_DIR, "accounts/ml"), exist_ok=True)
    joblib.dump(model, os.path.join(BASE_DIR, "accounts/ml/model.pkl"))
    joblib.dump(vectorizer, os.path.join(BASE_DIR, "accounts/ml/vectorizer.pkl"))
    print("✅ Model ve vectorizer accounts/ml/ klasörüne kaydedildi.")


if __name__ == "__main__":
    train_and_save_model()