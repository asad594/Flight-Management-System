"""
Observer Pattern Module for SkyBound Flight Management System.

Implements an event-driven notification dispatch mechanism. When a booking
or reservation status changes, the BookingSubject dispatches updates to
all registered observers (such as BookingObserver) without coupling the
business layer to concrete persistence or messaging logic.
"""

import datetime
from typing import List
from .database import db


class BookingObserver:
    """
    Concrete observer responsible for persisting notifications to SQLite.

    Listens for event emissions triggered by the subject and records
    a notification entry associated with the respective user.
    """

    def update(self, user_id: int, message: str) -> None:
        """
        Receives notification updates from the subject and persists them safely.

        Args:
            user_id: ID of the user receiving the notification.
            message: Informational message content describing the booking event.
        """
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            db.cursor.execute(
                "INSERT INTO notifications (user_id, message, is_read, created_at) VALUES (?, ?, 0, ?)",
                (user_id, message, now)
            )
            db.conn.commit()
        except Exception:
            # Non-critical operation – prevent logging/notification failures from halting the transaction
            pass


class BookingSubject:
    """
    Subject (Publisher) managing observer registration and event notifications.

    Maintains a list of observers and broadcasts state change events to all subscribers.
    """

    def __init__(self) -> None:
        """Initializes the subject with an empty list of registered observers."""
        self._observers: List[BookingObserver] = []

    def attach(self, observer: BookingObserver) -> None:
        """
        Registers a new observer instance with the subject.

        Args:
            observer: An observer instance implementing the update method.
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: BookingObserver) -> None:
        """
        Unregisters an observer instance from the subject.

        Args:
            observer: The observer instance to remove.
        """
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, user_id: int, message: str) -> None:
        """
        Notifies all registered observers of an event.

        Args:
            user_id: ID of the user targeted by the notification.
            message: Message payload describing the event.
        """
        for observer in self._observers:
            observer.update(user_id, message)


# Singleton subject ready for application-wide notification events
booking_notifier = BookingSubject()
booking_notifier.attach(BookingObserver())

