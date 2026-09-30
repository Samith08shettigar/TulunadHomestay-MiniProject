import os
import logging
from flask import Flask, render_template, redirect, url_for, session
from database import close_db
from models import create_tables
from blueprints.auth import auth_bp
from blueprints.admin import admin_bp
from blueprints.user import user_bp


def create_app():
    """Application factory for Tulunad Homestay."""
    app = Flask(__name__, instance_relative_config=True)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'tulunad-homestay-secret-key-2025')

    # Upload folder for room images
    upload_folder = os.path.join(app.static_folder, 'uploads', 'rooms')
    app.config['UPLOAD_FOLDER'] = upload_folder
    os.makedirs(upload_folder, exist_ok=True)

    # Ensure the instance folder exists (for homestay.db)
    os.makedirs(app.instance_path, exist_ok=True)

    # Register the teardown function to close DB connections
    app.teardown_appcontext(close_db)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)

    # Create database tables on startup (with graceful recovery)
    try:
        with app.app_context():
            create_tables()
    except Exception as err:
        logging.warning(f"Database initialization warning on startup: {err}")

    @app.route('/')
    def home():
        return render_template('index.html')

    @app.route('/login')
    def login():
        return redirect(url_for('auth.login'))

    @app.route('/feedback')
    @app.route('/feedbacks')
    def feedback_redirect():
        if session.get('role') == 'admin':
            return redirect(url_for('admin.feedback'))
        if session.get('user_id'):
            return redirect(url_for('user.my_bookings'))
        return redirect(url_for('auth.login'))

    # ── Error Handlers ───────────────────────────────────────
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('403.html'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        logging.exception("Unhandled server error: %s", e)
        return render_template('500.html'), 500

    return app


# Module-level app instance for WSGI servers (e.g. Gunicorn `app:app`)
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    if os.environ.get('RAILWAY_ENVIRONMENT') or (os.environ.get('DATABASE_URL') and not os.environ.get('FLASK_DEBUG')):
        import sys
        import subprocess
        # Initialize database tables and seed verified data
        try:
            from init_db import init_database
            init_database()
        except Exception as e:
            logging.error(f"Startup init_db notice: {e}")

        # Start Gunicorn WSGI server for production
        try:
            cmd = ['gunicorn', '--bind', f'0.0.0.0:{port}', '--workers', '2', 'app:app']
            logging.info("Starting production Gunicorn WSGI server: %s", " ".join(cmd))
            if os.name != 'nt':
                os.execvp('gunicorn', cmd)
            else:
                subprocess.run(cmd)
                sys.exit(0)
        except Exception as e:
            logging.warning("Gunicorn execution fallback: %s. Using Flask server.", e)
            app.run(host='0.0.0.0', port=port, debug=False)
    else:
        debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
        app.run(host='0.0.0.0', port=port, debug=debug_mode)
