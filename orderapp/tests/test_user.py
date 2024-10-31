from datetime import date
import pytest
from unittest.mock import Mock, MagicMock, patch, PropertyMock
from orderapp.models.user import Staff, Customer, CorporateCustomer

@pytest.fixture(scope='function')
def mock_db_session():
    """Mock database session for testing"""
    with patch('orderapp.db.session') as mock_session:
        yield mock_session

@pytest.fixture(scope='function')
def test_staff(mock_db_session):
    """Create a test staff member"""
    staff = Staff(
        firstname='Lucy',
        lastname='Baker',
        username='staff',
        password='123',
        deptName='Sales'
    )
    mock_db_session.add(staff)
    mock_db_session.commit()
    return staff

@pytest.fixture(scope='function')
def test_customer(mock_db_session):
    """Create a test customer"""
    customer = Customer(
        firstname='Ying',
        lastname='Zheng',
        username='ying',
        password='123',
        address='23 Kingsland Road, Auckland',
        balance=0.0,
        maxOwing=100.0
    )
    mock_db_session.add(customer)
    mock_db_session.commit()
    return customer

@pytest.fixture(scope='function')
def test_corporate_customer(mock_db_session):
    """Create a test corporate customer"""
    corp_customer = CorporateCustomer(
        firstname='Hello',
        lastname='Fresh',
        username='fresh',
        password='123',
        address='23 Commerce St, Wellington',
        balance=0.0,
        maxCredit=500.0
    )
    return corp_customer

# Basic creation tests
def test_staff_attributes(test_staff):
    assert test_staff.firstname == 'Lucy'
    assert test_staff.lastname == 'Baker'
    assert test_staff.username == 'staff'
    assert test_staff.deptName == 'Sales'
    assert test_staff.dateJoined == date.today()
    assert test_staff.check_password('123')

def test_customer_attributes(test_customer):
    assert test_customer.firstname == 'Ying'
    assert test_customer.lastname == 'Zheng'
    assert test_customer.username == 'ying'
    assert test_customer.custAddress == '23 Kingsland Road, Auckland'
    assert test_customer.custBalance == 0.0
    assert test_customer.maxOwing == 100.0
    assert test_customer.check_password('123')

def test_corporate_customer_attributes(test_corporate_customer):
    assert test_corporate_customer.firstname == 'Hello'
    assert test_corporate_customer.lastname == 'Fresh'
    assert test_corporate_customer.username == 'fresh'
    assert test_corporate_customer.custAddress == '23 Commerce St, Wellington'
    assert test_corporate_customer.custBalance == 0.0
    assert test_corporate_customer.maxCredit == 500.0
    assert test_corporate_customer.check_password('123')

# Customer method tests
def test_customer_view_profile(test_customer):
    profile = test_customer.view_profile()
    assert profile == {
        'firstname': 'Ying',
        'lastname': 'Zheng',
        'username': 'ying',
        'address': '23 Kingsland Road, Auckland',
        'balance': 0.0,
        'maxOwing': 100.0
    }

# Mocked veggie products
@pytest.fixture(scope='function')
def mock_weighted_veggies():
    """Mock weighted vegetable products"""
    weighted_veggie = Mock(
        id=1,
        type='weighted_veggie',
        vegName='Carrots',
        weight=1.0,
        weightPerKilo=2.50,
        stock=100,
        calculate_subtotal=lambda quantity: 2.50 * quantity,
        get_price=lambda: 2.50
    )
    return weighted_veggie

@pytest.fixture(scope='function')
def mock_pack_veggies():
    """Mock pack vegetable products"""
    pack_veggie = Mock(
        id=3,
        type='pack_veggie',
        vegName='Mushrooms',
        numOfPack=1,
        pricePerPack=4.50,
        stock=50,
        calculate_subtotal=lambda quantity: 4.50 * quantity,
        get_price=lambda: 4.50
    )
    return pack_veggie

