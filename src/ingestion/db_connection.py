import os
from pathlib import Path

import pg8000.dbapi as db
from dotenv import load_dotenv


def get_connection():
    # Find and load the .env file
    project_root = Path(__file__).resolve().parents[2]
    load_dotenv(project_root / ".env")

    # Validate required settings
    required = [
        "DB_HOST",
        "DB_PORT",
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD",
    ]

    missing = [name for name in required if not os.getenv(name)]

    if missing:
        raise ValueError(f"Missing database settings: {missing}")

    # Validate the port
    try:
        port = int(os.environ["DB_PORT"])
    except ValueError as exc:
        raise ValueError("DB_PORT must be an integer") from exc

    # Connect to PostgreSQL
    return db.connect(
        host=os.environ["DB_HOST"],
        port=port,
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )