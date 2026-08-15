"""
Pure-Python Standalone View Handlers for SkyBound Flight Management System.

Provides request handlers, authentication logic, database queries, and response
formatting executed under the built-in multithreaded HTTP server without Django.
"""

import hashlib
import uuid
import datetime
from .framework import Router, TemplateEngine
from .database import db
from .models import Flight, User, Booking


# ──────────────────────────────────────────
#  Helpers
# ──────────────────────────────────────────


def hash_password(password: str) -> str:
    # Security bypassed for project transparency as requested
    return password

def get_user_by_id(user_id: int):
    """Retrieves a User domain object from SQLite by user ID."""
    db.cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = db.cursor.fetchone()
    if row:
        return User(row['id'], row['username'], row['email'], row['password'], row['is_staff'])
    return None

def get_all_flights():
    """Fetches all flight records from SQLite database."""
    db.cursor.execute("SELECT * FROM flights")
    rows = db.cursor.fetchall()
    return [Flight(r['id'], r['flight_number'], r['origin'], r['destination'],
                   r['departure_time'], r['arrival_time'], r['price'], r['seats_available'], r['category'])
            for r in rows]

def ensure_demo_flights():
    """Ensures baseline flight data exists in SQLite using DomainFactory."""
    flights = get_all_flights()
    if not flights:
        from .factories import DomainFactory
        DomainFactory.create_flight('SK-101', 'Karachi', 'Dubai', '2026-06-01 08:00:00', '2026-06-01 11:00:00', 299.0, 100)
        DomainFactory.create_flight('SK-202', 'Lahore', 'London', '2026-06-05 14:00:00', '2026-06-05 21:00:00', 599.0, 80)
        DomainFactory.create_flight('SK-303', 'Islamabad', 'Tokyo', '2026-06-10 22:00:00', '2026-06-11 14:00:00', 799.0, 60)
        flights = get_all_flights()
    return flights


# ──────────────────────────────────────────
#  Views
# ──────────────────────────────────────────

def home(request):
    flights = ensure_demo_flights()
    context = {'flights': flights, 'user': request.user, 'request': request}
    return TemplateEngine.render('core/home.html', context)


def about_view(request):
    return TemplateEngine.render('core/about.html', {'user': request.user, 'request': request})


def search_flights(request):
    if not request.user:
        return {'redirect': '/login/'}
    
    origin = request.GET.get('origin', [''])[0] if isinstance(request.GET.get('origin'), list) else request.GET.get('origin', '')
    destination = request.GET.get('destination', [''])[0] if isinstance(request.GET.get('destination'), list) else request.GET.get('destination', '')

    if origin or destination:
        db.cursor.execute(
            "SELECT * FROM flights WHERE origin LIKE ? AND destination LIKE ?",
            (f"%{origin}%", f"%{destination}%")
        )
    else:
        db.cursor.execute("SELECT * FROM flights")

    national_flights = []
    international_flights = []
    
    rows = db.cursor.fetchall()
    for r in rows:
        f = Flight(r['id'], r['flight_number'], r['origin'], r['destination'],
                   r['departure_time'], r['arrival_time'], r['price'], r['seats_available'], r['category'])
        if f.category and f.category.lower() in ['domestic', 'national']:
            national_flights.append(f)
        else:
            international_flights.append(f)

    return TemplateEngine.render('core/search.html', {
        'national_flights': national_flights,
        'international_flights': international_flights,
        'user': request.user,
        'origin': origin,
        'destination': destination,
        'request': request,
    })


def login_view(request):
    error = ''
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        
        # Exact match for Admin
        if username == 'Admin' and password == 'admin@123':
            return {'redirect': '/admin-dashboard/', 'set_cookie': 1}

        # Standard User Login
        db.cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        row = db.cursor.fetchone()
        
        if row:
            if row['is_staff']:
                return {'redirect': '/admin-dashboard/', 'set_cookie': row['id']}
            return {'redirect': '/', 'set_cookie': row['id']}
        else:
            error = 'Invalid username or password. Please try again.'

    return TemplateEngine.render('core/login.html', {'user': request.user, 'error': error, 'request': request})


