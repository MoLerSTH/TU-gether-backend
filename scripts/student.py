import argparse, hashlib, os
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore

def hash_password(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()

def init_db():
    # 1) ใช้จากตัวแปรแวดล้อมถ้ามี
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if cred_path and os.path.exists(cred_path):
        firebase_admin.initialize_app(credentials.Certificate(cred_path))
        return firestore.client()

    # 2) หาไฟล์ในรากโปรเจกต์ (โฟลเดอร์เหนือ scripts)
    base = Path(__file__).resolve().parents[1]
    for name in [
        "serviceAccountKey.json",
        "firebase-key.json",
        "firebase-service-account.json",
        "tu-gether-firebase-adminsdk-fbsvc-f9e9c4a999.json",
    ]:
        p = base / name
        if p.exists():
            firebase_admin.initialize_app(credentials.Certificate(str(p)))
            return firestore.client()

    raise FileNotFoundError("ไม่พบไฟล์ credential — ตั้ง GOOGLE_APPLICATION_CREDENTIALS หรือวางไฟล์ไว้ที่รากโปรเจกต์")

def main():
    ap = argparse.ArgumentParser(description="Seed one student into Firestore: Student/<student_id>")
    ap.add_argument("--student-id", required=True, help="รหัสนักศึกษา (doc id)")
    ap.add_argument("--citizen-id", required=True, help="เลขบัตรประชาชน 13 หลัก (จะถูกแฮช)")
    ap.add_argument("--firstname", required=True)
    ap.add_argument("--lastname", required=True)
    ap.add_argument("--email", default=None)
    ap.add_argument("--grade", type=int, default=None)
    ap.add_argument("--phone", default=None)
    ap.add_argument("--faculty", default=None)
    ap.add_argument("--major", default=None)
    args = ap.parse_args()

    db = init_db()
    data = {
        "firstname": args.firstname.strip(),
        "lastname": args.lastname.strip(),
        "email": args.email,
        "grade": args.grade,
        "phone_num": args.phone,
        "faculty": args.faculty,
        "major": args.major,
        "role": "student",
        "national_id_hash": hash_password(args.citizen_id),
    }
    # merge=True → อัปเดตได้ซ้ำโดยไม่ลบทิ้งทั้งเอกสาร
    db.collection("Student").document(args.student_id).set(data, merge=True)
    print(f"OK ✔  Student/{args.student_id} ถูกสร้าง/อัปเดตแล้ว")

if __name__ == "__main__":
    main()
