import argparse
import sys
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from database import engine

# Anchored to this file, not the working directory — so it still
# works when launched from a parent dir, an IDE, or a container.
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def confirm() -> bool:
    print(f"  target : {engine.url.render_as_string(hide_password=True)}")
    print(f"  script : {SCHEMA_PATH.name}")
    print("\nThis DROPs the 'identity' schema. All data in it is lost.")
    return input("Type 'yes' to continue: ").strip().lower() == "yes"


def run_schema() -> None:
    sql = SCHEMA_PATH.read_text(encoding="utf-8")

    with engine.begin() as connection:
        # exec_driver_sql, NOT text(): the trigger body uses $$ quoting
        # and SQLAlchemy's text() would try to read ':' as bind params.
        connection.exec_driver_sql(sql)


def verify() -> None:
    with engine.connect() as connection:
        rows = connection.execute(
            text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'identity' AND table_name = 'users'
                ORDER BY ordinal_position
            """)
        ).all()

    if not rows:
        print("identity.users not found — schema did not apply.")
        sys.exit(1)

    print(f"\nidentity.users — {len(rows)} columns\n")
    for name, dtype, nullable in rows:
        null = "NULL" if nullable == "YES" else "NOT NULL"
        print(f"  {name:<16} {dtype:<28} {null}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true",
                        help="skip the confirmation prompt")
    args = parser.parse_args()

    if not SCHEMA_PATH.exists():
        print(f"schema.sql not found at {SCHEMA_PATH}")
        sys.exit(1)

    if not args.force and not confirm():
        print("Aborted.")
        sys.exit(0)

    try:
        run_schema()
    except SQLAlchemyError as error:
        # .orig is the raw psycopg2 error — the useful half.
        print(f"\nSchema failed: {getattr(error, 'orig', error)}")
        sys.exit(1)

    print("\nSchema applied.")
    verify()


if __name__ == "__main__":
    main()