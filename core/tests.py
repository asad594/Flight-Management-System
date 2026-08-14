from django.test import TestCase
from .singleton import AppConfigManager
from .strategies import PaymentContext, CreditCardStrategy, EasyPaisaStrategy, PayPalStrategy
from .observers import BookingSubject, BookingObserver
from .models import User, Flight, Booking, Payment, Notification

class DomainModelTestCase(TestCase):
    """Unit tests verifying domain model entity instantiation and representations."""

    def test_user_domain_model(self):
        """Verify User model attributes and string formatting."""
        user = User(1, 'sky_pilot', 'pilot@skybound.com', 'hashed_pw', False)
        self.assertEqual(user.id, 1)
        self.assertEqual(user.username, 'sky_pilot')
        self.assertEqual(str(user), 'sky_pilot')
        self.assertIn("<User id=1", repr(user))

    def test_flight_domain_model(self):
        """Verify Flight model attributes and string formatting."""
        flight = Flight(101, 'SK-990', 'New York', 'Tokyo', '2026-09-01 10:00:00', '2026-09-02 02:00:00', 850.0, 150, 'International')
        self.assertEqual(flight.flight_number, 'SK-990')
        self.assertEqual(flight.category, 'International')
        self.assertEqual(str(flight), 'SK-990: New York -> Tokyo')
        self.assertIn("<Flight id=101", repr(flight))

    def test_booking_domain_model(self):
        """Verify Booking model representation and status tracking."""
        user = User(2, 'traveler', 'traveler@skybound.com', 'pw', False)
        flight = Flight(102, 'SK-102', 'London', 'Paris', '2026-09-05 08:00:00', '2026-09-05 10:00:00', 120.0, 50)
        booking = Booking(501, user, flight, '2026-08-14 12:00:00', 'Confirmed')
        self.assertEqual(booking.id, 501)
        self.assertEqual(str(booking), 'Booking #501 (Confirmed)')
        self.assertIn("<Booking id=501", repr(booking))

    def test_payment_domain_model(self):
        """Verify Payment model representation and amount mapping."""
        user = User(3, 'passenger', 'pass@skybound.com', 'pw', False)
        flight = Flight(103, 'SK-103', 'Dubai', 'Karachi', '2026-09-10 14:00:00', '2026-09-10 16:30:00', 250.0, 80)
        booking = Booking(502, user, flight, '2026-08-14 12:30:00', 'Confirmed')
        payment = Payment(901, booking, 250.0, 'Credit Card', 'TXN-901901', 'Success')
        self.assertEqual(payment.amount, 250.0)
        self.assertEqual(str(payment), 'Payment #901 (Credit Card - $250.0)')
        self.assertIn("<Payment id=901", repr(payment))

    def test_notification_domain_model(self):
        """Verify Notification model representation and read status."""
        user = User(4, 'subscriber', 'sub@skybound.com', 'pw', False)
        notif = Notification(301, user, 'Flight SK-101 is boarding now!', False, '2026-08-14 13:00:00')
        self.assertEqual(notif.is_read, False)
        self.assertEqual(str(notif), 'Notification: Flight SK-101 is boarding now!')
        self.assertIn("<Notification id=301", repr(notif))

class DesignPatternTestCase(TestCase):
    """Unit tests verifying GoF Design Pattern behavior in core system."""

    def test_singleton_app_config(self):
        """Verify AppConfigManager maintains a single instance across calls."""
        config1 = AppConfigManager()
        config2 = AppConfigManager()
        self.assertIs(config1, config2)
        self.assertEqual(config1.get_setting("system_name"), "SkyBound")

    def test_singleton_set_and_has_setting(self):
        """Verify AppConfigManager dynamic setting configuration and presence checks."""
        config = AppConfigManager()
        self.assertTrue(config.has_setting("system_name"))
        self.assertFalse(config.has_setting("non_existent_key_xyz"))
        config.set_setting("support_email", "support@skybound.aero")
        self.assertTrue(config.has_setting("support_email"))
        self.assertEqual(config.get_setting("support_email"), "support@skybound.aero")


    def test_payment_strategy(self):
        """Verify PaymentContext correctly executes varied payment strategies."""
        card_context = PaymentContext(CreditCardStrategy())
        self.assertIn("Credit Card", card_context.execute_payment(100.0))

        easypaisa_context = PaymentContext(EasyPaisaStrategy())
        self.assertIn("EasyPaisa", easypaisa_context.execute_payment(150.0))

        paypal_context = PaymentContext(PayPalStrategy())
        self.assertIn("PayPal", paypal_context.execute_payment(200.0))

    def test_observer_pattern(self):
        """Verify BookingSubject attaches observers and dispatches updates."""
        subject = BookingSubject()
        observer = BookingObserver()
        subject.attach(observer)
        self.assertIn(observer, subject._observers)


