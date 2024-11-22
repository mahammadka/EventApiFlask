from . import db
from sqlalchemy import Enum
import enum
from werkzeug.security import generate_password_hash, check_password_hash

# Enum for representing the status of an event
class EventStatus(enum.Enum):
    scheduled = "scheduled"
    ongoing = "ongoing"
    completed = "completed"
    canceled = "canceled"

# Model for events
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    max_attendees = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(EventStatus), default=EventStatus.scheduled)

    def can_add_attendee(self):
        """Check if the event can accept more attendees."""
        return Attendee.query.filter_by(event_id=self.id).count() < self.max_attendees

# Model for attendees of events
class Attendee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(15), nullable=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    check_in_status = db.Column(db.Boolean, default=False)

# Model for users (authentication)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)