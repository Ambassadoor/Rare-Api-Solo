"""CRUD methods for the User table"""

import sqlite3
import os
import secrets
import json
from datetime import datetime
from models import User

DB_PATH = os.getenv("DB_PATH")


def _add_session_token(user_id, db_cursor):
    """Generates a session token and inserts it into the session table

    Args:
        user_id (int): The id of the user to create a session for
        db_cursor: The active sqlite3 cursor used to execute the INSERT

    Returns:
        str: A 64-character hex session token
    """
    token = secrets.token_hex(32)

    db_cursor.execute(
        """
        INSERT INTO session
        (token, user_id)
        VALUES (?,?)
        """,
        (token, user_id),
    )
    return token


def login_user(user):
    """Validates user credentials and creates a new session

    Args:
        user (dict): Must contain 'username' and 'password' keys

    Returns:
        str: A 64-character hex session token if credentials are valid
        None: If no matching user is found
    """
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
            select id, username
            from Users
            where username = ?
            and password = ?
        """,
            (user["username"], user["password"]),
        )

        user_from_db = db_cursor.fetchone()

        if user_from_db is not None:
            return _add_session_token(user_from_db["id"], db_cursor)

        return None


def create_user(user):
    """Inserts a new user into the database and creates an initial session

    Args:
        user (dict): Must contain 'first_name', 'last_name', 'username',
                     'email', 'password', and 'bio' keys

    Returns:
        str: A 64-character hex session token for the newly created user
    """
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
        Insert into Users (first_name, last_name, username, email, password, bio, created_on, active) values (?, ?, ?, ?, ?, ?, ?, 1)
        """,
            (
                user["first_name"],
                user["last_name"],
                user["username"],
                user["email"],
                user["password"],
                user["bio"],
                datetime.now(),
            ),
        )

        user_id = db_cursor.lastrowid

        token = _add_session_token(user_id, db_cursor)

        return token


def logout_user(token):
    """Removes the user session token from the db

    Args:
        token (str): User session token
    """
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.cursor().execute("DELETE FROM session WHERE token = ?", (token,))


def get_user_info_from_token(token):
    """On active session, resets session timer and returns user info for for session.
    On inactive, deletes expired session

    Args:
        token (str): User session token
    """
    with sqlite3.connect("./db.sqlite3") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
            SELECT 
                u.id, 
                u.first_name, 
                u.last_name,
                u.email,
                u.bio,
                u.username,
                u.created_on,
                u.active,
                u.is_admin,
                u.profile_image_url,
                u.updated_at
            FROM Users u
            JOIN session s
            ON u.id = s.user_id
            WHERE s.token = ?
            AND s.last_seen_at > datetime('now', '-30 minutes')
            """,
            (token,),
        )

        row = db_cursor.fetchone()

        if row is None:
            db_cursor.execute(
                """
                DELETE FROM session
                WHERE token = ?
                """, (token,)
            )
            return json.dumps({"valid": False})
        
        db_cursor.execute(
            """
            UPDATE session SET
            last_seen_at = datetime('now')
            WHERE token = ?
            """, (token,)
        )

        user = User(**dict(row)).to_dict()

        return json.dumps(user)
