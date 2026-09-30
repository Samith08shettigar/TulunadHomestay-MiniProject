import os
from database import get_db, is_postgres
from werkzeug.security import generate_password_hash

# Complete verified dataset of all 10 Tulunad Homestay rooms with their 40 gallery images
ALL_ROOMS_DATA = [
    {
        "room_name": "Urban Retreat Homestay (Mangalore)",
        "price": 5000.0,
        "capacity": 6,
        "description": "About this property\r\nComfortable Accommodation: Urban Retreat Homestay in Mangalore offers family rooms with private bathrooms. Each room includes air-conditioning, a TV, and free toiletries.\r\n\r\nOutdoor Spaces: Guests can relax in the garden or on the terrace. The property features a lounge, outdoor seating area, and picnic spots.\r\n\r\nConvenient Facilities: The homestay provides free WiFi, a shared kitchen, and a 24-hour front desk. Additional amenities include free on-site private parking, car hire, and breakfast in the room.\r\n\r\nPrime Location: Located 14 km from Mangalore International Airport and near attractions such as Kadri Manjunath Temple (9 km) and Mangala Devi Temple (13 km). Guests appreciate the attentive staff and room cleanliness.",
        "image_url": "/static/uploads/rooms/e877213b715e4080ad4dd8292e9cf846.jpg",
        "availability": 1,
        "gallery": [
            "/static/uploads/rooms/2f23a2b0ed9a4ee88399429a3ab23ff8.jpg",
            "/static/uploads/rooms/4bc9e2a2533f42a9a939a291bbeb5d4e.jpg",
            "/static/uploads/rooms/89b9b5f47a68468394f8297b72134bdf.jpg",
            "/static/uploads/rooms/8553e298f69548058a6f146fef5aff23.jpg"
        ]
    },
    {
        "room_name": "SaffronStays Blue Flag House (Mangalore)",
        "price": 10000.0,
        "capacity": 10,
        "description": "About this property\r\nBeachfront Location: SaffronStays Blue Flag House in Mangalore offers a private beach area and direct beachfront access. Guests can relax in the garden or enjoy the sea views from the balcony.\r\n\r\nSpacious Accommodation: The homestay features three bedrooms and three bathrooms, ensuring ample space for all visitors. The living room provides a comfortable area for relaxation.\r\n\r\nModern Amenities: Free WiFi is available throughout the property. Additional facilities include air-conditioning, a fully equipped kitchen, and free on-site parking.\r\n\r\nLocal Attractions: Mangalore International Airport is 28 km away. Nearby attractions include Kadri Manjunath Temple and Gokarnanatheshwara Temple, each 30 km from the property.",
        "image_url": "/static/uploads/rooms/38780ce90e384cf090c3063932442c36.jpg",
        "availability": 1,
        "gallery": [
            "/static/uploads/rooms/19ef3115df4b4e269a33ed97f46509f8.jpg",
            "/static/uploads/rooms/b5fec54c0db4459cb90510c8e2babdfe.jpg",
            "/static/uploads/rooms/a65ba5ace84b445a90f5ea3c3f22207f.jpg",
            "/static/uploads/rooms/db93595a6c204c8f9ece1627d5922aaa.jpg"
        ]
    },
    {
        "room_name": "Runnin' Airport- HomeStay (Mangalore)",
        "price": 2500.0,
        "capacity": 4,
        "description": "About this property\r\nComfortable Accommodations: Runnin' Airport- HomeStay near Mangalore International airport in Mangalore offers family rooms with air-conditioning, private bathrooms, and garden views. Each room includes a dining area, work desk, and free WiFi.\r\n\r\nDining Experience: The family-friendly restaurant serves Indian, seafood, and local cuisines in a traditional and modern ambience. Guests can enjoy lunch, dinner, and high tea with halal and vegetarian options.\r\n\r\nLeisure Facilities: The homestay features a sun terrace, garden, fitness room, and outdoor seating areas. Additional amenities include a swimming pool, indoor and outdoor play areas, and free on-site parking.\r\n\r\nLocation and Attractions: Located 3 km from Mangalore International Airport, the homestay is 19 km from Mangalore Central Station and close to Kadri Manjunath Temple (16 km) and Gokarnanatheshwara Temple (17 km)",
        "image_url": "/static/uploads/rooms/5d23a157fead4e2594741e0de5559be5.jpg",
        "availability": 1,
        "gallery": [
            "/static/uploads/rooms/c24fdd1d01034dedbd71a0b0c17a0bc4.jpg",
            "/static/uploads/rooms/75626e9479b64e5288b916f46f503ad2.jpg",
            "/static/uploads/rooms/5520b4a0ab2e4cb18286fc6def4846ab.jpg",
            "/static/uploads/rooms/965c2e542b2e4e4cb2562f041c36cb03.jpg"
        ]
    },
    {
        "room_name": "Anuradha Homestay (Mangalore)",
        "price": 25000.0,
        "capacity": 15,
        "description": "About this property\r\nComfortable Accommodation: Anuradha Homestay in Mangalore offers family rooms with air-conditioning, private bathrooms, and balconies. Each room includes a kitchenette, bathrobes, and free WiFi.\r\n\r\nLeisure Facilities: Guests can relax in the garden, on the terrace, or by the year-round outdoor swimming pool. The property features a shared kitchen, pool bar, and dining area.\r\n\r\nConvenient Location: Located 20 km from Mangalore International Airport and 21 km from Mangalore Central Station, the homestay is near attractions such as Kadri Manjunath Temple (18 km) and Gokarnanatheshwara Temple (22 km).",
        "image_url": "/static/uploads/rooms/f16214c4d16b4f61a6b1fee4f04fdb95.jpg",
        "availability": 1,
        "gallery": [
            "/static/uploads/rooms/1eceed32df214859b2b88f4888b9a6b2.jpg",
            "/static/uploads/rooms/9a51d134766249c5ae677495773a20d0.jpg",
            "/static/uploads/rooms/a632d84dcb444e5a89ac6ad762060eb1.jpg",
            "/static/uploads/rooms/d2deecc2999141269654ddb0826ee441.jpg"
        ]
    },
    {
        "room_name": "The Beach Villa by Sunny Smiles (Mangalore)",
        "price": 6000.0,
        "capacity": 6,
        "description": "About this property\r\nComfortable Accommodation: The Beach Villa by Sunny Smiles in Mangalore offers a guest house with a garden and terrace. Free WiFi is available throughout the property.\r\n\r\nModern Amenities: Each room features a private bathroom, air-conditioning, and sea views. Additional amenities include a tea and coffee maker, hairdryer, dining table, refrigerator, free toiletries, shower, TV, electric kettle, kitchenware, and wardrobe.\r\n\r\nConvenient Location: Surathkal Beach is just a few steps away. Mangalore Central Station is 16 km, Kadri Manjunath Temple and Gokarnanatheshwara Temple are 14 km, and Mangala Devi Temple is 18 km from the property. Mangalore International Airport is 13 km distant.",
        "image_url": "/static/uploads/rooms/1bbe2be7e1dc4ec39aba835a0f0b5422.jpg",
        "availability": 1,
        "gallery": [
            "/static/uploads/rooms/ba0fe11e80c84c2c87bf599c4c44e3d0.jpg",
            "/static/uploads/rooms/54e17e283cb84751ab2194ac2e261247.jpg",
            "/static/uploads/rooms/accbd023fd3d49d188d57f3a7ffc5a68.jpg",
            "/static/uploads/rooms/9392ced14c8145ebaf2b6e184019fcfa.jpg"
        ]
    },
    {
        "room_name": "Monappa Estate - Top Rated - Luxury Villa (Udupi)",
        "price": 30000.0,
        "capacity": 10,
        "description": "About this property\r\nSpacious Accommodation: Monappa Estate in Udupi offers a spacious villa with five bedrooms and five bathrooms. The property features a living room, dining area, and family rooms, ensuring comfort for all guests.\r\n\r\nOutdoor Amenities: Guests can relax on the sun terrace or in the lush garden. The villa includes an outdoor fireplace, outdoor dining area, and picnic spots, perfect for leisure activities.\r\n\r\nModern Facilities: The villa provides free WiFi, air-conditioning, and a fully equipped kitchen. Additional amenities include a coffee shop, barbecue facilities, and free on-site parking.\r\n\r\nConvenient Location: Located 74 km from Mangalore International Airport, the property offers easy access to local attractions. Walking tours and bicycle parking enhance the guest experience.",
        "image_url": "/static/uploads/rooms/a4e5676ec4b542a097df24cc59e01dd9.jpg",
        "availability": 1,
        "gallery": [
            "/static/uploads/rooms/da15d00dfa704f1abad3dcf50a946d6a.jpg",
            "/static/uploads/rooms/4eb25ea02d324c76b7878e556f90bf01.jpg",
            "/static/uploads/rooms/4746a8f9772e4334b5f447c430b549e1.jpg",
            "/static/uploads/rooms/2fecab614e5845f2a6c2f13cd550e322.jpg"
        ]
    },
    {
        "room_name": "Navasharada's White Sand Beach House (Udupi)",
        "price": 5000.0,
        "capacity": 4,
        "description": "About this property\r\nElegant Accommodation: Navasharada's White Sand Beach House in Udupi offers a country house experience with a beautiful garden and free WiFi. Guests can relax in the outdoor seating area and enjoy sea views.\r\n\r\nComfortable Amenities: The property features air-conditioning, private bathrooms with free toiletries, refrigerators, electric kettles, and soundproofing. Additional amenities include a shower, wardrobe, and free on-site private parking.\r\n\r\nConvenient Services: Private check-in and check-out, a 24-hour front desk, daily housekeeping, and full-day security ensure a comfortable stay. Mangalore International Airport is 56 km away.",
        "image_url": "/static/uploads/rooms/91a417ea87114c56a9950299d8bbed0a.jpg",
        "availability": 1,
        "gallery": [
            "/static/uploads/rooms/04f29506806d43578d6904e303760d88.jpg",
            "/static/uploads/rooms/bf3647bda96d42c686d39dd5f2de8513.jpg",
            "/static/uploads/rooms/dd9d2b8994394a668ad818411f10fd2d.jpg",
            "/static/uploads/rooms/b97d72d13ef14bb5aaa925cd1ca9f6e6.jpg"
        ]
    },
    {
        "room_name": "White Serenity Villa (Udupi)",
        "price": 8500.0,
        "capacity": 6,
        "description": "About this property\r\nElegant Accommodation: White Serenity Villa Udupi in Udupi offers a serene garden and complimentary WiFi. Guests can relax in the outdoor seating area or enjoy the lake and garden views.\r\n\r\nComfortable Amenities: The villa features air-conditioning, a kitchenette, washing machine, and private bathroom. Additional amenities include a dining area, sofa, and TV. Free on-site private parking is available.\r\n\r\nDelightful Breakfast: A vegetarian breakfast is served daily, catering to diverse dietary needs.\r\n\r\nConvenient Location: Located 71 km from Mangalore International Airport, the property provides easy access to local attractions.",
        "image_url": "/static/uploads/rooms/ddbf207457e74779a8725fd41641fd8b.jpg",
        "availability": 1,
        "gallery": [
            "/static/uploads/rooms/0ac1bde03cbb4c748276bb3fe06cc68d.jpg",
            "/static/uploads/rooms/0bdfe6bb50154c7aa2139d3248d89bea.jpg",
            "/static/uploads/rooms/3b97b092da21428fb5e4b76df80eca83.jpg",
            "/static/uploads/rooms/4465e44645294cf4a632ae38fc8def82.jpg"
        ]
    },
    {
        "room_name": "Willo Stays Luxe Heritage Home (Udupi)",
        "price": 15000.0,
        "capacity": 8,
        "description": "About this property\r\nBeachfront Location: Willo Stays Luxe Heritage Home in Udupi offers direct access to a private beach area and beachfront. Guests enjoy stunning garden views and a spacious terrace.\r\n\r\nComfortable Accommodation: The holiday home features four bedrooms and four bathrooms, a living room, and a fully equipped kitchen. Air-conditioning, a washing machine, and free WiFi ensure a comfortable stay.\r\n\r\nLeisure Facilities: The property includes a private check-in and check-out service, an outdoor seating area, a picnic spot, and a children's playground. Free on-site private parking is available.\r\n\r\nNearby Attractions: Mangalore International Airport is 60 km away. Malpe-Padukere Main Bridge is 5 km from the property, providing easy access to local attractions.",
        "image_url": "/static/uploads/rooms/93d01e7de7e448bd850605d011454ab7.jpg",
        "availability": 1,
        "gallery": [
            "/static/uploads/rooms/ade054aed38743aca51c71c0d6d1803c.jpg",
            "/static/uploads/rooms/9c2fbc0b9c2d408eaf13e2f059ed706f.jpg",
            "/static/uploads/rooms/6bbbc648c31e4501825d14d3d9f98df7.jpg",
            "/static/uploads/rooms/f5bc1421e89f414f9fde5a56fb07e794.jpg"
        ]
    },
    {
        "room_name": "Beach at the White House (Udupi)",
        "price": 15000.0,
        "capacity": 8,
        "description": "About this property\r\nBeachfront Location: Beach at the White House in Udupi offers a private beach area and direct beachfront access. Guests enjoy sea views and a serene garden setting.\r\n\r\nSpacious Accommodation: The villa features two bedrooms and four bathrooms, providing ample space for relaxation. Each room includes air-conditioning, a balcony, and a terrace.\r\n\r\nModern Amenities: Free WiFi, a fully equipped kitchen, and a washing machine ensure comfort. Additional facilities include a work desk, private entrance, and free on-site parking.\r\n\r\nLocal Attractions: Hoode Beach is just a few steps away, while Delta Beach is a 13-minute walk. Mangalore International Airport is 65 km from the property. Highly rated by guests.",
        "image_url": "/static/uploads/rooms/698db24e99df49a98a9c306f8fb9081b.jpg",
        "availability": 1,
        "gallery": [
            "/static/uploads/rooms/7372eaf87bec42d4b182d6ba03cf59f5.jpg",
            "/static/uploads/rooms/168a9ae14ef94243a29da7e76f67136a.jpg",
            "/static/uploads/rooms/ae2c95facf1d49d4b06342a3f1bf09bc.jpg",
            "/static/uploads/rooms/00b7fd6a53e741979b4f84440db79517.jpg"
        ]
    }
]


