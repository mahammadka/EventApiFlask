from flask import Blueprint, request, jsonify
from .models import Event, Attendee, db, EventStatus, User
from datetime import datetime
from werkzeug.utils import secure_filename
import csv
import os
from sqlalchemy import func, or_
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

# Define blueprints for authentication, events, and main application routes
auth_bp = Blueprint('auth', __name__)
event_bp = Blueprint('events', __name__)
main = Blueprint('main', __name__)

# Allowed file extensions for CSV
ALLOWED_EXTENSIONS = {'csv'}


@event_bp.route('/events', methods=['POST'])
@jwt_required()
def create_event():
    """Create a new event."""

    current_user_id = get_jwt_identity()
    data = request.json
    event = Event(
        name=data['name'],
        description=data.get('description'),
        start_time=datetime.fromisoformat(data['start_time']),
        end_time=datetime.fromisoformat(data['end_time']),
        location=data['location'],
        max_attendees=data['max_attendees']
    )
    db.session.add(event)
    db.session.commit()
    return jsonify({"message": "Event created successfully"}), 201


@event_bp.route('/events/<int:event_id>', methods=['PUT'])
@jwt_required()
def update_event(event_id):
    """Update an existing event."""

    current_user_id = get_jwt_identity()
    data = request.json
    event = Event.query.get(event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404

    # Check and update each field only if it is provided
    if 'name' in data:
        event.name = data['name']
    if 'description' in data:
        event.description = data['description']
    if 'start_time' in data:
        try:
            event.start_time = datetime.fromisoformat(data['start_time'])
        except ValueError:
            return jsonify({"error": "Invalid start_time format."}), 400
    if 'end_time' in data:
        try:
            event.end_time = datetime.fromisoformat(data['end_time'])
        except ValueError:
            return jsonify({"error": "Invalid end_time format."}), 400
    if 'location' in data:
        event.location = data['location']
    if 'max_attendees' in data:
        try:
            event.max_attendees = int(data['max_attendees'])
        except ValueError:
            return jsonify({"error": "max_attendees must be an integer."}), 400
    if 'status' in data:
        if data['status'] in [status.name for status in EventStatus]:
            event.status = data['status']
        else:
            return jsonify({"error": "Invalid status. Allowed values are: scheduled, ongoing, completed, canceled."}), 400

    db.session.commit()
    return jsonify({"message": "Event updated successfully"}), 200


@main.route('/events', methods=['GET'])
def list_events():
    """List all events and update statuses of past events."""

    now = datetime.utcnow().replace(microsecond=0)
    events = Event.query.all()

    for event in events:
        # Automatically update event status to 'completed' if it has ended
        if event.end_time < now and event.status.name == "ongoing":
            event.status = "completed"
            db.session.commit()

    result = [{"id": e.id, "name": e.name, "location": e.location, "status": e.status.name} for e in events]
    return jsonify(result), 200


@main.route('/events/<int:event_id>/attendees', methods=['POST'])
def register_attendee(event_id):
    """Register an attendee for a specific event."""

    data = request.json
    event = Event.query.get(event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404

    # Check if the attendee is already registered or the event is full
    if Attendee.query.filter_by(email=data['email'], event_id=event_id).first():
        return jsonify({"error": "Attendee already registered"}), 400
    if Attendee.query.filter_by(event_id=event_id).count() >= event.max_attendees:
        return jsonify({"error": "Max attendees reached"}), 400

    # Register a new attendee
    attendee = Attendee(
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        phone_number=data.get('phone_number'),
        event_id=event_id
    )
    db.session.add(attendee)
    db.session.commit()
    return jsonify({"message": "Attendee registered successfully"}), 201


@main.route('/events/<int:event_id>/attendees', methods=['GET'])
def list_attendees(event_id):
    """List all attendees for a specific event."""

    event = Event.query.get(event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404

    # Optionally filter by check-in status
    check_in_status = request.args.get('check_in_status')
    attendees_query = Attendee.query.filter_by(event_id=event_id)
    if check_in_status is not None:
        check_in_status = check_in_status.lower() == 'true'
        attendees_query = attendees_query.filter_by(check_in_status=check_in_status)

    # Return attendee details
    attendees = attendees_query.all()
    result = [
        {
            "id": attendee.id,
            "first_name": attendee.first_name,
            "last_name": attendee.last_name,
            "email": attendee.email,
            "check_in_status": attendee.check_in_status,
        }
        for attendee in attendees
    ]

    return jsonify(result), 200


@main.route('/events/<int:event_id>/attendees/<int:attendee_id>/checkin', methods=['PATCH'])
def check_in_attendee(event_id, attendee_id):
    """Mark an attendee as checked in."""

    event = Event.query.get(event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404

    attendee = Attendee.query.filter_by(id=attendee_id, event_id=event_id).first()
    if not attendee:
        return jsonify({"error": "Attendee not found"}), 404

    if attendee.check_in_status:
        return jsonify({"message": "Attendee is already checked in"}), 400

    # Mark the attendee as checked in
    attendee.check_in_status = True
    db.session.commit()

    return jsonify({"message": "Attendee checked in successfully"}), 200


@main.route('/events/<int:event_id>/attendees/bulk_checkin', methods=['POST'])
def bulk_checkin(event_id):
    """Bulk check-in attendees by uploading a CSV file."""

    event = Event.query.get(event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404

    file = request.files.get('file')
    if not file or file.filename == '':
        return jsonify({"error": "No file uploaded or file is empty."}), 400

    filename = secure_filename(file.filename)

    # Verify the file extension is .csv
    if not filename.lower().endswith('.csv'):
        return jsonify({"error": "Invalid file type. Please upload a CSV file."}), 400

    # Save the file
    upload_dir = os.path.join(os.getcwd(), 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)

    # Process the CSV file
    updated_attendees = []
    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            first_name = row.get('first_name', '').strip()
            last_name = row.get('last_name', '').strip()
            email = row.get('email', '').strip().lower()
            phone_number = row.get('phone_number', '').strip()

            print(f"Processing: {first_name} {last_name}, Email: {email}, Phone: {phone_number}")

            # Query for existing attendee
            attendee = Attendee.query.filter(
                Attendee.event_id == event_id,
                or_(
                    func.lower(Attendee.email) == email,
                    Attendee.phone_number == phone_number
                )
            ).first()

            if attendee:
                # Update check-in status for existing attendee
                attendee.check_in_status = True
                updated_attendees.append({
                    "first_name": attendee.first_name,
                    "last_name": attendee.last_name,
                    "email": attendee.email,
                    "phone_number": attendee.phone_number,
                    "status": "Checked In"
                })
            else:
                # Add new attendee if not found
                new_attendee = Attendee(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone_number=phone_number,
                    event_id=event_id,
                    check_in_status=True
                )
                db.session.add(new_attendee)
                updated_attendees.append({
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "phone_number": phone_number,
                    "status": "Added and Checked In"
                })

    db.session.commit()

    return jsonify({
        "message": "Bulk check-in completed",
        "attendees": updated_attendees
    }), 200


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""

    data = request.get_json()
    if not data.get('username') or not data.get('password'):
        return jsonify({"error": "Username and password required"}), 400

    user = User(username=data['username'], password=data['password'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully!"}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate a user and provide a JWT token."""

    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        access_token = create_access_token(identity=str(user.id))
        return jsonify(access_token=access_token)

    return jsonify({"error": "Invalid credentials"}), 401
