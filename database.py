import os
import sqlite3
from flask import g, current_app

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    psycopg2 = None


def get_database_url():
    """Retrieve DATABASE_URL from environment with postgresql:// normalization."""
    db_url = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL')
    if db_url and db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    return db_url


def is_postgres():
    """Return True if PostgreSQL DATABASE_URL is configured."""
    return bool(get_database_url() and psycopg2 is not None)


class PostgresRow:
    """Row wrapper that supports both dict-key and integer-index access (like sqlite3.Row)."""
    def __init__(self, data_dict, tuple_data, keys):
        self._dict = data_dict
        self._tuple = tuple_data
        self._keys = keys

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._tuple[key]
        return self._dict[key]

    def get(self, key, default=None):
        return self._dict.get(key, default)

    def keys(self):
        return self._keys

    def __contains__(self, key):
        return key in self._dict

    def __iter__(self):
        return iter(self._tuple)

    def __len__(self):
        return len(self._tuple)

    def __repr__(self):
        return f"<Row {self._dict}>"


class PostgresCursorWrapper:
    def __init__(self, cursor, lastrowid=None):
        self._cursor = cursor
        self.lastrowid = lastrowid

    def _convert_row(self, row):
        if row is None:
            return None
        keys = list(row.keys())
        tuple_data = tuple(row[k] for k in keys)
        return PostgresRow(dict(row), tuple_data, keys)

    def fetchone(self):
        row = self._cursor.fetchone()
        return self._convert_row(row)

    def fetchall(self):
        rows = self._cursor.fetchall()
        return [self._convert_row(r) for r in rows]

    @property
    def rowcount(self):
        return self._cursor.rowcount


class PostgresConnectionWrapper:
    def __init__(self, conn):
        self._conn = conn

    def _prepare_sql(self, sql):
        """Convert SQLite '?' placeholders to PostgreSQL '%s'."""
        return sql.replace('?', '%s')

    def execute(self, sql, params=None):
        pg_sql = self._prepare_sql(sql)
        is_insert = pg_sql.strip().upper().startswith('INSERT INTO')
        
        cursor = self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        lastrowid = None
        
        if is_insert and 'RETURNING' not in pg_sql.upper():
            try_sql = pg_sql.rstrip().rstrip(';') + ' RETURNING id'
            try:
                if params:
                    cursor.execute(try_sql, params)
                else:
                    cursor.execute(try_sql)
                ret = cursor.fetchone()
                if ret and 'id' in ret:
                    lastrowid = ret['id']
                return PostgresCursorWrapper(cursor, lastrowid=lastrowid)
            except Exception:
                self._conn.rollback()
                cursor = self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        if params:
            cursor.execute(pg_sql, params)
        else:
            cursor.execute(pg_sql)
        return PostgresCursorWrapper(cursor, lastrowid=lastrowid)

    def executemany(self, sql, seq_of_params):
        pg_sql = self._prepare_sql(sql)
        cursor = self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.executemany(pg_sql, seq_of_params)
        return PostgresCursorWrapper(cursor)

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()


def get_db():
    """Get a database connection, storing it on the Flask g object.
    Supports PostgreSQL when DATABASE_URL is set, and SQLite homestay.db otherwise.
    """
    if 'db' not in g:
        db_url = get_database_url()
        if db_url and psycopg2 is not None:
            conn = psycopg2.connect(db_url)
            g.db = PostgresConnectionWrapper(conn)
        else:
            db_path = os.path.join(current_app.instance_path, 'homestay.db')
            os.makedirs(current_app.instance_path, exist_ok=True)
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            g.db = conn
    return g.db


def close_db(e=None):
    """Close the database connection stored on the Flask g object."""
    db = g.pop('db', None)
    if db is not None:
        db.close()