@pytest.fixture(scope='function')
def mock_unit_price_veggies():
    """Mock unit price vegetable products"""
    unit_price_veggie = Mock(
        id=2,
        type='unit_price_veggie',
        vegName='Cucumber',
        quantity=1,
        pricePerUnit=3.99,
        stock=50,
        calculate_subtotal=lambda quantity: 3.99 * quantity,
        get_price=lambda: 3.99
    )
    return unit_price_veggie

@pytest.fixture(scope='function')
def mock_premade_boxes():
    """Mock premade box products"""
    mock_box = Mock(
        id=4,
        type='premade_box',
        boxSize='Medium',
        numOfBoxes=1,
        price=25.0,
        stock=20,
        isCustom=False,
        calculate_subtotal=lambda quantity: 25.0 * quantity,
        get_price=lambda: 25.0
    )
    # Mock the get_contents method to return a list of veggie names
    mock_box.get_contents.return_value = [
        Mock(vegName='Carrots'),
        Mock(vegName='Cucumber'),
        Mock(vegName='Mushrooms')
    ]
    return mock_box

def test_customer_view_veggies(test_customer, mock_weighted_veggies, mock_pack_veggies, mock_unit_price_veggies):
    # Mock the view_veggies method in Customer class
    test_customer.view_veggies = Mock(return_value={
        'weighted': [mock_weighted_veggies],
        'pack': [mock_pack_veggies],
        'unit_price': [mock_unit_price_veggies]
    })

    veggies = test_customer.view_veggies()
    
    assert veggies == {
        'weighted': [mock_weighted_veggies],
        'pack': [mock_pack_veggies],
        'unit_price': [mock_unit_price_veggies]
    }

def test_customer_view_premade_boxes(test_customer, mock_premade_boxes):
    # Mock the view_premade_boxes method in Customer class
    test_customer.view_premade_boxes = Mock(return_value=[mock_premade_boxes])
    
    boxes = test_customer.view_premade_boxes()
    
    assert boxes == [mock_premade_boxes]

@patch('orderapp.models.user.Order')
def test_customer_place_order(mock_order, test_customer, mock_db_session):
    """Test the place_order method in Customer class"""
    # Mock the scalar call for max order number
    mock_db_session.query.return_value.scalar.return_value = 999

    # Create a mock order instance
    mock_order_instance = Mock()
    mock_order.return_value = mock_order_instance

    # Call the place_order method
    order = test_customer.place_order('Delivery', 'Credit Card')

    # Verify the Order class was instantiated with correct parameters
    mock_order.assert_called_once_with(
        orderNumber='1000',  
        customer=test_customer,
        deliveryMethod='Delivery',
        paymentMethod='Credit Card',
    )

    # Verify the order was added to the database and committed
    mock_db_session.add.assert_called_with(mock_order_instance)
    mock_db_session.commit.assert_any_call()

    # Verify the returned order is the mock order instance
    assert order == mock_order_instance

@patch('orderapp.models.payment.Payment')
def test_customer_make_payment(mock_payment, test_customer, mock_db_session):
    """Test the make_payment method in Customer class"""
    payment_result = test_customer.make_payment(
        amount=50.0,
        payment_method='Credit Card',
        cardExpiryDate='12/24',
        cardNumber='4111111111111122',
        cardType='Visa'
    )
    
    assert payment_result is True
    assert mock_db_session.add.called
    assert mock_db_session.commit.called

# Mock the add_to_balance method test
def test_customer_add_to_balance(test_customer):
    initial_balance = test_customer.custBalance
    amount_to_add = 50.0
    
    test_customer.add_to_balance(amount_to_add)

    # Check if the balance is updated correctly
    assert test_customer.custBalance == initial_balance + amount_to_add

