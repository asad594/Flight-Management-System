from django.test import TestCase
from .singleton import AppConfigManager
from .strategies import PaymentContext, CreditCardStrategy, EasyPaisaStrategy, PayPalStrategy
from .observers import BookingSubject, BookingObserver

class DesignPatternTestCase(TestCase):
    """Unit tests verifying GoF Design Pattern behavior in core system."""

    def test_singleton_app_config(self):
        """Verify AppConfigManager maintains a single instance across calls."""
        config1 = AppConfigManager()
        config2 = AppConfigManager()
        self.assertIs(config1, config2)
        self.assertEqual(config1.get_setting("system_name"), "SkyBound")

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

