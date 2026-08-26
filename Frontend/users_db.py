import os
import re
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

BASE_URL = os.environ.get("SENTINEL_API_URL", "http://127.0.0.1:8000").rstrip("/")
TIMEOUT = 8  # seconds

# Set by every call that talks to the backend. login.py / register.py
# read this to show *why* a request failed (bad credentials vs. an
# unreachable server) instead of a generic error.
last_error = None

_access_token = None


def get_token():
    return _access_token


def is_logged_in() -> bool:
    return _access_token is not None


def logout():
    global _access_token
    _access_token = None


def _request(method: str, path: str, auth: bool = True, **kwargs):
    global last_error, _access_token

    headers = dict(kwargs.pop("headers", {}))
    if auth and _access_token:
        headers["Authorization"] = f"Bearer {_access_token}"

    try:
        response = requests.request(
            method, f"{BASE_URL}{path}", timeout=TIMEOUT,
            headers=headers, **kwargs
        )
    except requests.exceptions.ConnectionError:
        last_error = f"Can't reach the server at {BASE_URL}. Is it running?"
        return None
    except requests.exceptions.Timeout:
        last_error = "The server took too long to respond."
        return None
    except requests.exceptions.RequestException as error:
        last_error = str(error)
        return None

    if response.status_code == 401 and _access_token:
        _access_token = None
        try:
            detail = response.json().get("detail", "")
        except ValueError:
            detail = ""
        last_error = (
            "Your session expired. Please log in again."
            if "expired" in str(detail).lower()
            else "Your session is no longer valid. Please log in again."
        )
        return None

    if response.status_code >= 400:
        try:
            detail = response.json().get("detail")
        except ValueError:
            detail = None

        if isinstance(detail, list):
            # FastAPI/Pydantic validation errors: a list of
            # {"loc": [...], "msg": "...", ...} dicts.
            last_error = "; ".join(str(item.get("msg", item)) for item in detail)
        elif detail:
            last_error = str(detail)
        else:
            last_error = response.text or f"Server error ({response.status_code})"
        return None

    last_error = None
    try:
        return response.json()
    except ValueError:
        return {}


def _get(path: str, auth: bool = True):
    return _request("GET", path, auth=auth)


def _post(path: str, payload: dict, auth: bool = True):
    return _request("POST", path, auth=auth, json=payload)


def _to_profile(user: dict) -> dict:
    """Map the backend's column names onto what the GUI screens read."""
    return {
        "username":   user.get("username"),
        "name":       user.get("full_name"),
        "roll":       user.get("roll_num"),
        "branch":     user.get("branch"),
        "email":      user.get("email"),
        "phone":      user.get("phone"),
        "role":       user.get("role"),
        "status":     "Active" if user.get("is_active") else "Inactive",
        "age":        user.get("age"),
        "created_at": user.get("created_at"),
    }


# ---------------------------------------------------------------- lifecycle

def init_db():
    """No local database to create — just confirm the backend (and its
    connection to Postgres) is reachable before the UI starts making
    login/register calls."""
    global last_error
    health = _get("/health", auth=False)
    if health is None:
        return  # last_error already set by _get
    if health.get("database") != "connected":
        last_error = "The server is up but can't reach the database."


def seed_demo_users():
    """No-op: demo seeding was local-only (SQLite) and isn't wired to
    the backend. Use backend/create_admin.py for a real admin account."""
    pass


def seed_demo_events():
    """No-op: surveillance events aren't wired to the backend yet."""
    pass


# ---------------------------------------------------------------- auth

def authenticate(username: str, password: str):
    global _access_token

    result = _post(
        "/login",
        {"username": username, "password": password},
        auth=False,
    )
    if result is None:
        return None

    _access_token = result.get("access_token")
    return _to_profile(result.get("user", {}))


def add_user(username, password, role, age, name, phone, roll, branch, email) -> bool:
    """Register a new member. `role` is accepted for interface
    compatibility but ignored — the backend always creates 'member'
    accounts on self-registration; admins are provisioned separately."""
    # The GUI's own validation allows spaces/dashes in phone numbers
    # for readability; the backend requires digits only (plus a
    # leading +), so normalize here rather than tightening what people
    # can type into the form.
    normalized_phone = re.sub(r"[\s\-]", "", phone)

    payload = {
        "username": username,
        "full_name": name,
        "branch": branch,
        "roll_num": roll,
        "age": age,
        "email": email,
        "phone": normalized_phone,
        "password": password,
        "re_enter_password": password,
    }
    user = _post("/register", payload, auth=False)
    return user is not None



def username_exists(username: str) -> bool:
    result = _get(f"/username-available/{username}", auth=False)
    if result is None:
        return False
    return not result.get("available", True)


def get_user_profile(username: str):
    user = _get(f"/users/{username}")
    if user is None:
        return None
    return _to_profile(user)


# ---------------------------------------------------------- not yet wired

def get_all_members():
    return []


def get_all_users():
    return []


def log_activity(username: str, action: str, details: str = ""):
    pass


def get_recent_activity(limit: int = 50):
    return []


def get_recent_events(limit: int = 50):
    return []


def add_event(camera_id, event_type, location="", description="", severity="info"):
    return False
