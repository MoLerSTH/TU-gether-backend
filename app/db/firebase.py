# app/db/firebase.py

import os
import json
import threading
import firebase_admin
from firebase_admin import credentials, firestore

_db: firestore.Client | None = None
_lock = threading.Lock()

def initialize_firebase() -> firestore.Client:
    """
    Initialize Firebase without using local JSON files.
    - In production (Render): load JSON from FIREBASE_CREDENTIALS_JSON (1-line string)
    - In local dev: can still use GOOGLE_APPLICATION_CREDENTIALS or local serviceAccountKey.json
    """
    global _db

    if _db:
        return _db

    with _lock:
        if _db:
            return _db

        # -----------------------
        # 1) Production (Render): Load from ENV variable
        # -----------------------
        cred_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
        if cred_json:
            try:
                cred_dict = json.loads(cred_json)
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
                _db = firestore.client()
                print("🔥 Firebase initialized via FIREBASE_CREDENTIALS_JSON (Render)")
                return _db
            except Exception as e:
                print("❌ ERROR loading FIREBASE_CREDENTIALS_JSON:", e)

        # -----------------------
        # 2) Local dev: load from GOOGLE_APPLICATION_CREDENTIALS path
        # -----------------------
        path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if path and os.path.exists(path):
            cred = credentials.Certificate(path)
            firebase_admin.initialize_app(cred)
            _db = firestore.client()
            print("🔥 Firebase initialized via GOOGLE_APPLICATION_CREDENTIALS (local)")
            return _db

        # -----------------------
        # 3) Local fallback: look for serviceAccountKey.json in project
        # -----------------------
        fallback_paths = [
            "app/key_admin/serviceAccountKey.json",
            "serviceAccountKey.json",
            "firebase-key.json",
        ]

        for p in fallback_paths:
            if os.path.exists(p):
                cred = credentials.Certificate(p)
                firebase_admin.initialize_app(cred)
                _db = firestore.client()
                print(f"🔥 Firebase initialized via local fallback: {p}")
                return _db

        # -----------------------
        # 4) Worst case: use Application Default Credentials
        # -----------------------
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred)
        _db = firestore.client()
        print("⚠️ Firebase initialized via ApplicationDefault (not recommended)")
        return _db


def get_db() -> firestore.Client:
    global _db
    if not _db:
        _db = initialize_firebase()
    return _db
