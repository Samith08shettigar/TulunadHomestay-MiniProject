from werkzeug.security import generate_password_hash
from app import create_app
from database import get_db


def seed():
    """Seed the database with an admin user and sample rooms."""
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
            print('✅ Admin user created.')
        else:
            print('ℹ️  Admin user already exists, skipping.')

        # --- Sample Rooms ---
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

            db.executemany(
                'INSERT INTO rooms (room_name, price, capacity, description, image_url, availability) VALUES (?, ?, ?, ?, ?, ?)',
                rooms
            )
            print('✅ 3 sample rooms created.')
        else:
            print(f'ℹ️  {existing_rooms} room(s) already exist, skipping.')

        db.commit()
        print('🌱 Seeding complete!')


if __name__ == '__main__':
    seed()
