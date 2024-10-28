from orderapp import db
from sqlalchemy import Boolean, Column, Integer, String, Float, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import date
from orderapp.models.order import Order

class Payment(db.Model):
    """
    Base class for all payment types.
    """
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True)
    paymentAmount = Column(Float, nullable=False)
    paymentDate = Column(Date, nullable=False, default=date.today)
    type = Column(String(50))

    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    customer = relationship("Customer", back_populates="payments")

    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False, unique=True)
    order = relationship('Order', back_populates='payment')

    __mapper_args__ = {
        'polymorphic_identity': 'payment',
        'polymorphic_on': type
    }
    
    def __init__(self, paymentAmount, customer, order):
        self.paymentAmount = paymentAmount
        self.customer = customer
        self.order = order

class CreditCardPayment(Payment):
    """
    Subclass for credit card payments.
    """
    __tablename__ = 'credit_card_payments'

    id = Column(Integer, ForeignKey('payments.id'), primary_key=True)
    cardExpiryDate = Column(Date, nullable=False)
    cardNumber = Column(String(16), nullable=False)
    cardType = Column(String(50), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'credit_card_payment',
    }

    def __init__(self, paymentAmount, customer, order, cardExpiryDate, cardNumber, cardType):
        super().__init__(paymentAmount, customer, order)
        self.cardExpiryDate = cardExpiryDate
        self.cardNumber = cardNumber
        self.cardType = cardType

class DebitCardPayment(Payment):
    """
    Subclass for debit card payments.
    """
    __tablename__ = 'debit_card_payments'

    id = Column(Integer, ForeignKey('payments.id'), primary_key=True)
    bankName = Column(String(100), nullable=False)
    debitCardNumber = Column(String(16), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'debit_card_payment',
    }

    def __init__(self, paymentAmount, customer, order, bankName, debitCardNumber):
        super().__init__(paymentAmount, customer, order)
        self.bankName = bankName
        self.debitCardNumber = debitCardNumber

class AccountPayment(Payment):
    """
    Subclass for account payments.
    """
    __tablename__ = 'account_payments'

    id = Column(Integer, ForeignKey('payments.id'), primary_key=True)  

    __mapper_args__ = {
        'polymorphic_identity': 'account_payment',
    }

    def __init__(self, paymentAmount, customer, order):
        super().__init__(paymentAmount, customer, order)
    
    def process_payment(self):
        """
        Process the payment by adding the payment amount to the customer's balance.
        """
        self.customer.add_to_balance(self.paymentAmount)
        return True

