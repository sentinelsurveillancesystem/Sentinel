from fastapi import Depends, FastAPI, HTTPException, status

from datetime import datetime
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, VerifyMismatchError
from pydantic import BaseModel, EmailStr, Field, model_validator
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from database import engine

from auth.dependencies import get_current_user, require_admin
from auth.tokens import create_access_token

app = FastAPI(title="Sentinel Auth")

ph = PasswordHasher()

# Verified against on login when the username doesn't exist, so a
# failed login takes the same amount of time either way and can't be
# used to enumerate valid usernames.
_DUMMY_HASH = ph.hash("not-a-real-password")

# Every query below selects exactly these columns, so all routes stay
# in sync with UserResponse. Change it here, not in four places.
USER_COLUMNS = """
    user_id, username, full_name, branch, roll_num,
    age, email, phone, role, is_active, created_at
"""


# ---------- Schemas ----------

class RegistrationRequest(BaseModel):
    username: str = Field(min_length=3, max_length=32, pattern=r"^[a-zA-Z0-9_]+$")
    full_name: str = Field(min_length=3, max_length=50)
    branch: str = Field(min_length=2, max_length=100)
    roll_num: str = Field(min_length=2, max_length=20, pattern=r"^[A-Za-z0-9/-]+$")
    age: int = Field(ge=13, le=120)
    email: EmailStr
    phone: str = Field(pattern=r"^\+?[1-9]\d{7,14}$")
    password: str = Field(min_length=8, max_length=128)
    re_enter_password: str

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.re_enter_password:
            raise ValueError("Passwords do not match")
        return self


class UserResponse(BaseModel):
    user_id: int
    username: str
    full_name: str
    branch: str
    roll_num: str
    age: int
    email: EmailStr
    phone: str
    role: str
    is_active: bool
    created_at: datetime


class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class UsernameAvailability(BaseModel):
    username: str
    available: bool


# ---------- Routes ----------

@app.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(user: RegistrationRequest):

    try:
        with engine.begin() as connection:
            row = connection.execute(
                text(f"""
                    INSERT INTO identity.users
                        (username, full_name, branch, roll_num,
                         age, email, phone, password_hash, role)
                    VALUES
                        (:username, :full_name, :branch, :roll_num,
                         :age, :email, :phone, :password_hash, 'member')
                    RETURNING {USER_COLUMNS}
                """),
                {
                    "username": user.username,
                    "full_name": user.full_name.strip(),
                    "branch": user.branch.strip(),
                    "roll_num": user.roll_num.upper(),
                    "age": user.age,
                    "email": user.email.lower(),
                    "phone": user.phone,
                    "password_hash": ph.hash(user.password),
                },
            ).mappings().first()

    except IntegrityError:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Username, email or roll number already registered",
        )

    return row


@app.post("/login", response_model=LoginResponse)
def login(credentials: LoginRequest):

    with engine.connect() as connection:
        row = connection.execute(
            text(f"""
                SELECT {USER_COLUMNS}, password_hash
                FROM identity.users
                WHERE username = :username
            """),
            {"username": credentials.username},
        ).mappings().first()

    hash_to_check = row["password_hash"] if row else _DUMMY_HASH

    try:
        ph.verify(hash_to_check, credentials.password)
    except (VerifyMismatchError, VerificationError):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Invalid username or password"
        )

    if row is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Invalid username or password"
        )

    if not row["is_active"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Account is suspended")

    token = create_access_token(
        user_id=row["user_id"],
        username=row["username"],
        role=row["role"],
    )

    return {"access_token": token, "token_type": "bearer", "user": row}



@app.get("/health")
def health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False
    return {"status": "ok", "database": "connected" if db_ok else "unreachable"}


@app.get("/username-available/{username}", response_model=UsernameAvailability)
def username_available(username: str):
    with engine.connect() as connection:
        row = connection.execute(
            text("SELECT 1 FROM identity.users WHERE username = :username"),
            {"username": username},
        ).first()

    return {"username": username, "available": row is None}


@app.get("/users", response_model=list[UserResponse])
def get_users(current_user: dict = Depends(require_admin)):

    with engine.connect() as connection:
        rows = connection.execute(
            text(f"""
                SELECT {USER_COLUMNS}
                FROM identity.users
                ORDER BY created_at DESC
            """)
        ).mappings().all()

    return rows


@app.get("/users/{username}", response_model=UserResponse)
def get_user(username: str, current_user: dict = Depends(get_current_user)):

    with engine.connect() as connection:
        row = connection.execute(
            text(f"""
                SELECT {USER_COLUMNS}
                FROM identity.users
                WHERE username = :username
            """),
            {"username": username},
        ).mappings().first()

    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    return row