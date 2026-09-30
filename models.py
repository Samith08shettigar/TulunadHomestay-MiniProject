from database import get_db, is_postgres
from werkzeug.security import generate_password_hash


def create_tables():
    """Create all database tables if they don't already exist.
    Supports both PostgreSQL and SQLite.
    """
    db = get_db()

    if is_postgres():
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'user'
            )
        ''')

        db.execute('''
            CREATE TABLE IF NOT EXISTS rooms (
                id SERIAL PRIMARY KEY,
                room_name TEXT NOT NULL,
                price REAL NOT NULL,
                capacity INTEGER NOT NULL,
                description TEXT,
                image_url TEXT,
                availability INTEGER DEFAULT 1
            )
        ''')

        db.execute('''
            CREATE TABLE IF NOT EXISTS room_images (
                id SERIAL PRIMARY KEY,
                room_id INTEGER NOT NULL,
                image_url TEXT NOT NULL,
                sort_order INTEGER DEFAULT 0,
                FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
            )
        ''')

        db.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                room_id INTEGER NOT NULL,
                checkin_date TEXT NOT NULL,
                checkout_date TEXT NOT NULL,
                meal_type TEXT,
                fire_camp TEXT,
                status TEXT DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (room_id) REFERENCES rooms (id)
            )
        ''')

        db.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                booking_id INTEGER NOT NULL,
                rating INTEGER NOT NULL,
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (booking_id) REFERENCES bookings (id)
            )
        ''')
    else:
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'user'
            )
        ''')

        db.execute('''
            CREATE TABLE IF NOT EXISTS rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_name TEXT NOT NULL,
                price REAL NOT NULL,
                capacity INTEGER NOT NULL,
                description TEXT,
                image_url TEXT,
                availability INTEGER DEFAULT 1
            )
        ''')

        db.execute('''
            CREATE TABLE IF NOT EXISTS room_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_id INTEGER NOT NULL,
                image_url TEXT NOT NULL,
                sort_order INTEGER DEFAULT 0,
                FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
            )
        ''')

        db.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                room_id INTEGER NOT NULL,
                checkin_date TEXT NOT NULL,
                checkout_date TEXT NOT NULL,
                meal_type TEXT,
                fire_camp TEXT,
                status TEXT DEFAULT 'Pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (room_id) REFERENCES rooms (id)
            )
        ''')

        db.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                booking_id INTEGER NOT NULL,
                rating INTEGER NOT NULL,
                comment TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (booking_id) REFERENCES bookings (id)
            )
        ''')

    db.commit()

    # Automatically seed default admin and sample rooms on first initialization
    _auto_seed(db)


def _auto_seed(db):
    """Seed admin user and sample rooms if empty."""
    try:
        existing = db.execute(
            'SELECT id FROM users WHERE email = ?', ('admin@tulunad.com',)
        ).fetchone()

        if not existing:
            db.execute(
                'INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)',
                (
                    'Admin',
                    'admin@tulunad.com',
                    generate_password_hash('admin123'),
                    'admin'
                )
            )

        existing_rooms = db.execute('SELECT COUNT(*) FROM rooms').fetchone()[0]
        if existing_rooms == 0:
            rooms = [
                (
                    'Forest View Cottage',
                    2500.0,
                    2,
                    'A cozy cottage nestled among lush green forests with a breathtaking view of the Western Ghats. Perfect for couples seeking a peaceful retreat.',
                    'https://images.unsplash.com/photo-1587061949409-02df41d5e562?w=800',
                    1
                ),
                (
                    'Riverside Bamboo Hut',
                    3500.0,
                    4,
                    'A spacious bamboo hut by the river, surrounded by tropical greenery. Wake up to the sounds of flowing water and birdsong.',
                    'https://images.unsplash.com/photo-1499696010180-025ef6e1a8f9?w=800',
                    1
                ),
                (
                    'Treetop Nature Lodge',
                    4500.0,
                    6,
                    'An elevated lodge offering panoramic views of the dense forest canopy. Ideal for families and groups looking for an adventurous stay.',
                    'https://images.unsplash.com/photo-1510798831971-661eb04b3739?w=800',
                    1
                ),
            ]
            for room in rooms:
                db.execute(
                    'INSERT INTO rooms (room_name, price, capacity, description, image_url, availability) VALUES (?, ?, ?, ?, ?, ?)',
                    room
                )

        db.commit()
    except Exception as e:
        print(f"[INFO] Auto-seeding skipped or already initialized: {e}")
        try:
            db.rollback()
        except Exception:
            pass
