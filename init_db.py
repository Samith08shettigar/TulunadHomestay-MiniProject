import os
import sys
import logging
from app import create_app
from database import get_db, is_postgres, get_database_url
from models import create_tables

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def init_database():
    """Initialize database tables and seed verified homestay data."""
    db_url = get_database_url()
    if db_url:
        # Mask credentials safely for logging
        if "@" in db_url:
            masked_target = db_url.split("@")[-1]
        else:
            masked_target = "configured"
        logging.info("DATABASE_URL is configured (target: %s)", masked_target)
    else:
        logging.info("No remote DATABASE_URL configured. Local SQLite fallback active.")

    app = create_app()
    with app.app_context():
        db = get_db()
        pg_active = is_postgres()
        logging.info("Active Database Engine: %s", "PostgreSQL" if pg_active else "SQLite")

        logging.info("Running create_tables()...")
        create_tables()

        # Table verification
        if pg_active:
            res = db.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name"
            ).fetchall()
            table_names = [r["table_name"] if hasattr(r, "keys") else r[0] for r in res]
        else:
            res = db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
            ).fetchall()
            table_names = [r[0] for r in res]

        logging.info("Verified tables in database: %s", table_names)

        # Count verification
        try:
            users_cnt = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            rooms_cnt = db.execute("SELECT COUNT(*) FROM rooms").fetchone()[0]
            images_cnt = db.execute("SELECT COUNT(*) FROM room_images").fetchone()[0]
            logging.info("Data verification -> Users: %s | Rooms: %s | Gallery Images: %s", users_cnt, rooms_cnt, images_cnt)
        except Exception as e:
            logging.warning("Count check warning: %s", e)

        logging.info("Database initialization completed successfully.")


if __name__ == "__main__":
    init_database()
