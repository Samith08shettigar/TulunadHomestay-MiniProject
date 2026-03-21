import sqlite3
import os
from flask import g, current_app


def get_db():
    """Get a database connection, storing it on the Flask g object."""
    if 'db' not in g:
        db_path = os.path.join(current_app.instance_path, 'homestay.db')
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    """Close the database connection stored on the Flask g object."""
    db = g.pop('db', None)
    if db is not None:
        db.close()
