"""
models.py — Modelos SQLAlchemy para Sorteos Universales
  · User          — Usuarios (admin / user)
  · Event         — Eventos de rifa
  · Ticket        — Boletos comprados
  · SorteoResult  — Resultado del sorteo (ganador)
  · ContactInfo   — Información de la página de contacto
"""
from datetime import datetime
from database import db


class User(db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(120), nullable=False)
    email         = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    phone         = db.Column(db.String(30), default='')
    role          = db.Column(db.String(10), default='user')   # 'admin' | 'user'
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    tickets       = db.relationship('Ticket', backref='user', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.email} [{self.role}]>'


class Event(db.Model):
    __tablename__ = 'events'

    id            = db.Column(db.Integer, primary_key=True)
    title         = db.Column(db.String(200), nullable=False)
    description   = db.Column(db.Text, default='')
    prize_title   = db.Column(db.String(200), default='')

    # Imágenes: puede ser URL externa o ruta relativa a /static/
    event_image   = db.Column(db.Text, default='')
    prize_image   = db.Column(db.Text, default='')
    qr_image      = db.Column(db.Text, default='')  # QR de pago

    ticket_price  = db.Column(db.Float, default=5.0)
    total_tickets = db.Column(db.Integer, default=100)
    ticket_style  = db.Column(db.String(20), default='galactico')  # galactico|estelar|nebulosa

    end_date      = db.Column(db.DateTime, nullable=False)
    status        = db.Column(db.String(15), default='active')  # active|finished
    ended_at      = db.Column(db.DateTime, nullable=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    tickets       = db.relationship('Ticket', backref='event', lazy='dynamic',
                                    cascade='all, delete-orphan')
    result        = db.relationship('SorteoResult', backref='event', uselist=False,
                                    cascade='all, delete-orphan')

    @property
    def sold_count(self):
        return self.tickets.count()

    @property
    def available_count(self):
        return self.total_tickets - self.sold_count

    @property
    def sold_pct(self):
        if self.total_tickets == 0:
            return 0
        return round((self.sold_count / self.total_tickets) * 100)

    @property
    def img_src(self):
        """Devuelve la src correcta para usar en <img>."""
        if not self.event_image:
            return 'https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=800'
        if self.event_image.startswith('http'):
            return self.event_image
        return '/static/' + self.event_image

    @property
    def prize_img_src(self):
        if not self.prize_image:
            return 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600'
        if self.prize_image.startswith('http'):
            return self.prize_image
        return '/static/' + self.prize_image

    @property
    def qr_src(self):
        if not self.qr_image:
            return None
        if self.qr_image.startswith('http'):
            return self.qr_image
        return '/static/' + self.qr_image

    def __repr__(self):
        return f'<Event {self.id}: {self.title}>'


class Ticket(db.Model):
    __tablename__ = 'tickets'

    id            = db.Column(db.Integer, primary_key=True)
    event_id      = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    user_id       = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ticket_number = db.Column(db.Integer, nullable=False)

    buyer_name    = db.Column(db.String(120), default='')
    buyer_email   = db.Column(db.String(200), default='')
    buyer_phone   = db.Column(db.String(30), default='')
    pay_ref       = db.Column(db.String(100), default='')

    purchased_at  = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('event_id', 'ticket_number', name='uq_event_ticket'),
    )

    def __repr__(self):
        return f'<Ticket #{self.ticket_number} Event={self.event_id}>'


class SorteoResult(db.Model):
    __tablename__ = 'sorteo_results'

    id                   = db.Column(db.Integer, primary_key=True)
    event_id             = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False)
    winner_ticket_id     = db.Column(db.Integer, db.ForeignKey('tickets.id'))
    winner_ticket_number = db.Column(db.Integer)
    winner_name          = db.Column(db.String(120), default='')
    winner_email         = db.Column(db.String(200), default='')
    decided_at           = db.Column(db.DateTime, default=datetime.utcnow)

    winner_ticket = db.relationship('Ticket', foreign_keys=[winner_ticket_id])

    def __repr__(self):
        return f'<SorteoResult Event={self.event_id} Winner={self.winner_name}>'


class ContactInfo(db.Model):
    __tablename__ = 'contact_info'

    id           = db.Column(db.Integer, primary_key=True)
    phone        = db.Column(db.String(50), default='+591 70000000')
    address      = db.Column(db.String(300), default='')
    email        = db.Column(db.String(200), default='hola@sorteos-universales.com')
    schedule     = db.Column(db.String(200), default='Lun – Vie: 8:00 AM – 6:00 PM')
    video_url    = db.Column(db.Text, default='')   # YouTube embed URL
    video_local  = db.Column(db.Text, default='')   # ruta /static/uploads/videos/...
    map_embed    = db.Column(db.Text, default='')   # iframe embed HTML de Google Maps
    gallery_json = db.Column(db.Text, default='')   # URLs separadas por coma

    @property
    def gallery_list(self):
        if not self.gallery_json:
            return []
        return [u.strip() for u in self.gallery_json.split(',') if u.strip()]

    @property
    def video_src(self):
        if self.video_local:
            return '/static/' + self.video_local
        return self.video_url or ''
