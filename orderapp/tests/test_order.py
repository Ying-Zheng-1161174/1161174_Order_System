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
def test_order(mock_customer, mock_db_session):
    """Create a test order and add it to the database."""
    order = Order(
        orderNumber='1001', 
        customer=mock_customer, 
        deliveryMethod='Pickup', 
        paymentMethod='Credit Card'
    )
    mock_db_session.add(order)
    mock_db_session.commit()
    return order

def test_order_attributes(test_order, mock_customer):
    """Test order attributes"""
    assert test_order.orderNumber == '1001'
    assert test_order.customer == mock_customer
    assert test_order.deliveryMethod == 'Pickup'
    assert test_order.paymentMethod == 'Credit Card'
    assert test_order.orderStatus == 'Pending'
    assert test_order.orderDate == date.today()

def test_order_line(test_order, mock_item, mock_db_session):
    """Test order line attributes"""
    order_line = OrderLine(
        order=test_order,
        item=mock_item,
        quantity=2
    )
    mock_db_session.add(order_line)
    mock_db_session.commit()

    assert order_line.order == test_order
    assert order_line.item == mock_item
    assert order_line.quantity == 2
    assert order_line.subtotal == mock_item.calculate_subtotal(2)

def test_add_item(test_order, mock_item, mock_db_session):
    """Test adding an item to the order lines list"""
    mock_db_session.reset_mock()
    test_order.add_item(mock_item, 2)
    
    # Test order line was created correctly
    assert len(test_order.order_lines) == 1
    assert test_order.order_lines[0].item == mock_item
    assert test_order.order_lines[0].quantity == 2
    assert test_order.order_lines[0].subtotal == mock_item.calculate_subtotal(2)

    # Verify database interactions
    assert mock_db_session.add.call_count == 1
    mock_db_session.add.assert_called_once_with(test_order.order_lines[0])
    mock_db_session.commit.assert_called_once()

def test_add_item_insufficient_stock(test_order, mock_item):
    """Test adding an item with insufficient stock"""
    mock_item.stock = 1  # Set stock lower than requested quantity
    
    with pytest.raises(ValueError) as exc_info:
        test_order.add_item(mock_item, 2)
    
    assert str(exc_info.value) == "Not enough stock. Available: 1, Requested: 2"
    # Verify no order line was added
    assert len(test_order.order_lines) == 0  

def test_update_stock(test_order, mock_item, mock_db_session):
    """Test updating the stock of items after receiving the payment"""
    test_order.add_item(mock_item, 2)
    mock_db_session.reset_mock() 
    
    test_order.update_stock()

    # Verify database interactions
    assert mock_item.stock == 8
    mock_db_session.add.assert_called_once_with(mock_item)
    mock_db_session.commit.assert_called_once()

def test_private_customer_pickup_calculate_total(test_order, mock_item):
    """Test calculating the total price of the order for private customer pickup"""
    order_lines = [OrderLine(order=test_order, item=mock_item, quantity=2)]
    test_order.order_lines = order_lines

    assert test_order.calculate_total() == 3.98

def test_private_customer_delivery_calculate_total(test_order, mock_item):
    """Test calculating the total price of the order for private customer delivery"""
    test_order.deliveryMethod = 'Delivery'
    order_lines = [OrderLine(order=test_order, item=mock_item, quantity=2)]
    test_order.order_lines = order_lines

    assert test_order.calculate_total() == 13.98

def test_corporate_customer_pickup_calculate_total(test_order, mock_item):
    """Test calculating the total price of the order for corporate customer pickup"""
    test_order.customer.type = 'corporate_customer'
    order_lines = [OrderLine(order=test_order, item=mock_item, quantity=2)]
    test_order.order_lines = order_lines

    assert test_order.calculate_total() == 3.98 * 0.9

def test_corporate_customer_delivery_calculate_total(test_order, mock_item):
    """Test calculating the total price of the order for corporate customer delivery"""
    test_order.customer.type = 'corporate_customer'
    test_order.deliveryMethod = 'Delivery'
    order_lines = [OrderLine(order=test_order, item=mock_item, quantity=2)]
    test_order.order_lines = order_lines

    assert test_order.calculate_total() == 3.98 * 0.9 + 10

def test_get_order_details(test_order, mock_item):
    """Test getting the order details"""
    order_lines = [OrderLine(order=test_order, item=mock_item, quantity=2)]
    test_order.order_lines = order_lines
    details = test_order.get_order_details()
    assert details['orderNumber'] == test_order.orderNumber
    assert details['orderDate'] == test_order.orderDate
    assert details['deliveryMethod'] == test_order.deliveryMethod
    assert details['paymentMethod'] == test_order.paymentMethod
    assert details['orderStatus'] == test_order.orderStatus
    assert details['total'] == 3.98
    assert details['items'][0]['name'] == mock_item.vegName
    assert details['items'][0]['quantity'] == 2
    assert details['items'][0]['unit_price'] == mock_item.get_price()
    assert details['items'][0]['subtotal'] == mock_item.calculate_subtotal(2)
    assert details['customer']['id'] == test_order.customer.id
    assert details['customer']['type'] == test_order.customer.type
    assert details['customer']['firstName'] == test_order.customer.firstname
    assert details['customer']['lastName'] == test_order.customer.lastname
    assert details['customer']['custAddress'] == test_order.customer.custAddress
