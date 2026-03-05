"""Database models for Vinayaka Chavithi app."""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db, login_manager


# ─── Auth ─────────────────────────────────────────────────────────────────────

class Admin(UserMixin, db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Admin {self.username}>'


@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))


# ─── Content Models ───────────────────────────────────────────────────────────

class Announcement(db.Model):
    __tablename__ = 'announcements'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), default='normal')
    is_active = db.Column(db.Boolean, default=True)
    is_banner = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'priority': self.priority,
            'is_banner': self.is_banner,
            'created_at': self.created_at.strftime('%d %b %Y')
        }


class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    event_date = db.Column(db.DateTime, nullable=False)
    event_time = db.Column(db.String(50))
    location = db.Column(db.String(200))
    category = db.Column(db.String(50), default='general')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'event_date': self.event_date.strftime('%d %b %Y'),
            'event_time': self.event_time or '',
            'location': self.location or '',
            'category': self.category,
        }


class CommitteeMember(db.Model):
    __tablename__ = 'committee_members'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    photo = db.Column(db.String(300))
    display_order = db.Column(db.Integer, default=99)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Donor(db.Model):
    __tablename__ = 'donors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    donation_type = db.Column(db.String(100), nullable=False)
    donation_details = db.Column(db.Text)
    category = db.Column(db.String(50), default='general')
    year = db.Column(db.Integer, default=datetime.utcnow().year)
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=99)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class MediaGallery(db.Model):
    __tablename__ = 'media_gallery'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    media_type = db.Column(db.String(10), default='image')
    file_path = db.Column(db.String(300), nullable=False)
    thumbnail = db.Column(db.String(300))
    album = db.Column(db.String(100), default='General')
    year = db.Column(db.Integer, default=datetime.utcnow().year)
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=99)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Volunteer(db.Model):
    __tablename__ = 'volunteers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120))
    area_of_interest = db.Column(db.String(200))
    availability = db.Column(db.String(100))
    message = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SiteSettings(db.Model):
    __tablename__ = 'site_settings'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def get(cls, key, default=''):
        obj = cls.query.filter_by(key=key).first()
        return obj.value if obj else default

    @classmethod
    def set(cls, key, value):
        obj = cls.query.filter_by(key=key).first()
        if obj:
            obj.value = value
        else:
            obj = cls(key=key, value=value)
            db.session.add(obj)
        db.session.commit()


class LiveUpdate(db.Model):
    __tablename__ = 'live_updates'
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    update_type = db.Column(db.String(30), default='info')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'message': self.message,
            'update_type': self.update_type,
            'created_at': self.created_at.strftime('%d %b %Y, %I:%M %p')
        }


class DonationSettings(db.Model):
    __tablename__ = 'donation_settings'
    id = db.Column(db.Integer, primary_key=True)
    upi_id = db.Column(db.String(100))
    upi_name = db.Column(db.String(150))
    qr_code_image = db.Column(db.String(300))
    bank_account_name = db.Column(db.String(150))
    bank_account_number = db.Column(db.String(50))
    bank_ifsc = db.Column(db.String(20))
    bank_name = db.Column(db.String(100))
    bank_branch = db.Column(db.String(100))
    whatsapp_number = db.Column(db.String(20))
    donation_note = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)