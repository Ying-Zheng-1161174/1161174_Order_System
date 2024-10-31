import pytest
from datetime import date
from unittest.mock import MagicMock, patch
from orderapp.models.payment import CreditCardPayment, DebitCardPayment, AccountPayment

@pytest.fixture(scope='function')
def mock_db_session():
    """Mock database session for testing"""
    with patch('orderapp.db.session') as mock_session:
        yield mock_session

@pytest.fixture(scope='function')
def mock_customer(mock_db_session):
    """Create a mock customer for testing"""
    customer = MagicMock()
    customer.firstname = 'Ying'
    customer.lastname = 'Zheng'
    customer.username = 'ying'
    customer.custAddress = '23 Kingsland Road, Auckland'
    customer.custBalance = 0.0
    customer.maxOwing = 100.0
    mock_db_session.add(customer)
    mock_db_session.commit()
    return customer

@pytest.fixture(scope='function')
def mock_order(mock_db_session):
    """Create a mock order for testing"""
    order = MagicMock()
    order.order_id = 1
    order.deliveryMethod = 'Delivery'
    order.orderStatus = 'Completed'
    order.paymentMethod = 'Credit Card'
    mock_db_session.add(order)
    mock_db_session.commit()
    return order

def test_credit_card_payment(mock_db_session, mock_customer, mock_order):
    """Test credit card payment"""
    credit_card_payment = CreditCardPayment(
        paymentAmount=100.00,
        customer=mock_customer,
        order=mock_order,
        cardExpiryDate=date(2025, 1, 1),
        cardNumber='1234567890123456',
        cardType='Visa'
    )

    mock_db_session.add(credit_card_payment)
    mock_db_session.commit()

    assert credit_card_payment.cardExpiryDate == date(2025, 1, 1)
    assert credit_card_payment.cardNumber == '1234567890123456'
    assert credit_card_payment.cardType == 'Visa'

def test_debit_card_payment(mock_db_session, mock_customer, mock_order):
    """Test debit card payment"""
    debit_card_payment = DebitCardPayment(
        paymentAmount=100.00,
        customer=mock_customer,
        order=mock_order,
        bankName='ASB',
        debitCardNumber='1234567890123456'
    )

    mock_db_session.add(debit_card_payment)
    mock_db_session.commit()

    assert debit_card_payment.bankName == 'ASB'
    assert debit_card_payment.debitCardNumber == '1234567890123456'

def test_account_payment(mock_db_session, mock_customer, mock_order):
    """Test account payment"""
    account_payment = AccountPayment(
        paymentAmount=100.00,
        customer=mock_customer,
        order=mock_order
    )

    mock_db_session.add(account_payment)
    mock_db_session.commit()

    assert account_payment.paymentAmount == 100.00
    assert account_payment.customer == mock_customer
    assert account_payment.order == mock_order
    assert account_payment.customer
