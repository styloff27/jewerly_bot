import sqlite3
from pathlib import Path

DB_DIR = Path(__file__).resolve().parent
DB_PATH = DB_DIR / "jewelry_ops.db"
SEED_PATH = DB_DIR / "seed.sql"
SCHEMA_PATH = DB_DIR / "schema.sql"

def get_connection():
    """Return a connection to the JewelryOps database. Creates DB and seeds if missing."""
    if not DB_PATH.exists():
        _init_db()
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # rows as dict-like objects
    return conn


def _init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.executescript(SCHEMA_PATH.read_text())
    conn.executescript(SEED_PATH.read_text())
    conn.commit()
    conn.close()
