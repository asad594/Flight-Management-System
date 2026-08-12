import datetime
from .database import db

# ── Observer Pattern (Pure Python, no Django) ──────────────────────────────

class BookingObserver:
    """Concrete observer: writes a notification row to SQLite."""
    def update(self, user_id: int, message: str) -> None:
        """Receives notification updates and persists notification record."""
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            db.cursor.execute(
                "INSERT INTO notifications (user_id, message, is_read, created_at) VALUES (?, ?, 0, ?)",
                (user_id, message, now)
            )
            db.conn.commit()
        except Exception:
            pass  # Non-critical – never crash the booking flow


class BookingSubject:
    """Subject that manages observers and triggers notifications."""
    def __init__(self):
        self._observers = []

    def attach(self, observer: BookingObserver) -> None:
        """Registers a new observer instance."""
        self._observers.append(observer)

    def notify(self, user_id: int, message: str) -> None:
        """Notifies all registered observers of a booking event."""
        for observer in self._observers:
            observer.update(user_id, message)


# Singleton subject – ready to use across the app
booking_notifier = BookingSubject()
booking_notifier.attach(BookingObserver())
