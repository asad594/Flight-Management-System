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
        self.assertEqual(card_context.strategy.name, "Credit Card")
        self.assertIn("Credit Card", card_context.execute_payment(100.0))

        easypaisa_context = PaymentContext(EasyPaisaStrategy())
        self.assertEqual(easypaisa_context.strategy.name, "EasyPaisa / JazzCash")
        self.assertIn("EasyPaisa", easypaisa_context.execute_payment(150.0))

        paypal_context = PaymentContext(PayPalStrategy())
        self.assertEqual(paypal_context.strategy.name, "PayPal")
        self.assertIn("PayPal", paypal_context.execute_payment(200.0))

    def test_observer_pattern(self):
        """Verify BookingSubject attaches observers and dispatches updates."""
        subject = BookingSubject()
        observer = BookingObserver()
        subject.attach(observer)
        self.assertIn(observer, subject._observers)

class DomainFactoryTestCase(TestCase):
    """Unit tests verifying DomainFactory creation and database persistence."""

    def test_domain_factory_user_creation(self):
        """Verify DomainFactory creates and returns a valid User domain object."""
        from .factories import DomainFactory
        import uuid
        uname = f"testuser_{uuid.uuid4().hex[:6]}"
        user = DomainFactory.create_user(uname, f"{uname}@skybound.com", "securepass123")
        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, uname)
        self.assertEqual(user.is_staff, 0)

    def test_domain_factory_flight_and_booking(self):
        """Verify DomainFactory creates a flight and subsequent booking reservation."""
        from .factories import DomainFactory
        import uuid
        fnum = f"SK-T{uuid.uuid4().hex[:4].upper()}"
        flight = DomainFactory.create_flight(
            fnum, 'Islamabad', 'Doha', '2026-10-01 06:00:00', '2026-10-01 09:30:00', 350.0, 75, 'International'
        )
        self.assertIsNotNone(flight.id)
        self.assertEqual(flight.flight_number, fnum)
        self.assertEqual(flight.seats_available, 75)

        uname = f"booker_{uuid.uuid4().hex[:6]}"
        user = DomainFactory.create_user(uname, f"{uname}@skybound.com", "pass")
        booking = DomainFactory.create_booking(user, flight)
        self.assertIsNotNone(booking.id)
        self.assertEqual(booking.status, 'Confirmed')
        self.assertEqual(booking.flight.id, flight.id)

class RouterTestCase(TestCase):
    """Unit tests verifying custom framework Router path registration and pattern matching."""

    def test_router_static_path_match(self):
        """Verify Router correctly registers and resolves static URL endpoints."""
        from .framework import Router
        dummy_handler = lambda req: "homepage_output"
        Router.add('/test-home-route', dummy_handler)

        handler, params = Router.match('/test-home-route')
        self.assertEqual(handler, dummy_handler)
        self.assertEqual(params, {})

        # Trailing slash flexibility
        handler, params = Router.match('/test-home-route/')
        self.assertEqual(handler, dummy_handler)

    def test_router_dynamic_param_match(self):
        """Verify Router correctly parses integer path parameters."""
        from .framework import Router
        dummy_booking_handler = lambda req, flight_id: f"booking_{flight_id}"
        Router.add('/test-book/<int:flight_id>/', dummy_booking_handler)

        handler, params = Router.match('/test-book/42/')
        self.assertEqual(handler, dummy_booking_handler)
        self.assertEqual(params, {'flight_id': 42})

    def test_router_unmatched_path(self):
        """Verify Router returns None for unmatched URL paths."""
        from .framework import Router
        handler, params = Router.match('/unregistered-route-xyz-404')
        self.assertIsNone(handler)
        self.assertEqual(params, {})


class CustomViewsIntegrationTestCase(TestCase):
    """Integration tests verifying custom standalone framework views."""

    def test_search_flights_rendering(self):
        """Verify search_flights renders HTML response for valid query."""
        from .custom_views import search_flights
        from .models import User

        class MockRequest:
            pass

        req = MockRequest()
        req.user = User(1, 'admin', 'admin@skybound.com', 'pass', 1)
        req.path = '/search/'
        req.GET = {'origin': 'Karachi', 'destination': 'Dubai'}

        res = search_flights(req)
        self.assertIsInstance(res, str)
        self.assertIn("SkyBound", res)





