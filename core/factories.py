from .models import Flight, Booking, User
from .database import db
import datetime

class DomainFactory:
    @staticmethod
    def create_user(username, email, password):
        db.cursor.execute(
            "INSERT INTO users (username, email, password, is_staff) VALUES (?, ?, ?, 0)",
            (username, email, password)
        )
        db.conn.commit()
        user_id = db.cursor.lastrowid
        return User(user_id, username, email, password, 0)

    @staticmethod
    def create_flight(flight_number, origin, destination, departure_time, arrival_time, price, seats, category='Domestic'):
        db.cursor.execute(
            "INSERT INTO flights (flight_number, origin, destination, departure_time, arrival_time, price, seats_available, category) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (flight_number, origin, destination, departure_time, arrival_time, price, seats, category)
        )
        db.conn.commit()
        flight_id = db.cursor.lastrowid
        return Flight(flight_id, flight_number, origin, destination, departure_time, arrival_time, price, seats, category)

    @staticmethod
    def create_booking(user, flight):
        date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.cursor.execute(
            "INSERT INTO bookings (user_id, flight_id, booking_date, status) VALUES (?, ?, ?, 'Confirmed')",
            (user.id, flight.id, date_str)
        )
        db.conn.commit()
        booking_id = db.cursor.lastrowid
        return Booking(booking_id, user, flight, date_str, 'Confirmed')
