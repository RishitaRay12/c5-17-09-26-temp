from app.user import hash_password, verify_password, create_access_token, get_current_user
from sql_data import get_conn
from fastapi import APIRouter, HTTPException, Depends, status
from schema import UserRegister, TokenResponse
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(
    prefix="/users",
    tags=["Login & Registration"],
)

# Pydantic Schemas


# 1. Register Endpoint
@router.post("/register")
def register(user: UserRegister):

    with get_conn() as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id FROM users WHERE username = ? OR email = ?",
            (user.username, user.email),
        )

        existing_user = cursor.fetchone()

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Username or email already exists.",
            )

        hashed_password = hash_password(user.password)

        cursor.execute(
            """
            INSERT INTO users
            (username, name, email, hashed_password)
            VALUES (?, ?, ?, ?)
            """,
            (
                user.username,
                user.name,
                user.email,
                hashed_password,
            ),
        )

        user_id = cursor.lastrowid

    return {
        "message": "User registered successfully",
        "user_id": user_id,
    }

# 2. Login Endpoint (OAuth2 Compatible)
@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends()):

    with get_conn() as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username = ?",
            (form_data.username,),
        )

        user = cursor.fetchone()

    if not user or not verify_password(
        form_data.password,
        user["hashed_password"],
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user["username"]}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user["username"],
    }

@router.get("/me")
def get_me(
    current_user: dict = Depends(get_current_user),
):
    return current_user
