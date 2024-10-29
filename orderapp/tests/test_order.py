import pytest
from unittest.mock import MagicMock, patch
from datetime import date
from orderapp.models.order import Order, OrderLine

@pytest.fixture(scope='function')
def mock_db_session():
    """Mock database session for testing"""
    with patch('orderapp.db.session') as mock_session:
        yield mock_session

@pytest.fixture(scope='function')
def mock_customer():
    """Create a mock customer for testing"""
    customer = MagicMock()
    customer.id = 1
    customer.type = 'private_customer'
    customer.firstname = 'Ying'
    customer.lastname = 'Zheng'
    customer.custAddress = '23 Kingsland Road, Auckland'
    return customer

@pytest.fixture(scope='function')
def mock_item():
    """Create a mock item for testing"""
    item = MagicMock()
    item.vegName = 'Carrot'
    item.price = 1.99
    item.stock = 10
    item.calculate_subtotal = lambda quantity: item.price * quantity
    item.get_price = lambda: item.price
    return item

@pytest.fixture(scope='function')
def test_order(mock_customer):
    """Create a fresh test order for each test."""
    order = Order(
        orderNumber='1001', 
        customer=mock_customer, 
        deliveryMethod='Pickup', 
        paymentMethod='Credit Card'
    )
    # Ensure order_lines is empty at the start
    order.order_lines = []
    return order

def test_order_attributes(test_order, mock_customer):
    assert test_order.orderNumber == '1001'
    assert test_order.customer == mock_customer
    assert test_order.deliveryMethod == 'Pickup'
    assert test_order.paymentMethod == 'Credit Card'
    assert test_order.orderStatus == 'Pending'
    assert test_order.orderDate == date.today()

def test_order_line(test_order, mock_item):
    order_line = OrderLine(
        order=test_order,
        item=mock_item,
        quantity=2
    )

    assert order_line.order == test_order
    assert order_line.item == mock_item
    assert order_line.quantity == 2
    assert order_line.subtotal == mock_item.calculate_subtotal(2)



