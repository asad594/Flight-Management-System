"""
Domain Models Module for SkyBound Flight Management System.

Defines the core plain-Python entity classes representing users, flights,
bookings, payments, and notifications, decoupled from heavy ORM abstractions.
"""

from typing import Any, Optional, Union


class User:
    """
    Domain model representing a system user or administrator.

    Attributes:
        id (int): Unique database primary key identifier.
        username (str): Unique username for authentication.
        email (str): Contact email address for booking confirmations.
        password (str): Stored authentication credential hash or token.
        is_staff (bool): Privilege flag indicating administrative access rights.
    """

    def __init__(self, id: int, username: str, email: str, password: str, is_staff: Union[bool, int]) -> None:
        """
        Initializes a User domain entity instance.

        Args:
            id: Unique integer identifier.
            username: Account username string.
            email: Account email string.
            password: User password or hash string.
            is_staff: Boolean or integer (0/1) flag indicating admin access.
        """
        self.id: int = id
        self.username: str = username
        self.email: str = email
        self.password: str = password
        self.is_staff: bool = bool(is_staff)

    def __repr__(self) -> str:
        """Returns unambiguous developer string representation of the User entity."""
        return f"<User id={self.id} username='{self.username}' is_staff={bool(self.is_staff)}>"

    def __str__(self) -> str:
        """Returns human-readable string representation of the user."""
        return self.username


class Flight:
    """
    Domain model representing a scheduled flight route and inventory.

    Attributes:
        id (int): Unique database primary key identifier.
        flight_number (str): Unique flight code identifier (e.g., 'SK-101').
        origin (str): Departure city or airport location.
        destination (str): Arrival destination city or airport location.
        departure_time (str): Scheduled departure timestamp string.
        arrival_time (str): Scheduled arrival timestamp string.
        price (float): Base ticket price in USD / configured currency.
        seats_available (int): Remaining available seat inventory count.
        category (str): Flight route classification ('Domestic' or 'International').
    """

    def __init__(
        self,
        id: int,
        flight_number: str,
        origin: str,
        destination: str,
        departure_time: str,
        arrival_time: str,
        price: float,
        seats_available: int,
        category: str = 'Domestic'
    ) -> None:
        """
        Initializes a Flight domain entity instance.

        Args:
            id: Unique integer identifier.
            flight_number: Alphanumeric flight code.
            origin: Departure location.
            destination: Arrival location.
            departure_time: ISO or formatted departure datetime string.
            arrival_time: ISO or formatted arrival datetime string.
            price: Standard seat price.
            seats_available: Number of unbooked seats.
            category: Route classification.
        """
        self.id: int = id
        self.flight_number: str = flight_number
        self.origin: str = origin
        self.destination: str = destination
        self.departure_time: str = departure_time
        self.arrival_time: str = arrival_time
        self.price: float = price
        self.seats_available: int = seats_available
        self.category: str = category

    def __repr__(self) -> str:
        """Returns unambiguous developer string representation of the Flight entity."""
        return f"<Flight id={self.id} number='{self.flight_number}' route='{self.origin}->{self.destination}' price={self.price}>"

    def __str__(self) -> str:
        """Returns human-readable route string representation."""
        return f"{self.flight_number}: {self.origin} -> {self.destination}"


class Booking:
    """
    Domain model representing a passenger flight reservation.

    Attributes:
        id (int): Unique database primary key identifier.
        user (User): Associated User domain object who placed the booking.
        flight (Flight): Reserved Flight domain object.
        booking_date (str): Timestamp string when reservation was recorded.
        status (str): Current reservation lifecycle status ('Confirmed', 'Cancelled', etc.).
    """

    def __init__(self, id: int, user: Any, flight: Any, booking_date: str, status: str) -> None:
        """
        Initializes a Booking domain entity instance.

        Args:
            id: Unique integer identifier.
            user: Associated User domain object or user id.
            flight: Associated Flight domain object or flight id.
            booking_date: Booking timestamp string.
            status: Reservation status string.
        """
        self.id: int = id
        self.user: Any = user
        self.flight: Any = flight
        self.booking_date: str = booking_date
        self.status: str = status

    def __repr__(self) -> str:
        """Returns unambiguous developer string representation of the Booking entity."""
        return f"<Booking id={self.id} user={self.user} flight={self.flight} status='{self.status}'>"

    def __str__(self) -> str:
        """Returns human-readable booking summary string."""
        return f"Booking #{self.id} ({self.status})"


class Payment:
    """
    Domain model representing a financial transaction for a booking.

    Attributes:
        id (int): Unique database primary key identifier.
        booking (Booking): Associated Booking domain object.
        amount (float): Transaction total amount.
        method (str): Gateway/strategy identifier used for payment.
        transaction_id (str): Unique transaction reference identifier.
        status (str): Payment gateway status ('Success', 'Pending', 'Failed').
    """

    def __init__(
        self,
        id: int,
        booking: Any,
        amount: float,
        method: str,
        transaction_id: str,
        status: str
    ) -> None:
        """
        Initializes a Payment domain entity instance.

        Args:
            id: Unique integer identifier.
            booking: Associated Booking domain object.
            amount: Total monetary value paid.
            method: Payment strategy name.
            transaction_id: External or generated transaction ID.
            status: Final or pending payment state.
        """
        self.id: int = id
        self.booking: Any = booking
        self.amount: float = amount
        self.method: str = method
        self.transaction_id: str = transaction_id
        self.status: str = status

    def __repr__(self) -> str:
        """Returns unambiguous developer string representation of the Payment entity."""
        return f"<Payment id={self.id} amount={self.amount} method='{self.method}' status='{self.status}'>"

    def __str__(self) -> str:
        """Returns human-readable payment summary string."""
        return f"Payment #{self.id} ({self.method} - ${self.amount})"


class Notification:
    """
    Domain model representing an alert or event notification for a user.

    Attributes:
        id (int): Unique database primary key identifier.
        user (User): Recipient User domain object.
        message (str): Notification body text.
        is_read (bool): Boolean flag denoting whether the user has read the notice.
        created_at (str): Generation timestamp string.
    """

    def __init__(
        self,
        id: int,
        user: Any,
        message: str,
        is_read: Union[bool, int],
        created_at: str
    ) -> None:
        """
        Initializes a Notification domain entity instance.

        Args:
            id: Unique integer identifier.
            user: Recipient User domain object.
            message: Informational alert message.
            is_read: Read state flag.
            created_at: Creation timestamp string.
        """
        self.id: int = id
        self.user: Any = user
        self.message: str = message
        self.is_read: bool = bool(is_read)
        self.created_at: str = created_at

    def __repr__(self) -> str:
        """Returns unambiguous developer string representation of the Notification entity."""
        return f"<Notification id={self.id} user={self.user} is_read={bool(self.is_read)}>"

    def __str__(self) -> str:
        """Returns human-readable notification message string."""
        return f"Notification: {self.message}"



