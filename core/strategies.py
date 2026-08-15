"""
Strategy Pattern Module for SkyBound Flight Management System.

Provides interchangeable payment processing algorithms adhering to a common
abstract interface, allowing the checkout flow to dynamically switch between
Credit Card, EasyPaisa/JazzCash, and PayPal strategies at runtime.
"""

from abc import ABC, abstractmethod


class PaymentStrategy(ABC):
    """
    Abstract Base Class defining the strategy interface for processing payments.

    All concrete payment gateway strategies must implement the name property
    and the pay execution method.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable provider identifier for the payment strategy."""
        pass

    @abstractmethod
    def pay(self, amount: float) -> str:
        """
        Processes payment of a specified currency amount.

        Args:
            amount: The total financial amount to be billed.

        Returns:
            A transaction confirmation message string.
        """
        pass


class CreditCardStrategy(PaymentStrategy):
    """
    Concrete payment strategy for credit/debit card transactions.

    Simulates card processing with merchant bank authorization.
    """

    @property
    def name(self) -> str:
        """Returns the human-readable gateway identifier."""
        return "Credit Card"

    def pay(self, amount: float) -> str:
        """
        Executes credit card payment processing.

        Args:
            amount: The total financial amount to charge.

        Returns:
            Formatted payment confirmation message.
        """
        return f"Paid {amount} using Credit Card."


class EasyPaisaStrategy(PaymentStrategy):
    """
    Concrete payment strategy for EasyPaisa / JazzCash mobile wallet transactions.

    Handles digital wallet mock authorizations.
    """

    @property
    def name(self) -> str:
        """Returns the human-readable gateway identifier."""
        return "EasyPaisa / JazzCash"

    def pay(self, amount: float) -> str:
        """
        Executes mobile wallet payment processing.

        Args:
            amount: The total financial amount to charge.

        Returns:
            Formatted payment confirmation message.
        """
        return f"Paid {amount} using EasyPaisa/JazzCash."


class PayPalStrategy(PaymentStrategy):
    """
    Concrete payment strategy for PayPal gateway transactions.

    Simulates express checkout and account authorization.
    """

    @property
    def name(self) -> str:
        """Returns the human-readable gateway identifier."""
        return "PayPal"

    def pay(self, amount: float) -> str:
        """
        Executes PayPal payment processing.

        Args:
            amount: The total financial amount to charge.

        Returns:
            Formatted payment confirmation message.
        """
        return f"Paid {amount} using PayPal Mock."


class PaymentContext:
    """
    Context class that executes a payment through an injected PaymentStrategy.

    Decouples the billing client code from specific payment gateway implementations.
    """

    def __init__(self, strategy: PaymentStrategy):
        """
        Initializes the context with an initial payment strategy.

        Args:
            strategy: An instance conforming to the PaymentStrategy interface.
        """
        self._strategy: PaymentStrategy = strategy

    @property
    def strategy(self) -> PaymentStrategy:
        """Returns the currently active payment strategy instance."""
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: PaymentStrategy) -> None:
        """Allows dynamic switching of the payment strategy at runtime."""
        self._strategy = strategy

    def execute_payment(self, amount: float) -> str:
        """
        Delegates payment processing to the configured strategy.

        Args:
            amount: The total financial amount to charge.

        Returns:
            Confirmation message from the underlying payment strategy.
        """
        return self._strategy.pay(amount)



