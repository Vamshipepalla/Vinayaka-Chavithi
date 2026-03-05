"""Admin panel routes — all protected by @login_required."""
import os
from datetime import datetime
from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, jsonify, current_app)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename

from models import (Admin, Announcement, Event, CommitteeMember, Donor,
                    MediaGallery, Volunteer, SiteSettings, LiveUpdate)
from models import (Admin, Announcement, Event, CommitteeMember, Donor,
                    MediaGallery, Volunteer, SiteSettings, LiveUpdate,
                    DonationSettings)
from extensions import db
from utils import (sanitize_input, allowed_image, allowed_video,
                   save_upload, validate_email, validate_phone, resize_image)

admin_bp = Blueprint('admin_bp', __name__)

# ─── Auth ─────────────────────────────────────────────────────────────────────

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_bp.dashboard'))
    if request.method == 'POST':
        username = sanitize_input(request.form.get('username', ''))
        password = request.form.get('password', '')
        admin = Admin.query.filter_by(username=username, is_active=True).first()
        if admin and admin.check_password(password):
            admin.last_login = datetime.utcnow()
            db.session.commit()
            login_user(admin, remember=False)
            return redirect(url_for('admin_bp.dashboard'))
        flash('Invalid username or password.', 'danger')
    return render_template('admin/login.html')


@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('admin_bp.login'))


# ─── Dashboard ────────────────────────────────────────────────────────────────

@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    stats = {
        'announcements': Announcement.query.filter_by(is_active=True).count(),
        'events': Event.query.filter_by(is_active=True).count(),
        'committee': CommitteeMember.query.filter_by(is_active=True).count(),
        'donors': Donor.query.filter_by(is_active=True).count(),
        'gallery': MediaGallery.query.filter_by(is_active=True).count(),
        'volunteers': Volunteer.query.filter_by(status='pending').count(),
        'live_updates': LiveUpdate.query.filter_by(is_active=True).count(),
    }
    recent_announcements = Announcement.query.order_by(
        Announcement.created_at.desc()).limit(5).all()
    recent_volunteers = Volunteer.query.filter_by(status='pending').order_by(
        Volunteer.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html',
                           stats=stats,
                           recent_announcements=recent_announcements,
                           recent_volunteers=recent_volunteers)


# ─── Announcements ────────────────────────────────────────────────────────────

@admin_bp.route('/announcements')
@login_required
def announcements():
    items = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return render_template('admin/announcements.html', items=items)


@admin_bp.route('/announcements/add', methods=['GET', 'POST'])
@login_required
def add_announcement():
    if request.method == 'POST':
        title = sanitize_input(request.form.get('title', ''))
        content = sanitize_input(request.form.get('content', ''))
        priority = request.form.get('priority', 'normal')
        is_banner = bool(request.form.get('is_banner'))
        if not title or not content:
            flash('Title and content are required.', 'danger')
        else:
            a = Announcement(title=title, content=content,
                             priority=priority, is_banner=is_banner)
            db.session.add(a)
            db.session.commit()
            flash('Announcement added!', 'success')
            return redirect(url_for('admin_bp.announcements'))
    return render_template('admin/announcement_form.html', item=None)


