from werkzeug.security import generate_password_hash
from app import create_app
from database import get_db
from models import ALL_ROOMS_DATA


def seed():
    """Seed the database with default admin user and all 10 verified rooms with gallery images."""
    app = create_app()

    with app.app_context():
        db = get_db()

        # --- Admin User ---
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
            print('[OK] Admin user created.')
        else:
            print('[INFO] Admin user already exists, skipping.')

        # --- Seed All 10 Rooms ---
        existing_rooms = db.execute('SELECT COUNT(*) FROM rooms').fetchone()
        room_count = existing_rooms[0] if existing_rooms else 0

        if room_count == 0:
            for item in ALL_ROOMS_DATA:
                cursor = db.execute(
                    '''INSERT INTO rooms (room_name, price, capacity, description, image_url, availability)
                       VALUES (?, ?, ?, ?, ?, ?)''',
                    (
                        item["room_name"],
                        item["price"],
                        item["capacity"],
                        item["description"],
                        item["image_url"],
                        item["availability"]
                    )
                )
                room_id = cursor.lastrowid
                if not room_id:
                    r = db.execute('SELECT id FROM rooms WHERE room_name = ?', (item["room_name"],)).fetchone()
                    if r:
                        room_id = r[0] if isinstance(r, (tuple, list)) else r["id"]

                if room_id and "gallery" in item:
                    for sort_idx, g_img in enumerate(item["gallery"]):
                        db.execute(
                            'INSERT INTO room_images (room_id, image_url, sort_order) VALUES (?, ?, ?)',
                            (room_id, g_img, sort_idx)
                        )
            print(f'[OK] All {len(ALL_ROOMS_DATA)} rooms and gallery images seeded successfully.')
        else:
            print(f'[INFO] {room_count} room(s) already exist, skipping.')

        db.commit()
        print('[DONE] Seeding complete!')


if __name__ == '__main__':
    seed()