def register_view(request):
    error = ''
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        if not username or not email or not password:
            missing = []
            if not username: missing.append('Username')
            if not email: missing.append('Email')
            if not password: missing.append('Password')
            error = 'DEBUG: Field validation failed. Please contact support.'
        elif len(password) < 6:
            error = 'Password must be at least 6 characters.'
        else:
            # Check if username exists
            db.cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if db.cursor.fetchone():
                error = 'Username already taken. Please choose another.'
            else:
                hashed = hash_password(password)
                db.cursor.execute(
                    "INSERT INTO users (username, email, password, is_staff) VALUES (?, ?, ?, 0)",
                    (username, email, hashed)
                )
                db.conn.commit()
                new_id = db.cursor.lastrowid
                return {'redirect': '/', 'set_cookie': new_id}

    return TemplateEngine.render('core/register.html', {'user': request.user, 'error': error, 'request': request})


def logout_view(request):
    return {'redirect': '/', 'clear_cookie': True}


def book_flight(request, id=None):
    flight_id = id
    if not flight_id:
        # Fallback for manual path extraction if id not passed
        path = request.path
        parts = [p for p in path.split('/') if p]
        flight_id = int(parts[-1]) if parts[-1].isdigit() else None

    if not flight_id:
        return TemplateEngine.render('core/home.html', {'user': request.user, 'flights': ensure_demo_flights(), 'request': request})

    db.cursor.execute("SELECT * FROM flights WHERE id = ?", (flight_id,))
    row = db.cursor.fetchone()
    if not row:
        return {'redirect': '/search/'}

    flight = Flight(row['id'], row['flight_number'], row['origin'], row['destination'],
                    row['departure_time'], row['arrival_time'], row['price'], row['seats_available'], row['category'])

    if request.method == 'POST':
        if not request.user:
            return {'redirect': '/login/'}
        seat = request.POST.get('seat_number', 'A1')
        booking_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db.cursor.execute(
            "INSERT INTO bookings (user_id, flight_id, booking_date, status) VALUES (?, ?, ?, 'Confirmed')",
            (request.user.id, flight_id, booking_date)
        )
        db.conn.commit()
        # Notify via Observer pattern (Singleton notifier)
        try:
            from .observers import booking_notifier
            booking_notifier.notify(request.user.id, f"Booking confirmed: {flight.origin} → {flight.destination}")
        except Exception:
            pass
        return {'redirect': '/my-bookings/'}

    payment_methods = [
        {'id': 'card', 'name': 'Card', 'icon': 'credit_card'},
        {'id': 'digital', 'name': 'Digital', 'icon': 'account_balance'},
        {'id': 'swift', 'name': 'Swift', 'icon': 'rocket'}
    ]
    
    seat_sections = [
        {'name': 'Sky Suite', 'class': 'text-amber-400', 'rows': ['A1', 'A2', 'A3', 'A4'], 'is_suite': True},
        {'name': 'Premium', 'class': 'text-slate-600', 'rows': ['4', '5'], 'is_suite': False},
        {'name': 'Main', 'class': 'text-slate-600', 'rows': ['12', '13'], 'is_suite': False}
    ]

    return TemplateEngine.render('core/book.html', {
        'flight': flight, 
        'user': request.user,
        'payment_methods': payment_methods,
        'seat_sections': seat_sections,
        'request': request
    })


