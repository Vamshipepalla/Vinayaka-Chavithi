"""
Vinayaka Chavithi Festival Web Application
Main application entry point
"""

import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

from flask import Flask
from extensions import db, login_manager, migrate
from config import get_config


def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = 'admin_bp.login'
    login_manager.login_message = 'Please log in to access the admin panel.'
    login_manager.login_message_category = 'warning'

    # Register blueprints
    from routes.public import public_bp
    from routes.admin import admin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Create upload directory
    upload_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    os.makedirs(upload_path, exist_ok=True)

    # Create tables and seed admin
    with app.app_context():
        db.create_all()
        seed_admin()

    return app


def seed_admin():
    """Create default admin if none exists."""
    from models import Admin
    if Admin.query.count() == 0:
        admin = Admin(
            username=os.getenv('ADMIN_USERNAME', 'admin'),
            email=os.getenv('ADMIN_EMAIL', 'admin@example.com')
        )
        admin.set_password(os.getenv('ADMIN_PASSWORD', 'Admin@12345'))
        db.session.add(admin)
        db.session.commit()
        print(f"[INFO] Default admin created: {admin.username}")


app = create_app()

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('FLASK_DEBUG', '0') == '1'
    )
