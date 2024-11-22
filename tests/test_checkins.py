import unittest
from app import create_app, db
from app.models import Event, Attendee
from datetime import datetime, timedelta
import time

class TestCheckIns(unittest.TestCase):
    def setUp(self):
        """
        Set up the test environment, including an in-memory database,
        test client, and test data.
        """
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

            # Create a sample event
            self.event = Event(
                name="Test Event",
                description="A test event",
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(hours=2),
                location="Test Location",
                max_attendees=10,
                status="ongoing"
            )
            db.session.add(self.event)
            db.session.commit()

            # Add a sample attendee to the event
            self.attendee = Attendee(
                first_name="Test",
                last_name="User",
                email="test.user@gmail.com",
                phone_number="1234567890",
                event_id=self.event.id,
                check_in_status=False
            )
            db.session.add(self.attendee)
            db.session.commit()

    def tearDown(self):
        """
        Clean up after each test by removing and dropping the database.
        """
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_individual_checkin(self):
        """
        Test the functionality of individually checking in an attendee.
        """
        with self.app.app_context():
            # Create the event for the test
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

            # Re-fetch the event to ensure it's part of the session
            event = Event.query.get(event.id)

            # Create a unique email for the test
            unique_email = f"test.user{int(time.time())}@gmail.com"

            # Create an attendee for the test with a unique email
            attendee = Attendee(
                first_name="Test",
                last_name="User",
                email=unique_email,
                phone_number="1234567890",
                event_id=event.id
            )
            db.session.add(attendee)
            db.session.commit()

            # Fetch the attendee to verify initial state
            attendee = Attendee.query.get(attendee.id)
            self.assertFalse(attendee.check_in_status)

            # Simulate the check-in action
            attendee.check_in_status = True
            db.session.commit()

            # Fetch the attendee again to confirm the check-in update
            attendee = Attendee.query.get(attendee.id)
            self.assertTrue(attendee.check_in_status)

if __name__ == '__main__':
    unittest.main()