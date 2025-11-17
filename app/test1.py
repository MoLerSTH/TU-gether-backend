# one-off bootstrap (รันครั้งเดียวใน REPL)
from app.db.firebase import get_db, initialize_firebase
from app.core.security import hash_password_bcrypt
initialize_firebase()
db = get_db()
db.collection("admins").document("admin").set({
    "password_hash": hash_password_bcrypt("Admin@1234"),
    "display_name": "Administrator",
    "status": "active",
    "role": "admin",
})
print("admin created: admin / Admin@1234")