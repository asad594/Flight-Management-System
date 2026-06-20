from abc import ABC, abstractmethod

class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount):
        pass

class CreditCardStrategy(PaymentStrategy):
    def pay(self, amount):
        return f"Paid {amount} using Credit Card."

class EasyPaisaStrategy(PaymentStrategy):
    def pay(self, amount):
        return f"Paid {amount} using EasyPaisa/JazzCash."

class PayPalStrategy(PaymentStrategy):
    def pay(self, amount):
        return f"Paid {amount} using PayPal Mock."

class PaymentContext:
    def __init__(self, strategy: PaymentStrategy):
        self._strategy = strategy

    def execute_payment(self, amount):
        return self._strategy.pay(amount)
