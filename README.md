# 🎓 TU-Gether – Event Management System

ระบบจัดการกิจกรรมสำหรับนักศึกษาและบุคลากรธรรมศาสตร์  
พัฒนาโดยใช้ **FastAPI + Firebase Firestore** พร้อม **Admin Console** สำหรับจัดการกิจกรรม

---

## ✨ Features

- 👤 **Authentication**
  - รองรับการเข้าสู่ระบบของนักศึกษา (Student)
  - ระบบ **Admin Login** แยกจาก collection `admins` สำหรับจัดการกิจกรรม

- 📅 **Event Management**
  - สร้าง / แก้ไข / ลบ กิจกรรมโดย Admin
  - เก็บข้อมูลกิจกรรมใน Firestore (`events` collection)
  - ข้อมูลกิจกรรมมีรายละเอียดครบ เช่น ชื่อ, คณะ, สาขา, วันจัดงาน, วันปิดรับสมัคร, สถานะ ฯลฯ
  - ระบบสถานะอัตโนมัติ: `Upcoming`, `Open`, `Close`, `Full`

- 📝 **Registration**
  - ผู้ใช้ทั่วไป / นักศึกษา สามารถลงทะเบียนเข้าร่วมกิจกรรม
  - เช็คเงื่อนไขการสมัคร เช่น ช่วงเวลาเปิดลงทะเบียน, จำนวนที่รับขั้นต่ำ/สูงสุด
  - API ตรวจสอบรายการลงทะเบียนของแต่ละกิจกรรม

- 🎨 **Frontend (Admin Console)**
  - ใช้ **HTML + JS + Tailwind CSS**
  - Admin สามารถจัดการกิจกรรมผ่านหน้าเว็บ (CRUD)
  - รองรับการค้นหา / กรองกิจกรรม

---

## 🏗️ Tech Stack

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.13)
- **Database**: [Firebase Firestore](https://firebase.google.com/docs/firestore)
- **Frontend (Admin)**: HTML, Tailwind CSS, JavaScript
- **Deployment**: Uvicorn (Local Dev)

---

## 📂 Project Structure
app/
├── api/v1/
│ ├── routes_auth.py # API สำหรับ auth
│ ├── routes_student.py # API สำหรับนักศึกษา
│ ├── routes_events.py # API สำหรับกิจกรรม
│ ├── routes_admin.py # API สำหรับ admin console
│
├── repositories/
│ ├── admin_repo.py # จัดการ collection: admins
│ ├── events_repo.py # จัดการ collection: events
│
├── schemas/
│ ├── event.py # Pydantic models ของ Event
│ ├── user.py # Pydantic models ของ User
│
├── services/
│ ├── auth_service.py # Logic ของ Authentication
│
├── static/
│ ├── css/ # CSS (Tailwind, custom)
│ ├── js/ # JavaScript (admin_event.js)
│ ├── img/ # Assets
│
├── templates/ # Jinja2 HTML Templates
│ ├── events/ # หน้าเว็บกิจกรรม
│ ├── admin/ # Admin console
│
├── db/
│ ├── firebase.py # Initial Firebase Firestore
│
├── core/
│ ├── config.py # การตั้งค่าโปรเจค
│ ├── security.py # การเข้ารหัส password
│
└── main.py # FastAPI entrypoint

RUN FASTAPI: uvicorn app.main:app --reload

Authors:
PM       | WACHIRAWICH CHANKAEW
Frontend | Parkapon Angkaew              ([@yBRi9HT](https://github.com/BRi9HT))
Frontend | Pongpiphat Phonputtibunya 
Backend  | Hattakorn Pongsawai           ([@yMoLerSTH](https://github.com/MoLerSTH))
Backend  | Kanchanasin Juangsamutkhasem 

TU-Gether Dev Team
Thammasat University Software Engineering Student 2025

