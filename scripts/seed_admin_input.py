# scripts/seed_admin_input.py
"""
Seed admin user into Firestore.
- Interactive prompts (username, password, display_name, status)
- Or use CLI flags:  --username ... --password ... [--display-name ...] [--status active|disabled] [--update]
- Requires Firebase credentials configured same as the app.

Usage examples:
  python scripts/seed_admin_input.py
  python scripts/seed_admin_input.py --username admin --password Admin@1234 --display-name "Administrator" --status active
  python scripts/seed_admin_input.py --username admin --password NewPass123 --update
"""

import sys
import getpass
import argparse
from typing import Optional

# Reuse app wiring
from app.db.firebase import initialize_firebase, get_db
from app.core.security import hash_password_bcrypt

COLL = "admins"

def upsert_admin(
    *,
    username: str,
    password: str,
    display_name: Optional[str] = None,
    status: str = "active",
    allow_update: bool = False,
) -> dict:
    if not username or len(username.strip()) < 3:
        raise ValueError("username ต้องมีความยาวอย่างน้อย 3 ตัวอักษร")
    if not password or len(password) < 8:
        raise ValueError("password ต้องมีความยาวอย่างน้อย 8 ตัวอักษร")
    if status not in {"active", "disabled"}:
        raise ValueError("status ต้องเป็น 'active' หรือ 'disabled'")

    initialize_firebase()
    db = get_db()

    ref = db.collection(COLL).document(username)
    snap = ref.get()
    pwd_hash = hash_password_bcrypt(password)

    if snap.exists:
        if not allow_update:
            raise ValueError(f"admin '{username}' มีอยู่แล้ว (ใส่ --update ถ้าต้องการแก้ไข)")
        # update existing
        payload = {
            "password_hash": pwd_hash,
        }
        if display_name is not None:
            payload["display_name"] = display_name
        if status:
            payload["status"] = status
        ref.update(payload)
        return {"action": "updated", "username": username, "status": payload.get("status", snap.to_dict().get("status"))}
    else:
        # create new
        ref.set({
            "password_hash": pwd_hash,
            "display_name": display_name or username,
            "status": status,
            "role": "admin",
        })
        return {"action": "created", "username": username, "status": status}

def list_admins(limit: int = 50):
    initialize_firebase()
    db = get_db()
    print(f"\n[admins] (limit {limit})")
    count = 0
    for d in db.collection(COLL).limit(limit).stream():
        data = d.to_dict() or {}
        print(f"- {d.id:20s}  status={data.get('status','?'):8s}  display_name={data.get('display_name','')}")
        count += 1
    if count == 0:
        print("(no admins found)")

def main():
    p = argparse.ArgumentParser(description="Seed/Update admin account in Firestore")
    p.add_argument("--username", type=str, help="admin username (doc id)")
    p.add_argument("--password", type=str, help="admin password (will be bcrypt-hashed)")
    p.add_argument("--display-name", type=str, default=None, help="display name for admin")
    p.add_argument("--status", type=str, default="active", choices=["active", "disabled"], help="admin status")
    p.add_argument("--update", action="store_true", help="allow update if the admin already exists")
    p.add_argument("--list", action="store_true", help="list existing admins and exit")
    args = p.parse_args()

    if args.list:
        list_admins()
        return 0

    # interactive mode if missing args
    username = args.username or input("Admin username: ").strip()
    password = args.password or getpass.getpass("Admin password: ").strip()
    display_name = args.display_name
    if display_name is None:
        dn = input("Display name (optional, default: username): ").strip()
        display_name = dn or None
    status = args.status or "active"

    # confirm
    print("\nSummary:")
    print(f"  username     : {username}")
    print(f"  display_name : {display_name or username}")
    print(f"  status       : {status}")
    if not args.update:
        confirm = input("Proceed? [y/N]: ").strip().lower()
        if confirm != "y":
            print("Aborted.")
            return 1

    try:
        result = upsert_admin(
            username=username,
            password=password,
            display_name=display_name,
            status=status,
            allow_update=args.update,
        )
        print(f"\n✅ Admin {result['action']}: {result['username']} (status={result['status']})")
        print("   หมายเหตุ: password ถูกบันทึกเป็น bcrypt เรียบร้อย")
        print("   คุณสามารถล็อกอินผ่าน /auth (เลือก “ผู้ใช้ทั่วไป”) ได้ทันที")
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 2

if __name__ == "__main__":
    sys.exit(main())