@admin_bp.route('/announcements/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_announcement(id):
    item = Announcement.query.get_or_404(id)
    if request.method == 'POST':
        item.title = sanitize_input(request.form.get('title', ''))
        item.content = sanitize_input(request.form.get('content', ''))
        item.priority = request.form.get('priority', 'normal')
        item.is_banner = bool(request.form.get('is_banner'))
        item.is_active = bool(request.form.get('is_active', True))
        db.session.commit()
        flash('Announcement updated!', 'success')
        return redirect(url_for('admin_bp.announcements'))
    return render_template('admin/announcement_form.html', item=item)


@admin_bp.route('/announcements/delete/<int:id>', methods=['POST'])
@login_required
def delete_announcement(id):
    item = Announcement.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Announcement deleted.', 'info')
    return redirect(url_for('admin_bp.announcements'))


# ─── Live Updates ─────────────────────────────────────────────────────────────

@admin_bp.route('/live-updates')
@login_required
def live_updates():
    items = LiveUpdate.query.order_by(LiveUpdate.created_at.desc()).all()
    return render_template('admin/live_updates.html', items=items)


@admin_bp.route('/live-updates/add', methods=['POST'])
@login_required
def add_live_update():
    msg = sanitize_input(request.form.get('message', ''))
    utype = request.form.get('update_type', 'info')
    if msg:
        u = LiveUpdate(message=msg, update_type=utype)
        db.session.add(u)
        db.session.commit()
        flash('Live update posted!', 'success')
    return redirect(url_for('admin_bp.live_updates'))


@admin_bp.route('/live-updates/delete/<int:id>', methods=['POST'])
@login_required
def delete_live_update(id):
    item = LiveUpdate.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Live update removed.', 'info')
    return redirect(url_for('admin_bp.live_updates'))


# ─── Events ───────────────────────────────────────────────────────────────────

@admin_bp.route('/events')
@login_required
def events():
    items = Event.query.order_by(Event.event_date.asc()).all()
    return render_template('admin/events.html', items=items)


@admin_bp.route('/events/add', methods=['GET', 'POST'])
@login_required
def add_event():
    if request.method == 'POST':
        title = sanitize_input(request.form.get('title', ''))
        desc = sanitize_input(request.form.get('description', ''))
        date_str = request.form.get('event_date', '')
        time_str = sanitize_input(request.form.get('event_time', ''))
        location = sanitize_input(request.form.get('location', ''))
        category = request.form.get('category', 'general')
        try:
            event_dt = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format.', 'danger')
            return render_template('admin/event_form.html', item=None)
        e = Event(title=title, description=desc, event_date=event_dt,
                  event_time=time_str, location=location, category=category)
        db.session.add(e)
        db.session.commit()
        flash('Event added!', 'success')
        return redirect(url_for('admin_bp.events'))
    return render_template('admin/event_form.html', item=None)


@admin_bp.route('/events/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_event(id):
    item = Event.query.get_or_404(id)
    if request.method == 'POST':
        item.title = sanitize_input(request.form.get('title', ''))
        item.description = sanitize_input(request.form.get('description', ''))
        date_str = request.form.get('event_date', '')
        try:
            item.event_date = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format.', 'danger')
            return render_template('admin/event_form.html', item=item)
        item.event_time = sanitize_input(request.form.get('event_time', ''))
        item.location = sanitize_input(request.form.get('location', ''))
        item.category = request.form.get('category', 'general')
        item.is_active = bool(request.form.get('is_active', True))
        db.session.commit()
        flash('Event updated!', 'success')
        return redirect(url_for('admin_bp.events'))
    return render_template('admin/event_form.html', item=item)


@admin_bp.route('/events/delete/<int:id>', methods=['POST'])
@login_required
def delete_event(id):
    item = Event.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Event deleted.', 'info')
    return redirect(url_for('admin_bp.events'))


# ─── Committee Members ────────────────────────────────────────────────────────

@admin_bp.route('/committee')
@login_required
def committee():
    members = CommitteeMember.query.order_by(
        CommitteeMember.display_order.asc(), CommitteeMember.name.asc()).all()
    return render_template('admin/committee.html', members=members)


@admin_bp.route('/committee/add', methods=['GET', 'POST'])
@login_required
def add_committee():
    if request.method == 'POST':
        name = sanitize_input(request.form.get('name', ''))
        role = sanitize_input(request.form.get('role', ''))
        phone = sanitize_input(request.form.get('phone', ''))
        email = sanitize_input(request.form.get('email', ''))
        order = request.form.get('display_order', 99, type=int)
        photo_path = None
        if 'photo' in request.files:
            f = request.files['photo']
            if f and f.filename and allowed_image(f.filename):
                photo_path = save_upload(f, current_app.config['UPLOAD_FOLDER'], 'committee')
                if photo_path:
                    resize_image(os.path.join(current_app.root_path, photo_path), 300, 300)
        if not name or not role:
            flash('Name and role are required.', 'danger')
        else:
            m = CommitteeMember(name=name, role=role, phone=phone,
                                email=email, photo=photo_path, display_order=order)
            db.session.add(m)
            db.session.commit()
            flash('Committee member added!', 'success')
            return redirect(url_for('admin_bp.committee'))
    return render_template('admin/committee_form.html', item=None)


@admin_bp.route('/committee/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_committee(id):
    item = CommitteeMember.query.get_or_404(id)
    if request.method == 'POST':
        item.name = sanitize_input(request.form.get('name', ''))
        item.role = sanitize_input(request.form.get('role', ''))
        item.phone = sanitize_input(request.form.get('phone', ''))
        item.email = sanitize_input(request.form.get('email', ''))
        item.display_order = request.form.get('display_order', 99, type=int)
        item.is_active = bool(request.form.get('is_active'))
        if 'photo' in request.files:
            f = request.files['photo']
            if f and f.filename and allowed_image(f.filename):
                photo_path = save_upload(f, current_app.config['UPLOAD_FOLDER'], 'committee')
                if photo_path:
                    resize_image(os.path.join(current_app.root_path, photo_path), 300, 300)
                    item.photo = photo_path
        db.session.commit()
        flash('Member updated!', 'success')
        return redirect(url_for('admin_bp.committee'))
    return render_template('admin/committee_form.html', item=item)


@admin_bp.route('/committee/delete/<int:id>', methods=['POST'])
@login_required
def delete_committee(id):
    item = CommitteeMember.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Member removed.', 'info')
    return redirect(url_for('admin_bp.committee'))


# ─── Donors ───────────────────────────────────────────────────────────────────

@admin_bp.route('/donors')
@login_required
def donors():
    items = Donor.query.order_by(Donor.year.desc(), Donor.display_order.asc()).all()
    return render_template('admin/donors.html', items=items)


@admin_bp.route('/donors/add', methods=['GET', 'POST'])
@login_required
def add_donor():
    if request.method == 'POST':
        name = sanitize_input(request.form.get('name', ''))
        dtype = sanitize_input(request.form.get('donation_type', ''))
        details = sanitize_input(request.form.get('donation_details', ''))
        category = request.form.get('category', 'general')
        year = request.form.get('year', datetime.utcnow().year, type=int)
        order = request.form.get('display_order', 99, type=int)
        if not name or not dtype:
            flash('Name and donation type are required.', 'danger')
        else:
            d = Donor(name=name, donation_type=dtype, donation_details=details,
                      category=category, year=year, display_order=order)
            db.session.add(d)
            db.session.commit()
            flash('Donor added!', 'success')
            return redirect(url_for('admin_bp.donors'))
    return render_template('admin/donor_form.html', item=None)


@admin_bp.route('/donors/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_donor(id):
    item = Donor.query.get_or_404(id)
    if request.method == 'POST':
        item.name = sanitize_input(request.form.get('name', ''))
        item.donation_type = sanitize_input(request.form.get('donation_type', ''))
        item.donation_details = sanitize_input(request.form.get('donation_details', ''))
        item.category = request.form.get('category', 'general')
        item.year = request.form.get('year', datetime.utcnow().year, type=int)
        item.display_order = request.form.get('display_order', 99, type=int)
        item.is_active = bool(request.form.get('is_active'))
        db.session.commit()
        flash('Donor updated!', 'success')
        return redirect(url_for('admin_bp.donors'))
    return render_template('admin/donor_form.html', item=item)


@admin_bp.route('/donors/delete/<int:id>', methods=['POST'])
@login_required
def delete_donor(id):
    item = Donor.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Donor removed.', 'info')
    return redirect(url_for('admin_bp.donors'))


# ─── Gallery ──────────────────────────────────────────────────────────────────

@admin_bp.route('/gallery')
@login_required
def gallery():
    items = MediaGallery.query.order_by(MediaGallery.created_at.desc()).all()
    return render_template('admin/gallery.html', items=items)


@admin_bp.route('/gallery/upload', methods=['GET', 'POST'])
@login_required
def upload_media():
    if request.method == 'POST':
        title = sanitize_input(request.form.get('title', ''))
        desc = sanitize_input(request.form.get('description', ''))
        album = sanitize_input(request.form.get('album', 'General'))
        year = request.form.get('year', datetime.utcnow().year, type=int)
        order = request.form.get('display_order', 99, type=int)
        uploaded = 0
        files = request.files.getlist('files')
        for f in files:
            if not f or not f.filename:
                continue
            if allowed_image(f.filename):
                path = save_upload(f, current_app.config['UPLOAD_FOLDER'], 'gallery')
                if path:
                    m = MediaGallery(title=title or f.filename, description=desc,
                                     media_type='image', file_path=path, album=album,
                                     year=year, display_order=order)
                    db.session.add(m)
                    uploaded += 1
            elif allowed_video(f.filename):
                path = save_upload(f, current_app.config['UPLOAD_FOLDER'], 'gallery')
                if path:
                    m = MediaGallery(title=title or f.filename, description=desc,
                                     media_type='video', file_path=path, album=album,
                                     year=year, display_order=order)
                    db.session.add(m)
                    uploaded += 1
        if uploaded:
            db.session.commit()
            flash(f'{uploaded} file(s) uploaded successfully!', 'success')
        else:
            flash('No valid files uploaded.', 'warning')
        return redirect(url_for('admin_bp.gallery'))
    return render_template('admin/gallery_upload.html')


@admin_bp.route('/gallery/delete/<int:id>', methods=['POST'])
@login_required
def delete_media(id):
    item = MediaGallery.query.get_or_404(id)
    # Remove file from disk
    full_path = os.path.join(current_app.root_path, item.file_path)
    if os.path.exists(full_path):
        os.remove(full_path)
    db.session.delete(item)
    db.session.commit()
    flash('Media deleted.', 'info')
    return redirect(url_for('admin_bp.gallery'))


# ─── Volunteers ───────────────────────────────────────────────────────────────

@admin_bp.route('/volunteers')
@login_required
def volunteers():
    status_filter = request.args.get('status', '')
    query = Volunteer.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    items = query.order_by(Volunteer.created_at.desc()).all()
    return render_template('admin/volunteers.html', items=items, status_filter=status_filter)


@admin_bp.route('/volunteers/update-status/<int:id>', methods=['POST'])
@login_required
def update_volunteer_status(id):
    item = Volunteer.query.get_or_404(id)
    item.status = request.form.get('status', 'pending')
    db.session.commit()
    flash('Volunteer status updated.', 'success')
    return redirect(url_for('admin_bp.volunteers'))


@admin_bp.route('/volunteers/delete/<int:id>', methods=['POST'])
@login_required
def delete_volunteer(id):
    item = Volunteer.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Volunteer removed.', 'info')
    return redirect(url_for('admin_bp.volunteers'))


# ─── Settings ─────────────────────────────────────────────────────────────────

@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        keys = ['site_title', 'welcome_message', 'about_text', 'contact_address',
        'contact_phone', 'contact_email', 'facebook_url', 'youtube_url',
        'whatsapp_number', 'instagram_url', 'festival_year']
        for key in keys:
            val = sanitize_input(request.form.get(key, ''))
            SiteSettings.set(key, val)
        flash('Settings saved!', 'success')
        return redirect(url_for('admin_bp.settings'))
    current = {k: SiteSettings.get(k) for k in
               ['site_title', 'welcome_message', 'about_text', 'contact_address',
                'contact_phone', 'contact_email', 'facebook_url', 'youtube_url',
                'whatsapp_number', 'festival_year']}
    return render_template('admin/settings.html', current=current)


# ─── Change Password ──────────────────────────────────────────────────────────

@admin_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old = request.form.get('old_password', '')
        new = request.form.get('new_password', '')
        confirm = request.form.get('confirm_password', '')
        if not current_user.check_password(old):
            flash('Current password is incorrect.', 'danger')
        elif len(new) < 8:
            flash('New password must be at least 8 characters.', 'danger')
        elif new != confirm:
            flash('Passwords do not match.', 'danger')
        else:
            current_user.set_password(new)
            db.session.commit()
            flash('Password changed successfully!', 'success')
            return redirect(url_for('admin_bp.dashboard'))
    return render_template('admin/change_password.html')
@admin_bp.route('/donation-settings', methods=['GET', 'POST'])
@login_required
def donation_settings():
    donation = DonationSettings.query.first()
    if not donation:
        donation = DonationSettings()
        db.session.add(donation)
        db.session.commit()

    if request.method == 'POST':
        donation.upi_id = sanitize_input(request.form.get('upi_id', ''))
        donation.upi_name = sanitize_input(request.form.get('upi_name', ''))
        donation.bank_account_name = sanitize_input(request.form.get('bank_account_name', ''))
        donation.bank_account_number = sanitize_input(request.form.get('bank_account_number', ''))
        donation.bank_ifsc = sanitize_input(request.form.get('bank_ifsc', ''))
        donation.bank_name = sanitize_input(request.form.get('bank_name', ''))
        donation.bank_branch = sanitize_input(request.form.get('bank_branch', ''))
        donation.whatsapp_number = sanitize_input(request.form.get('whatsapp_number', ''))
        donation.donation_note = sanitize_input(request.form.get('donation_note', ''))
        donation.is_active = bool(request.form.get('is_active', True))

        # QR Code upload
        if 'qr_code_image' in request.files:
            f = request.files['qr_code_image']
            if f and f.filename and allowed_image(f.filename):
                path = save_upload(f, current_app.config['UPLOAD_FOLDER'], 'donation')
                if path:
                    donation.qr_code_image = path

        db.session.commit()
        flash('Donation settings saved!', 'success')
        return redirect(url_for('admin_bp.donation_settings'))

    return render_template('admin/donation_settings.html', donation=donation)