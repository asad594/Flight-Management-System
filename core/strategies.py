from abc import ABC, abstractmethod

class PaymentStrategy(ABC):
    """Abstract Base Class defining the strategy interface for processing payments."""
    @abstractmethod
    def pay(self, amount: float) -> str:
        """Processes payment of a specific amount."""
        pass

class CreditCardStrategy(PaymentStrategy):
    """Concrete strategy for credit card payments."""
    def pay(self, amount: float) -> str:
        return f"Paid {amount} using Credit Card."

class EasyPaisaStrategy(PaymentStrategy):
    """Concrete strategy for EasyPaisa / JazzCash payments."""
    def pay(self, amount: float) -> str:
        return f"Paid {amount} using EasyPaisa/JazzCash."

class PayPalStrategy(PaymentStrategy):
    """Concrete strategy for PayPal payments."""
    def pay(self, amount: float) -> str:
        return f"Paid {amount} using PayPal Mock."

class PaymentContext:
    """Context class that executes a payment through an injected PaymentStrategy."""
    def __init__(self, strategy: PaymentStrategy):
        self._strategy = strategy

    def execute_payment(self, amount: float) -> str:
        """Delegates payment processing to the configured strategy."""
        return self._strategy.pay(amount)

