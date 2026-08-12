from .models import Flight, Booking, User
from .database import db
import datetime

class DomainFactory:
    """Factory Pattern implementation for creating domain models and persisting them to SQLite."""

    @staticmethod
    def create_user(username: str, email: str, password: str) -> User:
        """Factory method to construct and persist a standard User entity."""
        db.cursor.execute(
            "INSERT INTO users (username, email, password, is_staff) VALUES (?, ?, ?, 0)",
            (username, email, password)
        )
        db.conn.commit()
        user_id = db.cursor.lastrowid
        return User(user_id, username, email, password, 0)

    @staticmethod
    def create_flight(flight_number: str, origin: str, destination: str, departure_time: str, arrival_time: str, price: float, seats: int, category: str = 'Domestic') -> Flight:
        """Factory method to construct and persist a Flight entity."""
        db.cursor.execute(
            "INSERT INTO flights (flight_number, origin, destination, departure_time, arrival_time, price, seats_available, category) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (flight_number, origin, destination, departure_time, arrival_time, price, seats, category)
        )
        db.conn.commit()
        flight_id = db.cursor.lastrowid
        return Flight(flight_id, flight_number, origin, destination, departure_time, arrival_time, price, seats, category)

    @staticmethod
    def create_booking(user: User, flight: Flight) -> Booking:
        """Factory method to construct and persist a Booking entity."""
        date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.cursor.execute(
            "INSERT INTO bookings (user_id, flight_id, booking_date, status) VALUES (?, ?, ?, 'Confirmed')",
            (user.id, flight.id, date_str)
        )
        db.conn.commit()
        booking_id = db.cursor.lastrowid
        return Booking(booking_id, user, flight, date_str, 'Confirmed')

