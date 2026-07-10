import os
from app import app, db
from models import User, Event, Ticket, ContactInfo, SorteoResult

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Event': Event,
        'Ticket': Ticket,
        'ContactInfo': ContactInfo,
        'SorteoResult': SorteoResult
    }

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()
