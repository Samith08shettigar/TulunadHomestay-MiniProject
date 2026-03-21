from flask import Blueprint, render_template, request, redirect, url_for, flash
from helpers import admin_required
from database import get_db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# ── Dashboard ────────────────────────────────────────────────
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    db = get_db()

    total_rooms = db.execute('SELECT COUNT(*) FROM rooms').fetchone()[0]
    total_bookings = db.execute('SELECT COUNT(*) FROM bookings').fetchone()[0]
    pending_count = db.execute(
        "SELECT COUNT(*) FROM bookings WHERE status = 'Pending'"
    ).fetchone()[0]
    confirmed_count = db.execute(
        "SELECT COUNT(*) FROM bookings WHERE status = 'Confirmed'"
    ).fetchone()[0]

    return render_template(
        'admin/dashboard.html',
        total_rooms=total_rooms,
        total_bookings=total_bookings,
        pending_count=pending_count,
        confirmed_count=confirmed_count,
    )


# ── Rooms — List ─────────────────────────────────────────────
@admin_bp.route('/rooms')
@admin_required
def rooms():
    db = get_db()
    rooms = db.execute('SELECT * FROM rooms ORDER BY id DESC').fetchall()
    return render_template('admin/rooms.html', rooms=rooms)


# ── Rooms — Add ──────────────────────────────────────────────
@admin_bp.route('/rooms/add', methods=['GET', 'POST'])
@admin_required
def add_room():
    if request.method == 'POST':
        room_name = request.form['room_name']
        price = request.form['price']
        capacity = request.form['capacity']
        description = request.form.get('description', '')
        image_url = request.form.get('image_url', '')
        availability = 1 if request.form.get('availability') else 0

        db = get_db()
        db.execute(
            '''INSERT INTO rooms (room_name, price, capacity, description, image_url, availability)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (room_name, float(price), int(capacity), description, image_url, availability),
        )
        db.commit()

        flash('Room added successfully!', 'success')
        return redirect(url_for('admin.rooms'))

    return render_template('admin/add_room.html')


# ── Rooms — Edit ─────────────────────────────────────────────
@admin_bp.route('/rooms/edit/<int:room_id>', methods=['GET', 'POST'])
@admin_required
def edit_room(room_id):
    db = get_db()
    room = db.execute('SELECT * FROM rooms WHERE id = ?', (room_id,)).fetchone()

    if not room:
        flash('Room not found.', 'danger')
        return redirect(url_for('admin.rooms'))

    if request.method == 'POST':
        room_name = request.form['room_name']
        price = request.form['price']
        capacity = request.form['capacity']
        description = request.form.get('description', '')
        image_url = request.form.get('image_url', '')
        availability = 1 if request.form.get('availability') else 0

        db.execute(
            '''UPDATE rooms
               SET room_name = ?, price = ?, capacity = ?, description = ?, image_url = ?, availability = ?
               WHERE id = ?''',
            (room_name, float(price), int(capacity), description, image_url, availability, room_id),
        )
        db.commit()

        flash('Room updated successfully!', 'success')
        return redirect(url_for('admin.rooms'))

    return render_template('admin/edit_room.html', room=room)


# ── Rooms — Delete ───────────────────────────────────────────
@admin_bp.route('/rooms/delete/<int:room_id>', methods=['POST'])
@admin_required
def delete_room(room_id):
    db = get_db()
    db.execute('DELETE FROM rooms WHERE id = ?', (room_id,))
    db.commit()
    flash('Room deleted.', 'info')
    return redirect(url_for('admin.rooms'))


# ── Bookings — List ──────────────────────────────────────────
@admin_bp.route('/bookings')
@admin_required
def bookings():
    db = get_db()
    bookings = db.execute(
        '''SELECT b.*, u.name AS user_name, r.room_name
           FROM bookings b
           JOIN users u ON b.user_id = u.id
           JOIN rooms r ON b.room_id = r.id
           ORDER BY b.created_at DESC'''
    ).fetchall()
    return render_template('admin/bookings.html', bookings=bookings)


# ── Bookings — Update Status ─────────────────────────────────
@admin_bp.route('/bookings/update/<int:booking_id>', methods=['POST'])
@admin_required
def update_booking(booking_id):
    new_status = request.form['status']

    if new_status not in ('Confirmed', 'Cancelled'):
        flash('Invalid status.', 'danger')
        return redirect(url_for('admin.bookings'))

    db = get_db()
    db.execute(
        'UPDATE bookings SET status = ? WHERE id = ?',
        (new_status, booking_id),
    )
    db.commit()

    flash(f'Booking #{booking_id} marked as {new_status}.', 'success')
    return redirect(url_for('admin.bookings'))


# ── Feedback — List ──────────────────────────────────────────
@admin_bp.route('/feedback')
@admin_required
def feedback():
    db = get_db()
    feedbacks = db.execute(
        '''SELECT f.*, u.name AS user_name, r.room_name,
                  b.checkin_date, b.checkout_date
           FROM feedback f
           JOIN users u ON f.user_id = u.id
           JOIN bookings b ON f.booking_id = b.id
           JOIN rooms r ON b.room_id = r.id
           ORDER BY f.created_at DESC'''
    ).fetchall()

    # Compute average rating
    avg_row = db.execute('SELECT AVG(rating) AS avg_rating, COUNT(*) AS total FROM feedback').fetchone()
    avg_rating = round(avg_row['avg_rating'], 1) if avg_row['avg_rating'] else 0
    total_reviews = avg_row['total']

    return render_template(
        'admin/feedback.html',
        feedbacks=feedbacks,
        avg_rating=avg_rating,
        total_reviews=total_reviews,
    )

