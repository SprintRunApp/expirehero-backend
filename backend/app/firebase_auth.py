import firebase_admin
from firebase_admin import auth, credentials

from app.config import settings


def init_firebase() -> None:
    if firebase_admin._apps:
        return

    cred = credentials.Certificate({
        "type": "service_account",
        "project_id": settings.firebase_project_id,
        "client_email": settings.firebase_client_email,
        "private_key": settings.firebase_private_key_fixed,
        "token_uri": "https://oauth2.googleapis.com/token",
    })

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