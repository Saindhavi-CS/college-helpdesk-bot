
import sqlite3
import bcrypt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "users.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL COLLATE NOCASE,
                password_hash BLOB NOT NULL,
                role TEXT NOT NULL DEFAULT 'Student'
                    CHECK (role IN ('Student', 'Faculty', 'Admin')),
                approved INTEGER NOT NULL DEFAULT 0
                    CHECK (approved IN (0, 1)),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def register_user(email, password):
    email = email.strip().lower()

    if not email or "@" not in email:
        return False, "Valid email address enter pannunga."

    if len(password) < 12:
        return False, "Password minimum 12 characters irukkanum."

    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    )

    try:
        with get_connection() as conn:
            conn.execute(
                """INSERT INTO users
                   (email, password_hash, role, approved)
                   VALUES (?, ?, 'Student', 1)""",
                (email, password_hash)
            )
        return True, "Registration successful. Admin approval pending."

    except sqlite3.IntegrityError:
        return False, "Indha email already registered."


def verify_login(email, password):
    email = email.strip().lower()

    with get_connection() as conn:
        user = conn.execute(
            """SELECT id, email, password_hash, role, approved
               FROM users WHERE email = ?""",
            (email,)
        ).fetchone()

    if user is None:
        return None

    try:
        valid_password = bcrypt.checkpw(
            password.encode("utf-8"),
            user[2]
        )
    except (ValueError, TypeError):
        return None

    if not valid_password or user[4] != 1:
        return None

    return {
        "id": user[0],
        "email": user[1],
        "role": user[3],
    }


def get_user_role(email):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT role, approved FROM users WHERE email = ?",
            (email.strip().lower(),)
        ).fetchone()

    if row and row[1] == 1:
        return row[0]

    return None


init_db()