# Mock the view_order_history method test
def test_customer_view_order_history(test_customer):
    # Mock the order history for the customer
    mock_orders = [
        MagicMock(order_id=1, deliveryMethod='Delivery', orderStatus='Completed', paymentMethod='Credit Card'),
        MagicMock(order_id=2, deliveryMethod='Pickup', orderStatus='Pending', paymentMethod='Debit Card')
    ]

    # Set the side effect for the view_order_history method
    test_customer.view_order_history = MagicMock(return_value=mock_orders)

    order_history = test_customer.view_order_history()

    # Check if the returned order history matches the mock
    assert len(order_history) == 2
    assert order_history[0].order_id == 1
    assert order_history[0].deliveryMethod == 'Delivery'
    assert order_history[0].orderStatus == 'Completed'
    assert order_history[0].paymentMethod == 'Credit Card'
    
    assert order_history[1].order_id == 2
    assert order_history[1].deliveryMethod == 'Pickup'
    assert order_history[1].orderStatus == 'Pending'
    assert order_history[1].paymentMethod == 'Debit Card'

def test_customer_cancel_order(test_customer, mock_db_session):
    # Create a mock order with specific attributes
    mock_order_instance = MagicMock()
    mock_order_instance.id = 1
    mock_order_instance.customer_id = test_customer.id
    mock_order_instance.orderStatus = 'Pending'  # Initial status

    # Mock order lines for the order
    mock_order_line = MagicMock()
    mock_order_line.item.stock = 10  # Initial stock
    mock_order_line.quantity = 2  # Quantity being ordered
    mock_order_instance.order_lines = [mock_order_line]

    # Mock the payment method and calculate_total
    mock_order_instance.paymentMethod = 'Credit Card'
    mock_order_instance.calculate_total.return_value = 100.0

    # Set up the mock database query to return our mock order using get()
    mock_db_session.query.return_value.get.return_value = mock_order_instance
    # Mock the Order.query property to return the mock session query
    with patch('orderapp.models.order.Order.query', new_callable=PropertyMock) as mock_query:
        mock_query.return_value = mock_db_session.query.return_value

        # Call the cancel_order method
        result = test_customer.cancel_order(1)

        # Assertions
        assert result is True
        assert mock_order_instance.orderStatus == 'Cancelled'
        assert mock_order_line.item.stock == 12  # 10 + 2 (restored stock)
        assert mock_db_session.commit.called

# Mock the view_payment_history method test
def test_customer_view_payment_history(test_customer):
    # Mock the payment history for the customer
    payment_history = [
        MagicMock(amount=50.0, date='2024-01-01', method='Credit Card', order_number=1001),
        MagicMock(amount=25.0, date='2024-01-15', method='Debit Card', order_number=1002)
    ]

    # Mock the view_payment_history method directly
    test_customer.view_payment_history = MagicMock(return_value=payment_history)

    payment_history = test_customer.view_payment_history()

    # Check if the returned payment history matches the mock
    assert len(payment_history) == 2
    assert payment_history[0].amount == 50.0
    assert payment_history[0].date == '2024-01-01'
    assert payment_history[0].method == 'Credit Card'
    assert payment_history[0].order_number == 1001
    assert payment_history[1].amount == 25.0
    assert payment_history[1].date == '2024-01-15'
    assert payment_history[1].method == 'Debit Card'
    assert payment_history[1].order_number == 1002

# Corporate customer method tests
def test_corporate_customer_apply_discount(test_corporate_customer):
    amount = 100.0
    discounted = test_corporate_customer.apply_discount(amount)
    assert discounted == amount * (1 - test_corporate_customer.discountRate)

# Staff method tests
def test_staff_list_of_customers(test_staff, mock_db_session):
    # Create mock customers
    mock_customers = [
        Mock(firstname='Ying', lastname='Zheng'),
        Mock(firstname='Hello', lastname='Fresh')
    ]
    
    # Set up the mock query
    mock_db_session.query.return_value.all.return_value = mock_customers
    
    # Get customers using the property
    customers = test_staff.listOfCustomers
    
    assert len(customers) == 2
    assert customers[0].firstname == 'Ying'
    assert customers[1].firstname == 'Hello'
    assert mock_db_session.query.called

def test_staff_list_of_orders(test_staff, mock_db_session):
    # Create mock orders
    mock_orders = [
        Mock(id=1, orderDate=date(2024, 1, 1), calculate_total=lambda: 100.0),
        Mock(id=2, orderDate=date(2024, 1, 2), calculate_total=lambda: 150.0)
    ]
    
    # Set up the mock query
    mock_db_session.query.return_value.order_by.return_value.all.return_value = mock_orders
    
    # Get orders using the property
    orders = test_staff.listOfOrders
    
    assert len(orders) == 2
    assert orders[0]['total'] == 100.0
    assert orders[1]['total'] == 150.0
    assert mock_db_session.query.called

