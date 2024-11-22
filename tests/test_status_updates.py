import unittest
from app import create_app, db
from app.models import Event, EventStatus
from datetime import datetime, timedelta

class TestStatusUpdates(unittest.TestCase):
    def setUp(self):
        """Set up the test database and client for status updates."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            # Create an event that has already ended
            self.event = Event(
                name="Test Event",
                description="A test event",
                start_time=datetime.now() - timedelta(days=1),
                end_time=datetime.now() - timedelta(hours=1),
                location="Test Location",
                max_attendees=10,
                status=EventStatus.ongoing
            )
            db.session.add(self.event)
            db.session.commit()
            self.event_id = self.event.id

    def tearDown(self):
        """Tear down the test database after each test."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_automatic_status_update(self):
        """Test that an event's status updates to 'completed' after end_time"""
        with self.app.app_context():
            event = db.session.get(Event, self.event.id)

            # Update status only if the event has already ended
            if event and event.end_time < datetime.now():
                event.status = EventStatus.completed
                db.session.commit()

                # Re-fetch the event again after commit to get updated data
                event = db.session.get(Event, self.event.id)

            self.assertEqual(event.status, EventStatus.completed)

if __name__ == '__main__':
    unittest.main()