import firebase_admin
from firebase_admin import auth, credentials

from .config import settings


def init_firebase() -> None:
    if firebase_admin._apps:
        return

    cred = credentials.Certificate("app/serviceAccountKey.json")

    firebase_admin.initialize_app(cred)


def verify_firebase_token(id_token: str) -> dict:
    init_firebase()

    try:
        decoded_token = auth.verify_id_token(id_token)
        print("🔥 TOKEN OK:", decoded_token)
        return decoded_token

    except Exception as e:
        print("❌ TOKEN ERROR:", e)
        raise e