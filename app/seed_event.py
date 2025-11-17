# seed_events.py
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# โหลด service account key (แก้ path ให้ตรงไฟล์จริงของคุณ)
cred = credentials.Certificate("key_admin/tu-gether-firebase-adminsdk-fbsvc-f9e9c4a999.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

events = [
    {
        "title": "TU Freshy Night 2025",
        "detail": "งานต้อนรับน้องใหม่สุดยิ่งใหญ่ ประจำปีการศึกษา 2568",
        "location": "สนามกีฬาธรรมศาสตร์ รังสิต",
        "faculty": "General",
        "category": "Welcome",
        "deadline_date": datetime(2025, 7, 10),
        "event_date": datetime(2025, 7, 15),
        "picture_url": "https://picsum.photos/id/1015/800/400",
        "status": "Open",
        "tags": ["freshy", "concert"]
    },
    {
        "title": "อบรม Python for Data Science",
        "detail": "อบรมฟรีสำหรับนักศึกษาและบุคคลทั่วไป",
        "location": "ห้องเรียนรวม SC",
        "faculty": "Science",
        "category": "Academic",
        "deadline_date": datetime(2025, 8, 5),
        "event_date": datetime(2025, 8, 12),
        "picture_url": "https://picsum.photos/id/1025/800/400",
        "status": "Upcoming",
        "tags": ["python", "data"]
    },
    {
        "title": "แข่งขัน E-Sport TU Championship",
        "detail": "ทัวร์นาเมนต์เกมระดับมหาวิทยาลัย",
        "location": "หอประชุมใหญ่",
        "faculty": "Engineering",
        "category": "Competition",
        "deadline_date": datetime(2025, 9, 1),
        "event_date": datetime(2025, 9, 5),
        "picture_url": "https://picsum.photos/id/1035/800/400",
        "status": "Open",
        "tags": ["esport", "gaming"]
    },
    {
        "title": "งานวิ่งการกุศล TU Charity Run",
        "detail": "รายได้ทั้งหมดสมทบทุนโรงพยาบาลธรรมศาสตร์",
        "location": "สนามกีฬากลาง",
        "faculty": "General",
        "category": "Sport",
        "deadline_date": datetime(2025, 10, 1),
        "event_date": datetime(2025, 10, 20),
        "picture_url": "https://picsum.photos/id/1045/800/400",
        "status": "Upcoming",
        "tags": ["sport", "charity"]
    },
    {
        "title": "นิทรรศการศิลปะนักศึกษา TU Art Exhibition",
        "detail": "แสดงผลงานศิลปะของนักศึกษา คณะศิลปกรรมศาสตร์",
        "location": "ศูนย์ศิลปวัฒนธรรม",
        "faculty": "FineArts",
        "category": "Exhibition",
        "deadline_date": datetime(2025, 11, 1),
        "event_date": datetime(2025, 11, 10),
        "picture_url": "https://picsum.photos/id/1055/800/400",
        "status": "Upcoming",
        "tags": ["art", "exhibition"]
    }
]

# เพิ่มข้อมูลลง collection "events"
for i, ev in enumerate(events, start=1):
    eid = str(i).zfill(6)  # เช่น 000001
    ev.update({
        "event_id": eid,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    })
    db.collection("events").document(eid).set(ev)
    print(f"Inserted event {eid}: {ev['title']}")

print("✅ Done seeding events")
