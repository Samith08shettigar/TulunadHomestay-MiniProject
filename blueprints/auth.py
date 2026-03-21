from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        db = get_db()

        # Check if email already exists
        existing = db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
        if existing:
            flash('Email already exists. Please log in.', 'danger')
            return redirect(url_for('auth.register'))

        # Insert new user
        db.execute(
            'INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)',
            (name, email, generate_password_hash(password), 'user')
        )
        db.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        db = get_db()
        user = db.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()

        if not user:
            flash('Email not found. Please register first.', 'danger')
            return redirect(url_for('auth.login'))

        if not check_password_hash(user['password'], password):
            flash('Wrong password. Please try again.', 'danger')
            return redirect(url_for('auth.login'))

        # Store user info in session
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        session['role'] = user['role']

        flash(f'Welcome back, {user["name"]}!', 'success')

        # Redirect based on role
        if user['role'] == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('user.dashboard'))

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