def test_staff_veggies(test_staff, mock_db_session):
    """Test the veggies property"""
    # Create mock veggies
    mock_veggies = [
        Mock(vegName='Carrot'),
        Mock(vegName='Potato'),
        Mock(vegName='Tomato')
    ]
    
    # Set up the mock query
    mock_db_session.query.return_value.all.return_value = mock_veggies
    
    # Get veggies using the property
    veggies = test_staff.veggies
    
    assert len(veggies) == 3
    assert veggies[0].vegName == 'Carrot'
    assert mock_db_session.query.called

def test_staff_premade_boxes(test_staff, mock_db_session):
    # Create mock premade boxes
    mock_boxes = [
        Mock(boxSize='Small', isCustom=False),
        Mock(boxSize='Medium', isCustom=False)
    ]
    
    # Set up the mock query
    mock_db_session.query.return_value.filter.return_value.all.return_value = mock_boxes
    
    # Get premade boxes using the property
    boxes = test_staff.premadeBoxes
    
    assert len(boxes) == 2
    assert boxes[0].boxSize == 'Small'
    assert boxes[1].boxSize == 'Medium'
    assert mock_db_session.query.called

@patch('orderapp.models.order.Order')
def test_staff_update_order_status(mock_order, test_staff, mock_db_session):
    mock_order_instance = Mock()
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_order_instance
    
    test_staff.update_order_status(1, 'Completed')
    
    assert mock_order_instance.orderStatus == 'Completed'
    assert mock_db_session.commit.called

def test_staff_get_weekly_sales(test_staff):
    with patch('orderapp.models.user.Order') as mock_order:
        # Mock some orders with different dates
        mock_order.query.all.return_value = [
            Mock(orderDate=date(2024, 1, 1), calculate_total=lambda: 100),
            Mock(orderDate=date(2024, 1, 8), calculate_total=lambda: 200)
        ]
        
        weekly_sales = test_staff.get_weekly_sales()
        assert len(weekly_sales) > 0
        assert isinstance(weekly_sales, dict)

def test_staff_get_popular_items(test_staff, mock_db_session):
    """Test the get_popular_items method"""
    # Create mock items with order counts
    mock_items = [
        (Mock(id=1, vegName='Carrot'), 10),
        (Mock(id=2, vegName='Potato'), 8),
        (Mock(id=3, vegName='Tomato'), 5)
    ]
    
    # Set up the mock query
    mock_db_session.query.return_value.join.return_value.group_by.return_value\
        .order_by.return_value.limit.return_value.all.return_value = mock_items
    
    # Get popular items
    popular_items = test_staff.get_popular_items()
    
    assert len(popular_items) == 3
    assert popular_items[0]['order_count'] == 10
    assert popular_items[1]['order_count'] == 8
    assert popular_items[2]['order_count'] == 5

def test_staff_get_unpopular_items(test_staff, mock_db_session):
    """Test the get_unpopular_items method"""
    # Create mock items with order counts
    mock_items = [
        (Mock(id=1, vegName='Carrot'), 0),
        (Mock(id=2, vegName='Potato'), 1),
        (Mock(id=3, vegName='Tomato'), 2)
    ]
    
    # Set up the mock query
    mock_db_session.query.return_value.outerjoin.return_value.group_by.return_value\
        .subquery.return_value = Mock()
    mock_db_session.query.return_value.outerjoin.return_value.order_by.return_value\
        .limit.return_value.all.return_value = mock_items
    
    # Get unpopular items
    unpopular_items = test_staff.get_unpopular_items()
    
    assert len(unpopular_items) == 3
    assert unpopular_items[0]['order_count'] == 0
    assert unpopular_items[1]['order_count'] == 1
    assert unpopular_items[2]['order_count'] == 2
