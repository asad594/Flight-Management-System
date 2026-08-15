"""
Factory Pattern Module for SkyBound Flight Management System.

Provides the DomainFactory class responsible for encapsulating the creation
and persistence logic for domain entities (User, Flight, Booking) directly
into the SQLite relational storage layer.
"""

import datetime
from .database import db
from .models import Booking, Flight, User


class DomainFactory:
    """
    Factory Pattern implementation for creating domain entities and persisting them.

    Encapsulates database INSERT queries and returns strongly typed domain model instances.
    """

    @staticmethod
    def create_user(username: str, email: str, password: str) -> User:
        """
        Factory method to construct and persist a standard User entity in SQLite.

        Args:
            username: The unique username for the user account.
            email: The email address associated with the account.
            password: The password string (or pre-hashed digest).

        Returns:
            A populated User domain object with its generated database primary key.
        """
        db.cursor.execute(
            "INSERT INTO users (username, email, password, is_staff) VALUES (?, ?, ?, 0)",
            (username, email, password)
        )
        db.conn.commit()
        user_id = db.cursor.lastrowid
        return User(user_id, username, email, password, 0)

    @staticmethod
    def create_flight(
        flight_number: str,
        origin: str,
        destination: str,
        departure_time: str,
        arrival_time: str,
        price: float,
        seats: int,
        category: str = 'Domestic'
    ) -> Flight:
        """
        Factory method to construct and persist a Flight entity in SQLite.

        Args:
            flight_number: Unique flight schedule identifier (e.g., 'SK-101').
            origin: Departure city or airport name.
            destination: Arrival city or airport name.
            departure_time: Timestamp string of departure.
            arrival_time: Timestamp string of arrival.
            price: Standard ticket price in system currency.
            seats: Initial total seat availability count.
            category: Flight category classification ('Domestic' or 'International').

        Returns:
            A populated Flight domain object with its generated database primary key.
        """
        db.cursor.execute(
            "INSERT INTO flights (flight_number, origin, destination, departure_time, arrival_time, price, seats_available, category) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (flight_number, origin, destination, departure_time, arrival_time, price, seats, category)
        )
        db.conn.commit()
        flight_id = db.cursor.lastrowid
        return Flight(flight_id, flight_number, origin, destination, departure_time, arrival_time, price, seats, category)

    @staticmethod
    def create_booking(user: User, flight: Flight) -> Booking:
        """
        Factory method to construct and persist a Booking reservation in SQLite.

        Args:
            user: The User instance making the reservation.
            flight: The Flight instance being reserved.

        Returns:
            A populated Booking domain object with its generated database primary key.
        """
        date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.cursor.execute(
            "INSERT INTO bookings (user_id, flight_id, booking_date, status) VALUES (?, ?, ?, 'Confirmed')",
            (user.id, flight.id, date_str)
        )
        db.conn.commit()
        booking_id = db.cursor.lastrowid
        return Booking(booking_id, user, flight, date_str, 'Confirmed')