def create_tables():
    """Create all database tables if they don't already exist.
    Supports both PostgreSQL and SQLite.
    """
    try:
        db = get_db()

        if is_postgres():
            statements = [
                '''CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT DEFAULT 'user'
                )''',
                '''CREATE TABLE IF NOT EXISTS rooms (
                    id SERIAL PRIMARY KEY,
                    room_name TEXT NOT NULL,
                    price REAL NOT NULL,
                    capacity INTEGER NOT NULL,
                    description TEXT,
                    image_url TEXT,
                    availability INTEGER DEFAULT 1
                )''',
                '''CREATE TABLE IF NOT EXISTS room_images (
                    id SERIAL PRIMARY KEY,
                    room_id INTEGER NOT NULL,
                    image_url TEXT NOT NULL,
                    sort_order INTEGER DEFAULT 0,
                    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
                )''',
                '''CREATE TABLE IF NOT EXISTS bookings (
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
                )''',
                '''CREATE TABLE IF NOT EXISTS feedback (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    booking_id INTEGER NOT NULL,
                    rating INTEGER NOT NULL,
                    comment TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (booking_id) REFERENCES bookings (id)
                )'''
            ]
            for stmt in statements:
                try:
                    db.execute(stmt)
                    db.commit()
                except Exception as e:
                    db.rollback()
                    print(f"[INFO] Table setup notice: {e}")
        else:
            statements = [
                '''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT DEFAULT 'user'
                )''',
                '''CREATE TABLE IF NOT EXISTS rooms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    room_name TEXT NOT NULL,
                    price REAL NOT NULL,
                    capacity INTEGER NOT NULL,
                    description TEXT,
                    image_url TEXT,
                    availability INTEGER DEFAULT 1
                )''',
                '''CREATE TABLE IF NOT EXISTS room_images (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    room_id INTEGER NOT NULL,
                    image_url TEXT NOT NULL,
                    sort_order INTEGER DEFAULT 0,
                    FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE CASCADE
                )''',
                '''CREATE TABLE IF NOT EXISTS bookings (
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
                )''',
                '''CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    booking_id INTEGER NOT NULL,
                    rating INTEGER NOT NULL,
                    comment TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (booking_id) REFERENCES bookings (id)
                )'''
            ]
            for stmt in statements:
                db.execute(stmt)
            db.commit()

        # Automatically seed default admin and all 10 verified rooms
        _auto_seed(db)
    except Exception as err:
        print(f"[WARN] Error during create_tables: {err}")


def _auto_seed(db):
    """Seed admin user and all 10 verified rooms with their 40 gallery images."""
    try:
        # 1. Admin User
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

        # 2. Rooms & Gallery Images
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
                    # Look up room_id by room_name
                    r = db.execute('SELECT id FROM rooms WHERE room_name = ?', (item["room_name"],)).fetchone()
                    if r:
                        room_id = r[0] if isinstance(r, (tuple, list)) else r["id"]

                if room_id and "gallery" in item:
                    for sort_idx, g_img in enumerate(item["gallery"]):
                        db.execute(
                            'INSERT INTO room_images (room_id, image_url, sort_order) VALUES (?, ?, ?)',
                            (room_id, g_img, sort_idx)
                        )

        db.commit()
    except Exception as e:
        print(f"[INFO] Auto-seeding notice: {e}")
        try:
            db.rollback()
        except Exception:
            pass