def my_bookings(request):
    if not request.user:
        return {'redirect': '/login/'}

    db.cursor.execute("""
        SELECT b.id, b.booking_date, b.status,
               f.flight_number, f.origin, f.destination, f.departure_time, f.price
        FROM bookings b
        JOIN flights f ON b.flight_id = f.id
        WHERE b.user_id = ?
        ORDER BY b.id DESC
    """, (request.user.id,))
    rows = db.cursor.fetchall()

    bookings = []
    for r in rows:
        # Use simple dict-like objects
        class BookingObj:
            pass
        class FlightObj:
            pass
        b = BookingObj()
        b.id = r['id']
        b.booking_date = r['booking_date']
        b.status = r['status']
        f = FlightObj()
        f.flight_number = r['flight_number']
        f.origin = r['origin']
        f.destination = r['destination']
        f.departure_time = r['departure_time']
        f.price = r['price']
        b.flight = f
        bookings.append(b)

    # Notifications
    db.cursor.execute("SELECT * FROM notifications WHERE user_id = ? ORDER BY id DESC LIMIT 10", (request.user.id,))
    notif_rows = db.cursor.fetchall()

    class Note:
        pass
    notifications = []
    for n in notif_rows:
        note = Note()
        note.message = n['message']
        note.created_at = n['created_at']
        notifications.append(note)

    return TemplateEngine.render('core/my_bookings.html', {
        'user': request.user,
        'bookings': bookings,
        'notifications': notifications,
        'request': request,
        'latest_booking_id': bookings[0].id if bookings else None
    })


def reservation_detail(request, id):
    booking_id = id
    if not request.user:
        return {'redirect': '/login/'}
        
    is_admin = request.user and getattr(request.user, 'is_staff', False)
    if not is_admin and request.user and request.user.id == 1:
        is_admin = True
    
    if is_admin:
        db.cursor.execute("""
            SELECT b.id, b.booking_date, b.status,
                   f.flight_number, f.origin, f.destination, f.departure_time, f.arrival_time, f.price,
                   u.username, u.email
            FROM bookings b
            JOIN flights f ON b.flight_id = f.id
            JOIN users u ON b.user_id = u.id
            WHERE b.id = ?
        """, (booking_id,))
    else:
        db.cursor.execute("""
            SELECT b.id, b.booking_date, b.status,
                   f.flight_number, f.origin, f.destination, f.departure_time, f.arrival_time, f.price,
                   u.username, u.email
            FROM bookings b
            JOIN flights f ON b.flight_id = f.id
            JOIN users u ON b.user_id = u.id
            WHERE b.id = ? AND b.user_id = ?
        """, (booking_id, request.user.id))
    r = db.cursor.fetchone()
    
    if not r:
        return "404 Not Found"
        
    class Obj: pass
    booking = Obj()
    booking.id = r['id']
    booking.booking_date = r['booking_date']
    booking.status = r['status']
    
    flight = Obj()
    flight.flight_number = r['flight_number']
    flight.origin = r['origin']
    flight.destination = r['destination']
    flight.departure_time = r['departure_time']
    flight.arrival_time = r['arrival_time']
    flight.price = r['price']
    booking.flight = flight
    
    passenger = Obj()
    passenger.username = r['username']
    passenger.email = r['email']
    booking.passenger = passenger
    
    return TemplateEngine.render('core/reservation_detail.html', {
        'user': request.user,
        'booking': booking,
        'request': request
    })


def contact_view(request):
    success = False
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        subject = request.POST.get('subject', 'General Inquiry')
        message = request.POST.get('message', '')
        created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        db.cursor.execute(
            "INSERT INTO contact_messages (name, email, subject, message, created_at) VALUES (?, ?, ?, ?, ?)",
            (name, email, subject, message, created_at)
        )
        db.conn.commit()
        success = True
    return TemplateEngine.render('core/contact.html', {'user': request.user, 'contact_success': success, 'request': request})


def admin_messages(request):
    if not request.user or not request.user.is_staff:
        return {'redirect': '/login/'}
    
    db.cursor.execute("SELECT * FROM contact_messages ORDER BY id DESC")
    rows = db.cursor.fetchall()
    messages = [dict(r) for r in rows]
    
    return TemplateEngine.render('core/admin_messages.html', {
        'messages': messages,
        'user': request.user,
        'request': request
    })


