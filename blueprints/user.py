from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from helpers import login_required
from database import get_db
from datetime import date

user_bp = Blueprint('user', __name__, url_prefix='')


@user_bp.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    user_id = session['user_id']

    total = db.execute(
        'SELECT COUNT(*) FROM bookings WHERE user_id = ?', (user_id,)
    ).fetchone()[0]

    confirmed = db.execute(
        'SELECT COUNT(*) FROM bookings WHERE user_id = ? AND status = ?',
        (user_id, 'Confirmed')
    ).fetchone()[0]

    return render_template(
        'user/dashboard.html',
        total_bookings=total,
        confirmed_bookings=confirmed
    )


@user_bp.route('/rooms')
@login_required
def rooms():
    db = get_db()
    rooms = db.execute(
        'SELECT * FROM rooms WHERE availability = 1'
    ).fetchall()
    return render_template('user/rooms.html', rooms=rooms)


@user_bp.route('/book/<int:room_id>', methods=['GET', 'POST'])
@login_required
def book_room(room_id):
    db = get_db()
    room = db.execute('SELECT * FROM rooms WHERE id = ?', (room_id,)).fetchone()

    if not room:
        flash('Room not found.', 'danger')
        return redirect(url_for('user.rooms'))

    if request.method == 'POST':
        checkin_date = request.form['checkin_date']
        checkout_date = request.form['checkout_date']
        meal_type = request.form.get('meal_type', 'Veg')
        fire_camp = request.form.get('fire_camp', 'No')

        # Validate dates
        if checkin_date >= checkout_date:
            flash('Check-out date must be after check-in date.', 'danger')
            return redirect(url_for('user.book_room', room_id=room_id))

        if checkin_date < date.today().isoformat():
            flash('Check-in date cannot be in the past.', 'danger')
            return redirect(url_for('user.book_room', room_id=room_id))

        # Double-booking overlap check
        # A conflict exists if there is any booking where:
        #   NOT (existing_checkout <= new_checkin OR existing_checkin >= new_checkout)
        conflict = db.execute(
            '''SELECT id FROM bookings
               WHERE room_id = ? AND status != 'Cancelled'
               AND NOT (checkout_date <= ? OR checkin_date >= ?)''',
            (room_id, checkin_date, checkout_date)
        ).fetchone()

        if conflict:
            flash('Room not available for selected dates. Please choose different dates.', 'danger')
            return redirect(url_for('user.book_room', room_id=room_id))

        # Insert booking
        db.execute(
            '''INSERT INTO bookings (user_id, room_id, checkin_date, checkout_date, meal_type, fire_camp, status)
               VALUES (?, ?, ?, ?, ?, ?, 'Pending')''',
            (session['user_id'], room_id, checkin_date, checkout_date, meal_type, fire_camp)
        )
        db.commit()

        flash('Booking submitted successfully! Awaiting confirmation.', 'success')
        return redirect(url_for('user.my_bookings'))

    today = date.today().isoformat()
    return render_template('user/book_room.html', room=room, today=today)


@user_bp.route('/my-bookings')
@login_required
def my_bookings():
    db = get_db()
    bookings = db.execute(
        '''SELECT b.*, r.room_name, r.price, r.image_url,
                  CASE WHEN f.id IS NOT NULL THEN 1 ELSE 0 END AS has_feedback
           FROM bookings b
           JOIN rooms r ON b.room_id = r.id
           LEFT JOIN feedback f ON f.booking_id = b.id
           WHERE b.user_id = ?
           ORDER BY b.created_at DESC''',
        (session['user_id'],)
    ).fetchall()
    return render_template('user/my_bookings.html', bookings=bookings)


@user_bp.route('/feedback/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def feedback(booking_id):
    db = get_db()

    # Fetch booking with room info — must belong to current user
    booking = db.execute(
        '''SELECT b.*, r.room_name, r.image_url
           FROM bookings b
           JOIN rooms r ON b.room_id = r.id
           WHERE b.id = ? AND b.user_id = ?''',
        (booking_id, session['user_id'])
    ).fetchone()

    if not booking:
        flash('Booking not found.', 'danger')
        return redirect(url_for('user.my_bookings'))

    if booking['status'] != 'Confirmed':
        flash('You can only leave feedback for confirmed bookings.', 'warning')
        return redirect(url_for('user.my_bookings'))

    # Check for existing feedback
    existing = db.execute(
        'SELECT id FROM feedback WHERE booking_id = ?', (booking_id,)
    ).fetchone()

    if existing:
        flash('You have already submitted feedback for this booking.', 'info')
        return redirect(url_for('user.my_bookings'))

    if request.method == 'POST':
        rating = request.form.get('rating', type=int)
        comment = request.form.get('comment', '').strip()

        if not rating or rating < 1 or rating > 5:
            flash('Please select a rating between 1 and 5.', 'danger')
            return redirect(url_for('user.feedback', booking_id=booking_id))

        if len(comment) < 10:
            flash('Comment must be at least 10 characters.', 'danger')
            return redirect(url_for('user.feedback', booking_id=booking_id))

        db.execute(
            'INSERT INTO feedback (user_id, booking_id, rating, comment) VALUES (?, ?, ?, ?)',
            (session['user_id'], booking_id, rating, comment)
        )
        db.commit()

        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('user.my_bookings'))

    return render_template('user/feedback.html', booking=booking)
