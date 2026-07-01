"""
RackMind AI

Authentication + Role Service

Provides login support with operator / manager / admin roles for
shared-team deployments. Passwords are stored as salted PBKDF2
hashes in the shared SQLite database.
"""

import hashlib
import os
import secrets
from datetime import datetime

from services.db import get_connection
from services.logger import info, warning

ROLES = ("operator", "manager", "admin")

ROLE_LEVELS = {
    "operator": 1,
    "manager": 2,
    "admin": 3,
}

PBKDF2_ITERATIONS = 120_000

DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_PASSWORD = "rackmind"


def _ensure_schema(connection):
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'operator',
            created_at TEXT NOT NULL,
            last_login TEXT
        )
        """
    )
    connection.commit()


def hash_password(password: str, salt: str) -> str:
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        PBKDF2_ITERATIONS,
    )

    return digest.hex()


def auth_enabled() -> bool:
    """
    Authentication is on by default. Set RACKMIND_AUTH=off to run
    the app open (single-operator or local demo mode).
    """

    value = str(os.getenv("RACKMIND_AUTH", "on")).strip().lower()

    return value not in ("off", "false", "0", "disabled", "no")


def ensure_default_admin():
    """
    Bootstrap a default admin account on first run so a fresh
    deployment is never locked out. The default password should be
    rotated immediately; the UI warns while it is still in use.
    """

    with get_connection() as connection:
        _ensure_schema(connection)

        row = connection.execute(
            "SELECT COUNT(*) AS total FROM users"
        ).fetchone()

        if row["total"] > 0:
            return False

    password = os.getenv(
        "RACKMIND_ADMIN_PASSWORD",
        DEFAULT_ADMIN_PASSWORD,
    )

    create_user(DEFAULT_ADMIN_USERNAME, password, "admin")

    info("Bootstrapped default admin account.")

    return True


def create_user(username: str, password: str, role: str = "operator") -> bool:
    username = str(username or "").strip().lower()

    if not username or not password:
        raise ValueError("Username and password are required.")

    if role not in ROLES:
        raise ValueError(
            f"Role must be one of: {', '.join(ROLES)}"
        )

    if len(password) < 4:
        raise ValueError("Password must be at least 4 characters.")

    salt = secrets.token_hex(16)

    with get_connection() as connection:
        _ensure_schema(connection)

        existing = connection.execute(
            "SELECT username FROM users WHERE username = ?",
            (username,),
        ).fetchone()

        if existing:
            raise ValueError(f"User '{username}' already exists.")

        connection.execute(
            """
            INSERT INTO users
                (username, password_hash, salt, role, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                username,
                hash_password(password, salt),
                salt,
                role,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )

        connection.commit()

    info(f"Created user '{username}' with role '{role}'.")

    return True


def authenticate(username: str, password: str) -> dict | None:
    """
    Verify credentials. Returns the user record (without secrets)
    on success, otherwise None.
    """

    username = str(username or "").strip().lower()

    with get_connection() as connection:
        _ensure_schema(connection)

        row = connection.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,),
        ).fetchone()

        if row is None:
            warning(f"Login failed for unknown user '{username}'.")
            return None

        candidate = hash_password(password or "", row["salt"])

        if not secrets.compare_digest(candidate, row["password_hash"]):
            warning(f"Login failed for user '{username}'.")
            return None

        connection.execute(
            "UPDATE users SET last_login = ? WHERE username = ?",
            (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                username,
            ),
        )

        connection.commit()

    info(f"User '{username}' logged in.")

    return {"username": username, "role": row["role"]}


def change_password(username: str, new_password: str) -> bool:
    username = str(username or "").strip().lower()

    if len(new_password or "") < 4:
        raise ValueError("Password must be at least 4 characters.")

    salt = secrets.token_hex(16)

    with get_connection() as connection:
        _ensure_schema(connection)

        cursor = connection.execute(
            "UPDATE users SET password_hash = ?, salt = ? WHERE username = ?",
            (hash_password(new_password, salt), salt, username),
        )

        connection.commit()

        return cursor.rowcount > 0


def set_role(username: str, role: str) -> bool:
    if role not in ROLES:
        raise ValueError(
            f"Role must be one of: {', '.join(ROLES)}"
        )

    username = str(username or "").strip().lower()

    with get_connection() as connection:
        _ensure_schema(connection)

        cursor = connection.execute(
            "UPDATE users SET role = ? WHERE username = ?",
            (role, username),
        )

        connection.commit()

        return cursor.rowcount > 0


def delete_user(username: str) -> bool:
    username = str(username or "").strip().lower()

    with get_connection() as connection:
        _ensure_schema(connection)

        admins = connection.execute(
            "SELECT COUNT(*) AS total FROM users WHERE role = 'admin'"
        ).fetchone()["total"]

        target = connection.execute(
            "SELECT role FROM users WHERE username = ?",
            (username,),
        ).fetchone()

        if target is None:
            return False

        if target["role"] == "admin" and admins <= 1:
            raise ValueError("Cannot delete the last admin account.")

        connection.execute(
            "DELETE FROM users WHERE username = ?",
            (username,),
        )

        connection.commit()

    return True


def list_users() -> list[dict]:
    with get_connection() as connection:
        _ensure_schema(connection)

        rows = connection.execute(
            """
            SELECT username, role, created_at, last_login
            FROM users ORDER BY username
            """
        ).fetchall()

    return [dict(row) for row in rows]


def has_role(user: dict | None, minimum_role: str) -> bool:
    """
    True when the user's role meets or exceeds minimum_role.
    When authentication is disabled everyone is treated as admin.
    """

    if not auth_enabled():
        return True

    if not user:
        return False

    user_level = ROLE_LEVELS.get(user.get("role"), 0)
    required = ROLE_LEVELS.get(minimum_role, ROLE_LEVELS["admin"])

    return user_level >= required


def is_default_password(username: str) -> bool:
    """
    True while the bootstrap admin password is still in place, so
    the UI can nag until it is rotated.
    """

    with get_connection() as connection:
        _ensure_schema(connection)

        row = connection.execute(
            "SELECT * FROM users WHERE username = ?",
            (str(username or "").strip().lower(),),
        ).fetchone()

    if row is None:
        return False

    candidate = hash_password(DEFAULT_ADMIN_PASSWORD, row["salt"])

    return secrets.compare_digest(candidate, row["password_hash"])
