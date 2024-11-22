class Config:
    """
        Configuration class for the Flask application.
        Defines settings for database connection, session security, and JWT authentication.
    """
    SQLALCHEMY_DATABASE_URI = 'sqlite:///event_management.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'Event_Management_Api_Flask'
    JWT_SECRET_KEY = 'my_jwt_secret_key'