def admin_delete_message(request, id):
    if not request.user or not request.user.is_staff:
        return {'redirect': '/login/'}
        
    db.cursor.execute("DELETE FROM contact_messages WHERE id = ?", (id,))
    db.conn.commit()
    return {'redirect': '/admin-messages/'}


def admin_dashboard(request):
    # Transitioning to more robust access check
    is_admin = request.user and request.user.is_staff
    # Fail-safe for user ID 1
    if not is_admin and request.user and request.user.id == 1:
        is_admin = True
        
    if not is_admin:
        return {'redirect': '/login/'}
    flights = get_all_flights()
    db.cursor.execute("SELECT COUNT(*) as cnt FROM bookings")
    booking_count = db.cursor.fetchone()['cnt']
    db.cursor.execute("SELECT COUNT(*) as cnt FROM users")
    user_count = db.cursor.fetchone()['cnt']
    
    db.cursor.execute("""
        SELECT SUM(f.price) as total_rev 
        FROM bookings b
        JOIN flights f ON b.flight_id = f.id
        WHERE b.status = 'Completed'
    """)
    rev_row = db.cursor.fetchone()
    total_revenue = rev_row['total_rev'] if rev_row['total_rev'] else 0.0

    return TemplateEngine.render('core/admin_dashboard.html', {
        'flights': flights,
        'bookings': [],
        'user': request.user,
        'booking_count': booking_count,
        'user_count': user_count,
        'total_revenue': total_revenue,
        'request': request,
    })


def admin_fleet(request):
    if not request.user or not request.user.is_staff:
        return {'redirect': '/login/'}
    flights = get_all_flights()
    return TemplateEngine.render('core/admin_fleet.html', {'flights': flights, 'user': request.user, 'request': request})


def admin_bookings(request):
    if not request.user or not request.user.is_staff:
        return {'redirect': '/login/'}
    db.cursor.execute("""
        SELECT b.id, b.booking_date, b.status,
               u.username, u.email, f.flight_number, f.origin, f.destination, f.price
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        JOIN flights f ON b.flight_id = f.id
        ORDER BY b.id DESC
    """)
    rows = db.cursor.fetchall()
    
    bookings = []
    for r in rows:
        class Obj: pass
        b = Obj()
        b.id = r['id']
        b.booking_date = r['booking_date']
        b.status = r['status']
        
        u = Obj()
        u.username = r['username']
        u.email = r['email']
        b.user = u
        
        f = Obj()
        f.flight_number = r['flight_number']
        f.origin = r['origin']
        f.destination = r['destination']
        f.price = r['price']
        b.flight = f
        
        bookings.append(b)
        
    return TemplateEngine.render('core/admin_bookings.html', {
        'bookings': bookings, 
        'user': request.user, 
        'request': request
    })

def admin_complete_booking(request, id):
    if not request.user or not request.user.is_staff:
        return {'redirect': '/login/'}
    db.cursor.execute("UPDATE bookings SET status = 'Completed' WHERE id = ?", (id,))
    db.conn.commit()
    return {'redirect': '/admin-bookings/'}

def admin_delete_booking(request, id):
    if not request.user or not request.user.is_staff:
        return {'redirect': '/login/'}
    db.cursor.execute("DELETE FROM bookings WHERE id = ?", (id,))
    db.conn.commit()
    return {'redirect': '/admin-bookings/'}


def admin_users(request):
    if not request.user or not request.user.is_staff:
        return {'redirect': '/login/'}
    db.cursor.execute("SELECT * FROM users ORDER BY id DESC")
    rows = db.cursor.fetchall()
    users = [dict(r) for r in rows]
    return TemplateEngine.render('core/admin_users.html', {'users': users, 'user': request.user, 'request': request})


