import os
from flask import Flask, render_template, redirect, url_for
from database import close_db
from models import create_tables
from blueprints.auth import auth_bp
from blueprints.admin import admin_bp
from blueprints.user import user_bp


def create_app():
    """Application factory for Tulunad Homestay."""
    app = Flask(__name__, instance_relative_config=True)

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'tulunad-homestay-secret-key')

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

    # Create database tables on startup
    with app.app_context():
        create_tables()

    @app.route('/')
    def home():
        return render_template('index.html')

    @app.route('/login')
    def login():
        return redirect(url_for('auth.login'))

    # ── Error Handlers ───────────────────────────────────────
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('403.html'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
