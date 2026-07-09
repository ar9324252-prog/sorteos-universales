"""
╔══════════════════════════════════════════════════════════════╗
║            SORTEOS UNIVERSALES — app.py                     ║
║  Flask + SQLite + Uploads  |  Plataforma completa de rifas  ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import random
import string
from datetime import datetime, timezone, timedelta
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from database import db
from models import User, Event, Ticket, ContactInfo, SorteoResult

# ── App config ────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'su-secret-galaxia-2024-xK9#mP!')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sorteos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
UPLOAD_ROOT = os.path.join(BASE_DIR, 'static', 'uploads')
ALLOWED_IMG = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_VID = {'mp4', 'webm', 'ogg'}
MAX_CONTENT = 50 * 1024 * 1024

app.config['UPLOAD_FOLDER'] = UPLOAD_ROOT
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT

db.init_app(app)

# ── Helpers ───────────────────────────────────────────────────
def allowed_file(filename, allowed):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed

def save_upload(file, subfolder, allowed):
    if not file or file.filename == '':
        return None
    if not allowed_file(file.filename, allowed):
        return None
    fname  = secure_filename(file.filename)
    unique = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    fname  = f"{unique}_{fname}"
    folder = os.path.join(UPLOAD_ROOT, subfolder)
    os.makedirs(folder, exist_ok=True)
    file.save(os.path.join(folder, fname))
    return f'uploads/{subfolder}/{fname}'

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión para acceder.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Acceso restringido.', 'error')
            return redirect(url_for('login'))
        user = db.session.get(User, session['user_id'])
        if not user or user.role != 'admin':
            flash('No tienes permisos de administrador.', 'error')
            return render_template('publico_denegado.html', current_user=user)
        return f(*args, **kwargs)
    return decorated

def current_user():
    if 'user_id' in session:
        return db.session.get(User, session['user_id'])
    return None

def now_utc():
    return datetime.utcnow()


def redirect_to_index():
    try:
        return redirect(url_for('index'))
    except Exception:
        return redirect('/')


@app.context_processor
def inject_user():
    return {'current_user': current_user()}

# ══════════════════════════════════════════════════════════════
#  RUTAS PÚBLICAS
# ══════════════════════════════════════════════════════════════

@app.route('/', endpoint='index')
def index():
    events   = Event.query.filter_by(status='active').order_by(Event.created_at.desc()).all()
    finished = Event.query.filter_by(status='finished').order_by(Event.ended_at.desc()).limit(6).all()
    return render_template('index.html', events=events, finished=finished, now=now_utc())

@app.route('/eventos')
def eventos():
    events   = Event.query.filter_by(status='active').order_by(Event.created_at.desc()).all()
    finished = Event.query.filter_by(status='finished').order_by(Event.ended_at.desc()).all()
    return render_template('eventos.html', events=events, finished=finished, now=now_utc())

@app.route('/evento/<int:event_id>')
def evento_detalle(event_id):
    evt       = Event.query.get_or_404(event_id)
    tickets   = Ticket.query.filter_by(event_id=event_id).all()
    sold_nums = {t.ticket_number for t in tickets}
    user      = current_user()
    my_tickets = [t for t in tickets if user and t.user_id == user.id]
    result    = SorteoResult.query.filter_by(event_id=event_id).first()
    return render_template(
        'evento_detalle.html',
        evt=evt, tickets=tickets, sold_nums=sold_nums,
        my_tickets=my_tickets, result=result, now=now_utc()
    )

@app.route('/nosotros')
def nosotros():
    return render_template('nosotros.html')

@app.route('/contacto')
def contacto():
    info = ContactInfo.query.first()
    return render_template('contacto.html', info=info)

@app.route('/api/evento/<int:event_id>/tickets')
def api_tickets(event_id):
    evt  = Event.query.get_or_404(event_id)
    sold = [t.ticket_number for t in Ticket.query.filter_by(event_id=event_id).all()]
    return jsonify({'total': evt.total_tickets, 'sold': sold, 'price': float(evt.ticket_price)})

# ══════════════════════════════════════════════════════════════
#  AUTH
# ══════════════════════════════════════════════════════════════

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user():
        return redirect(url_for('index'))
    if request.method == 'POST':
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user     = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session.permanent  = True
            flash(f'¡Bienvenido, {user.name}! 🚀', 'success')
            return redirect(url_for('admin_dashboard') if user.role == 'admin' else url_for('index'))
        flash('Correo o contraseña incorrectos.', 'error')
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user():
        return redirect(url_for('index'))
    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        phone    = request.form.get('phone', '').strip()
        if not name or not email or not password:
            flash('Completa todos los campos requeridos.', 'error')
            return render_template('registro.html')
        if len(password) < 6:
            flash('La contraseña debe tener al menos 6 caracteres.', 'error')
            return render_template('registro.html')
        if User.query.filter_by(email=email).first():
            flash('El correo ya está registrado.', 'error')
            return render_template('registro.html')
        user = User(name=name, email=email,
                    password_hash=generate_password_hash(password),
                    phone=phone, role='user')
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        flash(f'¡Cuenta creada! Bienvenido al universo, {name}! 🌟', 'success')
        return redirect(url_for('index'))
    return render_template('registro.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada. ¡Hasta pronto! 👋', 'success')
    return redirect(url_for('index'))

# ══════════════════════════════════════════════════════════════
#  COMPRA
# ══════════════════════════════════════════════════════════════

@app.route('/evento/<int:event_id>/comprar', methods=['POST'])
@login_required
def comprar_boletos(event_id):
    evt  = Event.query.get_or_404(event_id)
    user = current_user()
    if evt.status != 'active' or evt.end_date <= now_utc():
        flash('Este evento no está disponible para compra.', 'error')
        return redirect(url_for('evento_detalle', event_id=event_id))
    nums_raw = request.form.getlist('tickets')
    if not nums_raw:
        flash('Selecciona al menos un boleto.', 'error')
        return redirect(url_for('evento_detalle', event_id=event_id))
    try:
        nums = [int(n) for n in nums_raw]
    except ValueError:
        flash('Números de boleto inválidos.', 'error')
        return redirect(url_for('evento_detalle', event_id=event_id))
    if any(n < 1 or n > evt.total_tickets for n in nums):
        flash('Boleto fuera de rango.', 'error')
        return redirect(url_for('evento_detalle', event_id=event_id))
    sold_nums = {t.ticket_number for t in Ticket.query.filter_by(event_id=event_id).all()}
    conflict  = [n for n in nums if n in sold_nums]
    if conflict:
        flash(f'Los boletos {conflict} ya fueron vendidos. Selecciona otros.', 'error')
        return redirect(url_for('evento_detalle', event_id=event_id))
    buyer_name  = request.form.get('buyer_name', user.name).strip()
    buyer_email = request.form.get('buyer_email', user.email).strip()
    buyer_phone = request.form.get('buyer_phone', '').strip()
    pay_ref     = request.form.get('pay_ref', '').strip()
    for n in nums:
        db.session.add(Ticket(
            event_id=event_id, user_id=user.id, ticket_number=n,
            buyer_name=buyer_name, buyer_email=buyer_email,
            buyer_phone=buyer_phone, pay_ref=pay_ref
        ))
    db.session.commit()
    flash(f'🎉 ¡Compra exitosa! Adquiriste {len(nums)} boleto(s): {", ".join(f"#{n:03d}" for n in sorted(nums))}.', 'success')
    return redirect(url_for('evento_detalle', event_id=event_id))

# ══════════════════════════════════════════════════════════════
#  ADMIN
# ══════════════════════════════════════════════════════════════

@app.route('/admin', endpoint='admin_dashboard')
@admin_required
def admin_dashboard():
    return render_template('admin/dashboard.html',
        total_events=Event.query.count(),
        active_events=Event.query.filter_by(status='active').count(),
        total_tickets=Ticket.query.count(),
        total_users=User.query.filter_by(role='user').count(),
        recent_tickets=Ticket.query.order_by(Ticket.purchased_at.desc()).limit(10).all(),
        events=Event.query.order_by(Event.created_at.desc()).all(),
        now=now_utc()
    )

@app.route('/admin/eventos')
@admin_required
def admin_eventos():
    events = Event.query.order_by(Event.created_at.desc()).all()
    return render_template('admin/eventos.html', events=events, now=now_utc())

@app.route('/admin/eventos/nuevo', methods=['GET', 'POST'])
@admin_required
def admin_nuevo_evento():
    if request.method == 'POST':
        title        = request.form.get('title', '').strip()
        description  = request.form.get('description', '').strip()
        prize_title  = request.form.get('prize_title', '').strip()
        ticket_price = float(request.form.get('ticket_price', 5))
        total_tickets= int(request.form.get('total_tickets', 100))
        end_date_str = request.form.get('end_date', '')
        ticket_style = request.form.get('ticket_style', 'galactico')
        qr_url       = request.form.get('qr_url', '').strip()
        event_url    = request.form.get('event_image_url', '').strip()
        prize_url    = request.form.get('prize_image_url', '').strip()
        if not title or not description or not prize_title or not end_date_str:
            flash('Completa todos los campos requeridos.', 'error')
            return render_template('admin/evento_form.html', evt=None)
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Fecha de cierre inválida.', 'error')
            return render_template('admin/evento_form.html', evt=None)
        if end_date <= now_utc():
            flash('La fecha debe ser en el futuro.', 'error')
            return render_template('admin/evento_form.html', evt=None)
        event_img = save_upload(request.files.get('event_image_file'), 'events', ALLOWED_IMG) or event_url or ''
        prize_img = save_upload(request.files.get('prize_image_file'), 'prizes', ALLOWED_IMG) or prize_url or ''
        qr_img    = save_upload(request.files.get('qr_file'), 'qr', ALLOWED_IMG) or qr_url or ''
        evt = Event(title=title, description=description, prize_title=prize_title,
                    event_image=event_img, prize_image=prize_img,
                    ticket_price=ticket_price, total_tickets=total_tickets,
                    end_date=end_date, ticket_style=ticket_style,
                    qr_image=qr_img, status='active')
        db.session.add(evt)
        db.session.commit()
        flash(f'🚀 Evento "{title}" creado.', 'success')
        return redirect(url_for('admin_eventos'))
    return render_template('admin/evento_form.html', evt=None)

@app.route('/admin/eventos/<int:event_id>/editar', methods=['GET', 'POST'])
@admin_required
def admin_editar_evento(event_id):
    evt = Event.query.get_or_404(event_id)
    if request.method == 'POST':
        evt.title         = request.form.get('title', evt.title).strip()
        evt.description   = request.form.get('description', evt.description).strip()
        evt.prize_title   = request.form.get('prize_title', evt.prize_title).strip()
        evt.ticket_price  = float(request.form.get('ticket_price', evt.ticket_price))
        evt.total_tickets = int(request.form.get('total_tickets', evt.total_tickets))
        evt.ticket_style  = request.form.get('ticket_style', evt.ticket_style)
        qr_url   = request.form.get('qr_url', '').strip()
        ev_url   = request.form.get('event_image_url', '').strip()
        pr_url   = request.form.get('prize_image_url', '').strip()
        try:
            evt.end_date = datetime.strptime(request.form.get('end_date',''), '%Y-%m-%dT%H:%M')
        except ValueError:
            pass
        new_ev = save_upload(request.files.get('event_image_file'), 'events', ALLOWED_IMG)
        if new_ev: evt.event_image = new_ev
        elif ev_url: evt.event_image = ev_url
        new_pr = save_upload(request.files.get('prize_image_file'), 'prizes', ALLOWED_IMG)
        if new_pr: evt.prize_image = new_pr
        elif pr_url: evt.prize_image = pr_url
        new_qr = save_upload(request.files.get('qr_file'), 'qr', ALLOWED_IMG)
        if new_qr: evt.qr_image = new_qr
        elif qr_url: evt.qr_image = qr_url
        db.session.commit()
        flash(f'✅ Evento actualizado.', 'success')
        return redirect(url_for('admin_eventos'))
    return render_template('admin/evento_form.html', evt=evt)

@app.route('/admin/eventos/<int:event_id>/eliminar', methods=['POST'])
@admin_required
def admin_eliminar_evento(event_id):
    evt = Event.query.get_or_404(event_id)
    Ticket.query.filter_by(event_id=event_id).delete()
    SorteoResult.query.filter_by(event_id=event_id).delete()
    db.session.delete(evt)
    db.session.commit()
    flash(f'Evento "{evt.title}" eliminado.', 'success')
    return redirect(url_for('admin_eventos'))

@app.route('/admin/eventos/<int:event_id>/sorteo', methods=['POST'])
@admin_required
def admin_sorteo(event_id):
    evt     = Event.query.get_or_404(event_id)
    tickets = Ticket.query.filter_by(event_id=event_id).all()
    if not tickets:
        flash('Sin compradores para el sorteo.', 'error')
        return redirect(url_for('admin_eventos'))
    winner = random.choice(tickets)
    result = SorteoResult(event_id=event_id, winner_ticket_id=winner.id,
        winner_ticket_number=winner.ticket_number,
        winner_name=winner.buyer_name, winner_email=winner.buyer_email,
        decided_at=now_utc())
    evt.status   = 'finished'
    evt.ended_at = now_utc()
    db.session.add(result)
    db.session.commit()
    flash(f'🏆 Ganador: {winner.buyer_name} — Boleto #{winner.ticket_number:03d}', 'success')
    return redirect(url_for('admin_eventos'))

@app.route('/admin/eventos/<int:event_id>/compradores')
@admin_required
def admin_compradores(event_id):
    evt     = Event.query.get_or_404(event_id)
    tickets = Ticket.query.filter_by(event_id=event_id).order_by(Ticket.ticket_number).all()
    result  = SorteoResult.query.filter_by(event_id=event_id).first()
    return render_template('admin/compradores.html', evt=evt, tickets=tickets, result=result)

@app.route('/admin/usuarios')
@admin_required
def admin_usuarios():
    users = User.query.order_by(User.created_at.desc()).all()
    counts = {u.id: Ticket.query.filter_by(user_id=u.id).count() for u in users}
    return render_template('admin/usuarios.html', users=users, ticket_counts=counts)

@app.route('/admin/usuarios/<int:user_id>/eliminar', methods=['POST'])
@admin_required
def admin_eliminar_usuario(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        flash('No puedes eliminar una cuenta de administrador.', 'error')
        return redirect(url_for('admin_usuarios'))
    Ticket.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()
    flash(f'Usuario eliminado.', 'success')
    return redirect(url_for('admin_usuarios'))

@app.route('/admin/contacto', methods=['GET', 'POST'])
@admin_required
def admin_contacto():
    info = ContactInfo.query.first()
    if not info:
        info = ContactInfo()
        db.session.add(info)
        db.session.commit()
    if request.method == 'POST':
        info.phone     = request.form.get('phone', '').strip()
        info.address   = request.form.get('address', '').strip()
        info.email     = request.form.get('email', '').strip()
        info.schedule  = request.form.get('schedule', '').strip()
        info.video_url = request.form.get('video_url', '').strip()
        info.map_embed = request.form.get('map_embed', '').strip()
        gallery = [request.form.get(f'gallery_{i}','').strip() for i in range(6)]
        for i in range(6):
            gimg = save_upload(request.files.get(f'gallery_file_{i}'), 'gallery', ALLOWED_IMG)
            if gimg: gallery.append(gimg)
        info.gallery_json = ','.join(g for g in gallery if g)
        vid = save_upload(request.files.get('video_file'), 'videos', ALLOWED_VID)
        if vid: info.video_local = vid
        db.session.commit()
        flash('✅ Información de contacto actualizada.', 'success')
        return redirect(url_for('admin_contacto'))
    return render_template('admin/contacto.html', info=info)

@app.route('/admin/uploads')
@admin_required
def admin_uploads():
    cats = {
        'events':  'Imágenes de Eventos',
        'prizes':  'Imágenes de Premios',
        'qr':      'Códigos QR',
        'gallery': 'Galería',
        'videos':  'Videos',
    }
    files_by_cat = {}
    for cat, label in cats.items():
        folder = os.path.join(UPLOAD_ROOT, cat)
        os.makedirs(folder, exist_ok=True)
        files_by_cat[cat] = {'label': label, 'files': sorted(os.listdir(folder))}
    return render_template('admin/uploads.html', files_by_cat=files_by_cat)

@app.route('/admin/uploads/eliminar', methods=['POST'])
@admin_required
def admin_eliminar_upload():
    subfolder = request.form.get('subfolder', '')
    filename  = secure_filename(request.form.get('filename', ''))
    path = os.path.join(UPLOAD_ROOT, subfolder, filename)
    if os.path.exists(path):
        os.remove(path)
        flash(f'Archivo eliminado.', 'success')
    else:
        flash('Archivo no encontrado.', 'error')
    return redirect(url_for('admin_uploads'))

@app.route('/admin/uploads/nuevo', methods=['POST'])
@admin_required
def admin_upload_nuevo():
    subfolder = request.form.get('subfolder', 'gallery')
    allowed   = ALLOWED_VID if subfolder == 'videos' else ALLOWED_IMG
    path = save_upload(request.files.get('file'), subfolder, allowed)
    flash('✅ Archivo subido.' if path else 'Error al subir. Verifica el formato.', 'success' if path else 'error')
    return redirect(url_for('admin_uploads'))

# ══════════════════════════════════════════════════════════════
#  SEED + MAIN
# ══════════════════════════════════════════════════════════════

def seed_data():
    if User.query.count() == 0:
        db.session.add_all([
            User(name='Administrador', email='admin@sorteos.com',
                 password_hash=generate_password_hash('admin123'), role='admin', phone='+591 70000000'),
            User(name='Usuario Prueba', email='usuario@test.com',
                 password_hash=generate_password_hash('user123'), role='user', phone='+591 70000001'),
        ])
        db.session.commit()
    if Event.query.count() == 0:
        now = now_utc()
        db.session.add_all([
            Event(title='Rifa Interestelar: Telescopio Profesional',
                  description='Gana un telescopio refractor profesional de 8" con montura ecuatorial motorizada. Observa galaxias, nebulosas y planetas desde tu jardín. Premio valorado en $1,200 USD.',
                  prize_title='Telescopio Refractor 8" Celestron',
                  event_image='https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=800&auto=format&fit=crop',
                  prize_image='https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600&auto=format&fit=crop',
                  ticket_price=5.0, total_tickets=100,
                  end_date=now + timedelta(hours=48),
                  ticket_style='galactico', status='active', qr_image=''),
            Event(title='Sorteo Cosmos: Viaje al Planetario',
                  description='Viaja todo pagado al Planetario Nacional y Observatorio Astronómico. Incluye hotel 5 estrellas por 3 noches y cena de gala bajo las estrellas.',
                  prize_title='Viaje VIP al Observatorio 3 noches',
                  event_image='https://images.unsplash.com/photo-1419242902214-272b3f66ee7a?w=800&auto=format&fit=crop',
                  prize_image='https://images.unsplash.com/photo-1444703686981-a3abbc4d4fe3?w=600&auto=format&fit=crop',
                  ticket_price=10.0, total_tickets=200,
                  end_date=now + timedelta(days=5),
                  ticket_style='nebulosa', status='active', qr_image=''),
        ])
        db.session.commit()
    if ContactInfo.query.count() == 0:
        db.session.add(ContactInfo(
            phone='+591 78780260', address='Av.intenacional, plan3000, Santa Cruz',
            email='peperibas06@gmail.com', schedule='Lun – Vie: 8:00 AM – 00:00 PM',
            video_url='https://www.youtube.com/embed/0DJNteTwOZk',
            gallery_json='https://images.unsplash.com/photo-1543722530-d2c3201371e7?w=600,https://images.unsplash.com/photo-1502134249126-9f3755a50d78?w=600,https://images.unsplash.com/photo-1614642264762-d0a3b8bf3700?w=600,https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=600'
        ))
        db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_data()
    app.run(debug=True, host='0.0.0.0', port=5000)