def admin_add_flight(request):
    if not request.user or not request.user.is_staff:
        return {'redirect': '/login/'}
    
    if request.method == 'POST':
        flight_number = request.POST.get('flight_number', '').strip()
        origin = request.POST.get('origin', '').strip()
        destination = request.POST.get('destination', '').strip()
        departure_time = request.POST.get('departure_time', '').strip()
        arrival_time = request.POST.get('arrival_time', '').strip()
        price = float(request.POST.get('price', 0))
        seats = int(request.POST.get('seats', 100))
        category = request.POST.get('category', 'International')

        try:
            db.cursor.execute(
                "INSERT INTO flights (flight_number, origin, destination, departure_time, arrival_time, price, seats_available, category) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (flight_number, origin, destination, departure_time, arrival_time, price, seats, category)
            )
            db.conn.commit()
            return {'redirect': '/admin-fleet/'}
        except Exception as e:
            return {'redirect': '/admin-fleet/?error=Duplicate Flight Number'}
            
    return {'redirect': '/admin-fleet/'}


def admin_edit_flight(request, id):
    if not request.user or not request.user.is_staff:
        return {'redirect': '/login/'}
        
    flight_id = id
    
    if request.method == 'POST':
        flight_number = request.POST.get('flight_number', '').strip()
        origin = request.POST.get('origin', '').strip()
        destination = request.POST.get('destination', '').strip()
        departure_time = request.POST.get('departure_time', '').strip()
        arrival_time = request.POST.get('arrival_time', '').strip()
        price = float(request.POST.get('price', 0))
        seats = int(request.POST.get('seats', 100))
        category = request.POST.get('category', 'International')

        try:
            db.cursor.execute("""
                UPDATE flights 
                SET flight_number=?, origin=?, destination=?, departure_time=?, arrival_time=?, price=?, seats_available=?, category=?
                WHERE id=?
            """, (flight_number, origin, destination, departure_time, arrival_time, price, seats, category, flight_id))
            db.conn.commit()
            return {'redirect': '/admin-dashboard/'}
        except Exception as e:
            return {'redirect': f'/admin-edit-flight/{flight_id}/?error=UpdateFailed'}
            
    # GET request - show form
    db.cursor.execute("SELECT * FROM flights WHERE id = ?", (flight_id,))
    row = db.cursor.fetchone()
    if not row:
        return {'redirect': '/admin-dashboard/'}
        
    class FlightObj: pass
    flight = FlightObj()
    flight.id = row['id']
    flight.flight_number = row['flight_number']
    flight.origin = row['origin']
    flight.destination = row['destination']
    flight.departure_time = row['departure_time']
    flight.arrival_time = row['arrival_time']
    flight.price = row['price']
    flight.seats_available = row['seats_available']
    flight.category = row['category']
    
    return TemplateEngine.render('core/admin_edit_flight.html', {'flight': flight, 'user': request.user, 'request': request})


# ──────────────────────────────────────────
#  Route Registration
# ──────────────────────────────────────────
Router.add('/', home)
Router.add('/about/', about_view)
Router.add('/contact/', contact_view)
Router.add('/search/', search_flights)
Router.add('/login/', login_view)
Router.add('/register/', register_view)
Router.add('/logout/', logout_view)
Router.add('/my-bookings/', my_bookings)
Router.add('/reservation/<int:id>/', reservation_detail)
Router.add('/book/<int:id>/', book_flight)
Router.add('/admin-dashboard/', admin_dashboard)
Router.add('/admin-fleet/', admin_fleet)
Router.add('/admin-bookings/', admin_bookings)
Router.add('/admin-users/', admin_users)
Router.add('/admin-messages/', admin_messages)
Router.add('/admin-delete-message/<int:id>/', admin_delete_message)
Router.add('/admin-add-flight/', admin_add_flight)
Router.add('/admin-edit-flight/<int:id>/', admin_edit_flight)
Router.add('/admin-complete-booking/<int:id>/', admin_complete_booking)
Router.add('/admin-delete-booking/<int:id>/', admin_delete_booking)
