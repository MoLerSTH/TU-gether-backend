#!/usr/bin/env bash
# --------------------------
# start.sh for FastAPI on Render
# ปรับค่าอัตโนมัติ รองรับโครงสร้างหลายแบบ
# --------------------------

set -e  # หากเกิด error ให้หยุดทันที

# ตรวจสอบโครงสร้างโปรเจกต์และเลือกโมดูลที่ถูกต้อง
if [ -f "main.py" ]; then
    MODULE="main:app"
elif [ -f "app/main.py" ]; then
    MODULE="app.main:app"
elif [ -f "src/main.py" ]; then
    MODULE="src.main:app"
else
    echo "❌ ERROR: ไม่พบไฟล์ main.py หรือ app/main.py"
    exit 1
fi

echo "🚀 Starting FastAPI with module: $MODULE"

# รันแอปด้วย Gunicorn + UvicornWorker (เหมาะกับ Render)
exec gunicorn \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:$PORT \
    --timeout 120 \
    --workers 1 \
    "$MODULE"
