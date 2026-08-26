import getpass
import sys

from argon2 import PasswordHasher
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from database import engine

ph = PasswordHasher()


def prompt(label: str, validate=None) -> str:
    while True:
        value = input(f"{label}: ").strip()
        if not value:
            print("  required.")
            continue
        if validate and not validate(value):
            print("  invalid value, try again.")
            continue
        return value


def main() -> None:
    print("Create admin account\n" + "-" * 21)

    username  = prompt("Username (letters/digits/underscore)",
                       lambda v: v.replace("_", "").isalnum())
    full_name = prompt("Full name")
    branch    = prompt("Branch/department")
    roll_num  = prompt("Roll/employee number").upper()
    age       = prompt("Age", lambda v: v.isdigit() and 13 <= int(v) <= 120)
    email     = prompt("Email").lower()
    phone     = prompt("Phone (e.g. +919876543210, digits only)")

    password = getpass.getpass("Password (min 8 characters): ")
    confirm  = getpass.getpass("Confirm password: ")
    if password != confirm:
        print("Passwords do not match.")
        sys.exit(1)
    if len(password) < 8:
        print("Password must be at least 8 characters.")
        sys.exit(1)

    try:
        with engine.begin() as connection:
            connection.execute(
                text("""
                    INSERT INTO identity.users
                        (username, full_name, branch, roll_num,
                         age, email, phone, password_hash, role)
                    VALUES
                        (:username, :full_name, :branch, :roll_num,
                         :age, :email, :phone, :password_hash, 'admin')
                """),
                {
                    "username": username,
                    "full_name": full_name,
                    "branch": branch,
                    "roll_num": roll_num,
                    "age": int(age),
                    "email": email,
                    "phone": phone,
                    "password_hash": ph.hash(password),
                },
            )
    except IntegrityError as error:
        # .orig is the raw psycopg2 error — covers both "already taken"
        # and constraint failures like a malformed phone number.
        print(f"\nCould not create the account: {getattr(error, 'orig', error)}")
        sys.exit(1)

    print(f"\nAdmin '{username}' created.")


if __name__ == "__main__":
    main()
