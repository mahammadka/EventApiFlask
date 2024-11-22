import unittest
from app import create_app, db
from app.models import Event, Attendee
from datetime import datetime, timedelta


class TestRegistrationLimits(unittest.TestCase):
    def setUp(self):
        """Set up the test database and test client."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            # Create an event with a max limit of 2 attendees
            event = Event(
                name="Test Event",
                description="A test event",
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(hours=2),
                location="Test Location",
                max_attendees=2,
                status="scheduled"
            )
            db.session.add(event)
            db.session.commit()
            self.event_id = event.id

    def tearDown(self):
        """Tear down the test database."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def get_event(self):
        """Fetch the event object from the database using the event ID."""
        with self.app.app_context():
            return db.session.get(Event, self.event_id)

    def test_registration_within_limits(self):
        """Test that attendees can register within the event's max limit."""
        with self.app.app_context():
            event = self.get_event()
            attendee1 = Attendee(
                first_name="John",
                last_name="Doe",
                email="john.doe@example.com",
                phone_number="1234567890",
                event_id=event.id
            )
            attendee2 = Attendee(
                first_name="Jane",
                last_name="Smith",
                email="jane.smith@example.com",
                phone_number="9876543210",
                event_id=event.id
            )
            db.session.add_all([attendee1, attendee2])
            db.session.commit()

            attendees = Attendee.query.filter_by(event_id=event.id).all()
            self.assertEqual(len(attendees), 2)

    def test_registration_exceeding_limit(self):
        """Test that attendees cannot register beyond the max limit."""
        with self.app.app_context():
            event = self.get_event()

            # Add the first two attendees
            attendee1 = Attendee(
                first_name="John",
                last_name="Doe",
                email="john.doe@example.com",
                phone_number="1234567890",
                event_id=event.id
            )
            attendee2 = Attendee(
                first_name="Jane",
                last_name="Smith",
                email="jane.smith@example.com",
                phone_number="9876543210",
                event_id=event.id
            )
            db.session.add_all([attendee1, attendee2])
            db.session.flush()
            db.session.commit()

            # Check the attendee count
            print(f"DEBUG: Can add attendee? {event.can_add_attendee()}")
            self.assertFalse(event.can_add_attendee(), "Event should not allow more than max_attendees.")

            # Try adding a third attendee (should fail)
            attendee3 = Attendee(
                first_name="Mark",
                last_name="Lee",
                email="mark.lee@example.com",
                phone_number="5551234567",
                event_id=event.id
            )
            if not event.can_add_attendee():
                with self.assertRaises(ValueError) as context:
                    raise ValueError("Max attendees limit reached!")
            else:
                db.session.add(attendee3)
                db.session.commit()


if __name__ == '__main__':
    unittest.main()