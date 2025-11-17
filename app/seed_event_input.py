import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# โหลด service account key (แก้ path ให้ตรงไฟล์จริงของคุณ)
cred = credentials.Certificate("key_admin/tu-gether-firebase-adminsdk-fbsvc-f9e9c4a999.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

def get_next_event_id():
    """หาค่า event_id ล่าสุดแล้ว +1"""
    docs = db.collection("events").order_by("event_id", direction=firestore.Query.DESCENDING).limit(1).stream()
    last_id = "000000"
    for d in docs:
        last_id = d.to_dict().get("event_id", "000000")
        break
    return str(int(last_id) + 1).zfill(6)

def add_event():
    title = input("ชื่อกิจกรรม: ").strip()
    detail = input("รายละเอียด: ").strip()
    location = input("สถานที่: ").strip()
    faculty = input("คณะ/หน่วยงาน: ").strip()
    category = input("หมวดหมู่: ").strip()
    deadline = input("วันปิดรับสมัคร (YYYY-MM-DD): ").strip()
    event_date = input("วันจัดกิจกรรม (YYYY-MM-DD): ").strip()
    picture_url = input("ลิงก์รูป (ถ้าว่างจะใช้ placeholder): ").strip() or "https://picsum.photos/800/400"
    status = input("สถานะ (Upcoming/Open/Close/Full): ").strip() or "Upcoming"
    tags = input("แท็ก (คั่นด้วย ,): ").strip().split(",") if input else []

    try:
        deadline_dt = datetime.fromisoformat(deadline)
        event_dt = datetime.fromisoformat(event_date)
    except Exception:
        print("⚠️  รูปแบบวันที่ไม่ถูกต้อง (ใช้ YYYY-MM-DD)")
        return

    eid = get_next_event_id()
    data = {
        "event_id": eid,
        "title": title,
        "detail": detail,
        "location": location,
        "faculty": faculty,
        "category": category,
        "deadline_date": deadline_dt,
        "event_date": event_dt,
        "picture_url": picture_url,
        "status": status,
        "tags": [t.strip() for t in tags if t.strip()],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    db.collection("events").document(eid).set(data)
    print(f"✅ Added event {eid}: {title}")

if __name__ == "__main__":
    n = int(input("ต้องการเพิ่มกี่กิจกรรม? (เช่น 5): "))
    for _ in range(n):
        add_event()
    print("🎉 เสร็จสิ้น")
