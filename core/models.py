class User:
    """Represents a system user or administrator within the domain layer."""
    def __init__(self, id: int, username: str, email: str, password: str, is_staff: bool):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.is_staff = is_staff

    def __repr__(self) -> str:
        return f"<User id={self.id} username='{self.username}' is_staff={bool(self.is_staff)}>"

    def __str__(self) -> str:
        return self.username

class Flight:
    """Represents a flight schedule with origin, destination, and seating details."""
    def __init__(self, id: int, flight_number: str, origin: str, destination: str, departure_time: str, arrival_time: str, price: float, seats_available: int, category: str = 'Domestic'):
        self.id = id
        self.flight_number = flight_number
        self.origin = origin
        self.destination = destination
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.price = price
        self.seats_available = seats_available
        self.category = category

    def __repr__(self) -> str:
        return f"<Flight id={self.id} number='{self.flight_number}' route='{self.origin}->{self.destination}' price={self.price}>"

    def __str__(self) -> str:
        return f"{self.flight_number}: {self.origin} -> {self.destination}"

class Booking:
    """Represents a passenger booking reservation for a specific flight."""
    def __init__(self, id: int, user, flight, booking_date: str, status: str):
        self.id = id
        self.user = user
        self.flight = flight
        self.booking_date = booking_date
        self.status = status

    def __repr__(self) -> str:
        return f"<Booking id={self.id} user={self.user} flight={self.flight} status='{self.status}'>"

    def __str__(self) -> str:
        return f"Booking #{self.id} ({self.status})"

class Payment:
    """Represents a payment transaction record associated with a flight booking."""
    def __init__(self, id: int, booking, amount: float, method: str, transaction_id: str, status: str):
        self.id = id
        self.booking = booking
        self.amount = amount
        self.method = method
        self.transaction_id = transaction_id
        self.status = status

    def __repr__(self) -> str:
        return f"<Payment id={self.id} amount={self.amount} method='{self.method}' status='{self.status}'>"

    def __str__(self) -> str:
        return f"Payment #{self.id} ({self.method} - ${self.amount})"

class Notification:
    """Represents a user notification generated during system events."""
    def __init__(self, id: int, user, message: str, is_read: bool, created_at: str):
        self.id = id
        self.user = user
        self.message = message
        self.is_read = is_read
        self.created_at = created_at

    def __repr__(self) -> str:
        return f"<Notification id={self.id} user={self.user} is_read={bool(self.is_read)}>"

    def __str__(self) -> str:
        return f"Notification: {self.message}"


