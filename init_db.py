"""
init_db.py – Run once to create the cybersafe_db database and seed data.
Usage:
    python init_db.py
"""
import os
import sys
from werkzeug.security import generate_password_hash
from db import init_db, execute


def main():
    schema = os.path.join(os.path.dirname(__file__), 'schema.sql')
    if not os.path.exists(schema):
        print("ERROR: schema.sql not found."); sys.exit(1)

    print("Connecting to MySQL (XAMPP) and applying schema …")
    try:
        init_db(schema)
    except Exception as exc:
        print(f"ERROR: {exc}\nMake sure XAMPP MySQL is running on port 3306.")
        sys.exit(1)

    # Re-hash default accounts with proper werkzeug hashes
    pairs = [
        ('admin',  'Admin@123'),
        ('user1',  'User@1234'),
    ]
    for uname, pwd in pairs:
        h = generate_password_hash(pwd)
        execute(
            "UPDATE users SET password_hash=%s WHERE username=%s",
            (h, uname)
        )

    print("\n" + "="*55)
    print("  CyberSafe DB initialised successfully!")
    print("  Database : cybersafe_db")
    print("  Admin    : admin   /  Admin@123")
    print("  User     : user1   /  User@1234")
    print("="*55 + "\n")


if __name__ == '__main__':
    main()
