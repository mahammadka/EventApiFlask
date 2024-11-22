### Event Management API
This is a Python-based API built using Flask and SQL for managing events and attendees.

### Features
- Event creation, updating, and listing.
- Attendee registration, listing, and check-in (including bulk check-in via CSV).
- Status updates based on event time.
- JWT authentication for secured endpoints

### Setting up Flask Project
1. Install all the Required Packages:
    - pip install -r requirements.txt

2. Set up the database:
    - flask db init
    - flask db migrate -m "<message_>"
    - flask db upgrade

3. Run the application:
    - flask run

4. To run test files:
    - python -m unittest tests/<test_file>

### API Endpoints

#### 1. Register User
- Register a new user
    - HTTP method : POST
    - url - http://127.0.0.1:5000/auth/register
    - payload - {
    "username": "<test_user>", 
    "password": "<test_password>"
    }

#### 2. Login
- Authenticate a user and provide a JWT token
    - HTTP method : POST
    - url - http://127.0.0.1:5000/auth/login
    - payload - {
    "username": "<test_user>", 
    "password": "<test_password>"
    }

#### 3. Create Event
- Create a new event
    - HTTP method : POST
    - url - http://127.0.0.1:5000/events
    - Authorization - Bearer Token - paste token generated from Login API
    - payload - {
    "name": "<name_of_the_event>",
    "description": "<description_of_the_event>",
    "start_time": "<datetime_in_iso_format>",
    "end_time": "<datetime_in_iso_format>",
    "location": "<location_>",
    "max_attendees": <maximum_attendees>
    }

#### 4. List Events
- List all events and update statuses of past events
    - HTTP method : GET
    - url - http://127.0.0.1:5000/events

#### 4. Update Event
- Update an existing event
    - HTTP method : PUT
    - url - http://127.0.0.1:5000/events/<int:event_id>
    - Authorization - Bearer Token - paste token generated from Login API
    - payload - {
    "name": "<name_of_the_event>", #optional
    "description": "<description_of_the_event>", #optional
    "start_time": "<datetime_in_iso_format>", #optional
    "end_time": "<datetime_in_iso_format>", #optional
    "location": "<location_>", #optional
    "max_attendees": <maximum_attendees>, #optional
    "status": "<status_of_event>" #optional
    }

#### 5. Register Attendee
- Register an attendee for a specific event
    - HTTP method : POST
    - url - http://127.0.0.1:5000/events/<int:event_id>/attendees
    - payload - {
    "first_name": "<first_name>",
    "last_name": "<last_name>",
    "email": "<email_address>",
    "phone_number": "<phone_number>"
    }

#### 6. List Attendees
- List all attendees for a specific event
    - HTTP method : GET
    - url - http://127.0.0.1:5000/events/<int:event_id>/attendees

#### 7. Check-in Attendee
- Mark an attendee as checked in
    - HTTP method : PATCH
    - url - http://127.0.0.1:5000/events/<int:event_id>/attendees/<int:attendee_id>/checkin

#### 8. Bulk Check-in
- Bulk check-in attendees by uploading a CSV file
    - HTTP method : POST
    - url - http://127.0.0.1:5000/events/<int:event_id>/attendees/bulk_checkin
    - payload - {
    key: file, value: <file.csv>
    }
