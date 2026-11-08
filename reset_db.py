import sqlite3
from pathlib import Path
from mysite.database.db import engine, Base
import mysite.database.models  # Ensure models are loaded

def reset_database():
    db_path = Path(__file__).resolve().parent / "coursera.db"
    
    # Drop all existing tables
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    for (t,) in tables:
        if not t.startswith("sqlite_"):
            cur.execute(f"DROP TABLE IF EXISTS {t};")
    conn.commit()
    conn.close()

    # Recreate all tables cleanly
    Base.metadata.create_all(bind=engine)
    print("✓ Маалыматтар базасы нөлдөн (0-дөн) ийгиликтүү тазаланды жана баардык таблицалар кайра түзүлдү!")

if __name__ == "__main__":
    reset_database()
