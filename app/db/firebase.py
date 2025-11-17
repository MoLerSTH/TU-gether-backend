# app/db/firebase.py
import os
from pathlib import Path
import threading
import firebase_admin
from firebase_admin import credentials, firestore
from app.core.config import settings

_db: firestore.Client | None = None
_lock = threading.Lock()

def initialize_firebase() -> firestore.Client:
    global _db
    if _db:
        return _db
    with _lock:
        if _db:
            return _db
        if not firebase_admin._apps:
            path = settings.GOOGLE_APPLICATION_CREDENTIALS or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if path and os.path.exists(path):
                cred = credentials.Certificate(path)
                firebase_admin.initialize_app(cred)
            else:
                base = Path(__file__).resolve().parents[1]
                for name in [
                    "key_admin/tu-gether-firebase-adminsdk-fbsvc-17886978cb.json",
                    "firebase-key.json",
                    "firebase-service-account.json",
                    "serviceAccountKey.json"
                ]:
                    candidate = base / name
                    if candidate.exists():
                        cred = credentials.Certificate(str(candidate))
                        firebase_admin.initialize_app(cred)
                        break
                else:
                    cred = credentials.ApplicationDefault()
                    firebase_admin.initialize_app(cred)
        _db = firestore.client()
        return _db

def get_db() -> firestore.Client:
    global _db
    if not _db:
        _db = initialize_firebase()
    return _db
