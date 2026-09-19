from datetime import datetime, timedelta, timezone, UTC
import json
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import sqlite3
from app.config import settings
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher
from sql_data import get_conn

password_hash = PasswordHash((BcryptHasher(),))

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)
# Secret key for JWT signing (Keep this secret in environment variables in production)


# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")


# Password Hashing & Verification
# def hash_password(password: str) -> str:
#     return pwd_context.hash(password)

# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     return pwd_context.verify(plain_password, hashed_password)

# Token Generation
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

# Dependency to Protect Routes
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        username = payload.get("sub")

        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
            )

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
        )

    with get_conn() as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,),
        )

        user = cursor.fetchone()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )

    return dict(user)

def _ensure_chat_metadata_columns(conn: sqlite3.Connection) -> None:
    columns = {
        row["name"]
        for row in conn.execute("PRAGMA table_info(chat_messages)").fetchall()
    }
    if "sources" not in columns:
        conn.execute("ALTER TABLE chat_messages ADD COLUMN sources TEXT")
    if "token_usage" not in columns:
        conn.execute("ALTER TABLE chat_messages ADD COLUMN token_usage TEXT")


def save_chat_message(
    username: str,
    thread_id: str,
    role: str,
    message: str,
    sources: list[dict] | None = None,
    token_usage: dict | None = None,
) -> None:
    """
    Save one chatbot message.

    role should normally be:
        user
        assistant
    """

    with get_conn() as conn:
        _ensure_chat_metadata_columns(conn)

        conn.execute(
            """
            INSERT INTO chat_messages (
                username,
                thread_id,
                role,
                message,
                sources,
                token_usage
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                username,
                thread_id,
                role,
                message,
                json.dumps(sources or []),
                json.dumps(token_usage) if token_usage is not None else None,
            ),
        )


def get_chat_history(
    username: str,
    thread_id: str,
    limit: int = 20,
) -> list[dict]:
    """
    Get the most recent chatbot messages.

    Messages are returned from oldest to newest.
    """

    with get_conn() as conn:
        _ensure_chat_metadata_columns(conn)

        rows = conn.execute(
            """
            SELECT
                role,
                message,
                sources,
                token_usage,
                created_at
            FROM chat_messages
            WHERE username = ?
              AND thread_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (
                username,
                thread_id,
                limit,
            ),
        ).fetchall()

    # Reverse so oldest message comes first
    rows = list(reversed(rows))

    messages = []
    for row in rows:
        try:
            sources = json.loads(row["sources"] or "[]")
        except (TypeError, json.JSONDecodeError):
            sources = []
        try:
            token_usage = json.loads(row["token_usage"]) if row["token_usage"] else None
        except (TypeError, json.JSONDecodeError):
            token_usage = None

        messages.append({
            "role": row["role"],
            "message": row["message"],
            "sources": sources,
            "token_usage": token_usage,
            "created_at": row["created_at"],
        })
    return messages


def get_chat_thread_ids(username: str) -> set[str]:
    """Return thread IDs that have messages owned by the user."""
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT DISTINCT thread_id FROM chat_messages WHERE username = ?",
            (username,),
        ).fetchall()
    return {row["thread_id"] for row in rows}


def delete_chat_thread(username: str, thread_id: str) -> int:
    """Delete all application chat messages for a user's thread."""
    with get_conn() as conn:
        cursor = conn.execute(
            "DELETE FROM chat_messages WHERE username = ? AND thread_id = ?",
            (username, thread_id),
        )
        return cursor.rowcount
