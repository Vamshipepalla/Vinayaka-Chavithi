"""Public-facing routes."""
import os
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from models import (Announcement, Event, CommitteeMember, Donor,
                    MediaGallery, Volunteer, SiteSettings, LiveUpdate)
from models import (Announcement, Event, CommitteeMember, Donor,
                    MediaGallery, Volunteer, SiteSettings, LiveUpdate,
                    DonationSettings)
from extensions import db
from utils import sanitize_input, validate_phone, validate_email

public_bp = Blueprint('public_bp', __name__)


@public_bp.route('/')
def index():
    # Active banner announcements
    banners = Announcement.query.filter_by(is_active=True, is_banner=True).order_by(
        Announcement.created_at.desc()).limit(5).all()
    # Regular announcements
    announcements = Announcement.query.filter_by(is_active=True).order_by(
        Announcement.created_at.desc()).limit(6).all()
    # Upcoming events (sorted by date)
    events = Event.query.filter_by(is_active=True).order_by(Event.event_date.asc()).limit(6).all()
    # Gallery highlights
    gallery = MediaGallery.query.filter_by(is_active=True, media_type='image').order_by(
        MediaGallery.display_order.asc(), MediaGallery.created_at.desc()).limit(8).all()
    # Live updates
    live_updates = LiveUpdate.query.filter_by(is_active=True).order_by(
        LiveUpdate.created_at.desc()).limit(5).all()
    # Settings
    settings = {
        'site_title': SiteSettings.get('site_title', 'Vinayaka Chavithi Celebrations'),
        'welcome_message': SiteSettings.get('welcome_message', 'Wishing You Joy & Prosperity'),
        'about_text': SiteSettings.get('about_text', ''),
        'contact_address': SiteSettings.get('contact_address', ''),
        'contact_phone': SiteSettings.get('contact_phone', ''),
        'contact_email': SiteSettings.get('contact_email', ''),
        'facebook_url': SiteSettings.get('facebook_url', ''),
        'youtube_url': SiteSettings.get('youtube_url', ''),
        'whatsapp_number': SiteSettings.get('whatsapp_number', ''),
        'festival_year': SiteSettings.get('festival_year', str(datetime.utcnow().year)),
    }
    festival_date = current_app.config.get('FESTIVAL_DATE', '2025-08-27 06:00:00')
    return render_template('public/index.html',
                           banners=banners,
                           announcements=announcements,
                           events=events,
                           gallery=gallery,
                           live_updates=live_updates,
                           settings=settings,
                           festival_date=festival_date)


@public_bp.route('/committee')
def committee():
    members = CommitteeMember.query.filter_by(is_active=True).order_by(
        CommitteeMember.display_order.asc(), CommitteeMember.name.asc()).all()
    settings = _base_settings()
    return render_template('public/committee.html', members=members, settings=settings)


@public_bp.route('/donors')
def donors():
    year = request.args.get('year', datetime.utcnow().year, type=int)
    category = request.args.get('category', '')
    query = Donor.query.filter_by(is_active=True, year=year)
    if category:
        query = query.filter_by(category=category)
    donors_list = query.order_by(Donor.display_order.asc(), Donor.name.asc()).all()

    # Group by category
    grouped = {}
    for d in donors_list:
        grouped.setdefault(d.category, []).append(d)

    years = db.session.query(Donor.year).distinct().order_by(Donor.year.desc()).all()
    years = [y[0] for y in years] or [datetime.utcnow().year]
    settings = _base_settings()
    return render_template('public/donors.html',
                           grouped=grouped, years=years,
                           current_year=year, settings=settings)


@public_bp.route('/gallery')
def gallery():
    album = request.args.get('album', '')
    year = request.args.get('year', '', type=str)
    query = MediaGallery.query.filter_by(is_active=True)
    if album:
        query = query.filter_by(album=album)
    if year:
        query = query.filter_by(year=int(year))
    media = query.order_by(MediaGallery.display_order.asc(), MediaGallery.created_at.desc()).all()
    albums = db.session.query(MediaGallery.album).distinct().all()
    albums = [a[0] for a in albums]
    years = db.session.query(MediaGallery.year).distinct().order_by(MediaGallery.year.desc()).all()
    years = [y[0] for y in years]
    settings = _base_settings()
    return render_template('public/gallery.html',
                           media=media, albums=albums, years=years,
                           current_album=album, current_year=year, settings=settings)


@public_bp.route('/events')
def events():
    events_list = Event.query.filter_by(is_active=True).order_by(Event.event_date.asc()).all()
    settings = _base_settings()
    return render_template('public/events.html', events=events_list, settings=settings)


@public_bp.route('/volunteer', methods=['GET', 'POST'])
def volunteer():
    settings = _base_settings()
    if request.method == 'POST':
        name = sanitize_input(request.form.get('name', ''))
        phone = sanitize_input(request.form.get('phone', ''))
        email = sanitize_input(request.form.get('email', ''))
        area = sanitize_input(request.form.get('area_of_interest', ''))
        availability = sanitize_input(request.form.get('availability', ''))
        message = sanitize_input(request.form.get('message', ''))

        errors = []
        if not name or len(name) < 2:
            errors.append('Please enter a valid name.')
        if not phone or not validate_phone(phone):
            errors.append('Please enter a valid 10-digit phone number.')
        if email and not validate_email(email):
            errors.append('Please enter a valid email address.')

        if errors:
            for e in errors:
                flash(e, 'danger')
        else:
            vol = Volunteer(name=name, phone=phone, email=email,
                            area_of_interest=area, availability=availability,
                            message=message)
            db.session.add(vol)
            db.session.commit()
            flash('Thank you for volunteering! We will contact you soon. 🙏', 'success')
            return redirect(url_for('public_bp.volunteer'))

    return render_template('public/volunteer.html', settings=settings)


@public_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    settings = _base_settings()
    if request.method == 'POST':
        flash('Thank you for your message! We will get back to you soon. 🙏', 'success')
        return redirect(url_for('public_bp.contact'))
    return render_template('public/contact.html', settings=settings)


# ─── API endpoints (for live updates / AJAX) ─────────────────────────────────

@public_bp.route('/api/live-updates')
def api_live_updates():
    updates = LiveUpdate.query.filter_by(is_active=True).order_by(
        LiveUpdate.created_at.desc()).limit(10).all()
    return jsonify([u.to_dict() for u in updates])


@public_bp.route('/api/announcements')
def api_announcements():
    items = Announcement.query.filter_by(is_active=True).order_by(
        Announcement.created_at.desc()).limit(10).all()
    return jsonify([a.to_dict() for a in items])

@public_bp.route('/donate')
def donate():
    settings = _base_settings()
    donation = DonationSettings.query.filter_by(is_active=True).first()
    return render_template('public/donate.html',
                           settings=settings,
                           donation=donation)

def _base_settings():
    return {
        'site_title': SiteSettings.get('site_title', 'Vinayaka Chavithi Celebrations'),
        'contact_phone': SiteSettings.get('contact_phone', ''),
        'contact_email': SiteSettings.get('contact_email', ''),
        'facebook_url': SiteSettings.get('facebook_url', ''),
        'youtube_url': SiteSettings.get('youtube_url', ''),
        'whatsapp_number': SiteSettings.get('whatsapp_number', ''),
        'instagram_url': SiteSettings.get('instagram_url', ''),
        'festival_year': SiteSettings.get('festival_year', str(datetime.utcnow().year)),
    }
