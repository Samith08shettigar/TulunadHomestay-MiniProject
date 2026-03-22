import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from helpers import admin_required
from database import get_db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def _allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _save_upload(file_obj):
    """Save an uploaded file and return its URL path, or None on failure."""
    if file_obj and file_obj.filename and _allowed_file(file_obj.filename):
        ext = file_obj.filename.rsplit('.', 1)[1].lower()
        unique_name = f"{uuid.uuid4().hex}.{ext}"
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
        file_obj.save(save_path)
        return f"/static/uploads/rooms/{unique_name}"
    return None


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
        availability = 1 if request.form.get('availability') else 0

        # Cover image: prefer uploaded file, fall back to URL
        cover_url = _save_upload(request.files.get('cover_image'))
        if not cover_url:
            cover_url = request.form.get('image_url', '').strip()

        db = get_db()
        cursor = db.execute(
            '''INSERT INTO rooms (room_name, price, capacity, description, image_url, availability)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (room_name, float(price), int(capacity), description, cover_url, availability),
        )
        new_room_id = cursor.lastrowid

        # Gallery images: uploaded files
        gallery_files = request.files.getlist('gallery_files')
        sort_idx = 0
        for f in gallery_files:
            saved = _save_upload(f)
            if saved:
                db.execute(
                    'INSERT INTO room_images (room_id, image_url, sort_order) VALUES (?, ?, ?)',
                    (new_room_id, saved, sort_idx),
                )
                sort_idx += 1

        # Gallery images: URL inputs
        extra_images = request.form.getlist('extra_images')
        for img_url in extra_images:
            img_url = img_url.strip()
            if img_url:
                db.execute(
                    'INSERT INTO room_images (room_id, image_url, sort_order) VALUES (?, ?, ?)',
                    (new_room_id, img_url, sort_idx),
                )
                sort_idx += 1

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
        availability = 1 if request.form.get('availability') else 0

        # Cover image: prefer new upload, then URL input, then keep existing
        cover_url = _save_upload(request.files.get('cover_image'))
        if not cover_url:
            cover_url = request.form.get('image_url', '').strip()
        if not cover_url:
            cover_url = room['image_url'] or ''

        db.execute(
            '''UPDATE rooms
               SET room_name = ?, price = ?, capacity = ?, description = ?, image_url = ?, availability = ?
               WHERE id = ?''',
            (room_name, float(price), int(capacity), description, cover_url, availability, room_id),
        )

        # Replace gallery images: delete old, insert new
        db.execute('DELETE FROM room_images WHERE room_id = ?', (room_id,))

        sort_idx = 0

        # Keep existing images the user didn't remove
        keep_images = request.form.getlist('keep_images')
        for img_url in keep_images:
            img_url = img_url.strip()
            if img_url:
                db.execute(
                    'INSERT INTO room_images (room_id, image_url, sort_order) VALUES (?, ?, ?)',
                    (room_id, img_url, sort_idx),
                )
                sort_idx += 1

        # New uploaded files
        gallery_files = request.files.getlist('gallery_files')
        for f in gallery_files:
            saved = _save_upload(f)
            if saved:
                db.execute(
                    'INSERT INTO room_images (room_id, image_url, sort_order) VALUES (?, ?, ?)',
                    (room_id, saved, sort_idx),
                )
                sort_idx += 1

        # New URL inputs
        extra_images = request.form.getlist('extra_images')
        for img_url in extra_images:
            img_url = img_url.strip()
            if img_url:
                db.execute(
                    'INSERT INTO room_images (room_id, image_url, sort_order) VALUES (?, ?, ?)',
                    (room_id, img_url, sort_idx),
                )
                sort_idx += 1

        db.commit()

        flash('Room updated successfully!', 'success')
        return redirect(url_for('admin.rooms'))

    # Fetch existing gallery images for this room
    images = db.execute(
        'SELECT * FROM room_images WHERE room_id = ? ORDER BY sort_order', (room_id,)
    ).fetchall()

    return render_template('admin/edit_room.html', room=room, images=images)


# ── Rooms — Delete ───────────────────────────────────────────
@admin_bp.route('/rooms/delete/<int:room_id>', methods=['POST'])
@admin_required
def delete_room(room_id):
    db = get_db()

    # Delete in dependency order: feedback → bookings → room_images → room
    # (bookings and feedback FKs lack ON DELETE CASCADE)
    db.execute('''
        DELETE FROM feedback WHERE booking_id IN (
            SELECT id FROM bookings WHERE room_id = ?
        )
    ''', (room_id,))
    db.execute('DELETE FROM bookings WHERE room_id = ?', (room_id,))
    db.execute('DELETE FROM room_images WHERE room_id = ?', (room_id,))
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

