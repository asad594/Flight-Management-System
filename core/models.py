class User:
    def __init__(self, id, username, email, password, is_staff):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.is_staff = is_staff

class Flight:
    def __init__(self, id, flight_number, origin, destination, departure_time, arrival_time, price, seats_available, category='Domestic'):
        self.id = id
        self.flight_number = flight_number
        self.origin = origin
        self.destination = destination
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.price = price
        self.seats_available = seats_available
        self.category = category

class Booking:
    def __init__(self, id, user, flight, booking_date, status):
        self.id = id
        self.user = user
        self.flight = flight
        self.booking_date = booking_date
        self.status = status

class Payment:
    def __init__(self, id, booking, amount, method, transaction_id, status):
        self.id = id
        self.booking = booking
        self.amount = amount
        self.method = method
        self.transaction_id = transaction_id
        self.status = status

class Notification:
    def __init__(self, id, user, message, is_read, created_at):
        self.id = id
        self.user = user
        self.message = message
        self.is_read = is_read
        self.created_at = created_at
