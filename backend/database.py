import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv(Path(__file__).parent / ".env")

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    host     = os.environ.get("PGHOST", "localhost")
    port     = os.environ.get("PGPORT", "5432")
    database = os.environ.get("PGDATABASE", "sentinel_db")
    user     = os.environ.get("PGUSER", "postgres")
    password = os.environ.get("PGPASSWORD")

    if not password:
        raise RuntimeError(
            "No database configured. Copy backend/.env.example to "
            "backend/.env and fill in your PostgreSQL connection details "
            "(or set DATABASE_URL / PGPASSWORD as real environment "
            "variables)."
        )

    DATABASE_URL = (
        f"postgresql://{user}:{quote_plus(password)}@{host}:{port}/{database}"
    )

engine = create_engine(DATABASE_URL)
