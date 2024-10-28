from datetime import date
import pytest
from orderapp.tests import create_test_app, db
from orderapp.models.user import Staff, Customer, CorporateCustomer


@pytest.fixture(scope='function')
def app():
    app = create_test_app()
    with app.app_context():
        db.create_all()  # Create all tables before each test
        yield app
        db.session.remove()
        db.drop_all()  # Drop all tables after each test

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def session(app):
    return db.session

# Create common objects
@pytest.fixture
def staff(session):
    staff = Staff(firstname='Ying', lastname='Zheng', username='Ying', password='123456', deptName='Sales')
    session.add(staff)
    session.commit()
    return staff

@pytest.fixture
def customer(session):
    customer = Customer(firstname='Harry', lastname='Potter', username='Harry', password='123456', 
                        address='23 Kingsland Road, Auckland', balance=0.0, maxOwing=100.0)
    session.add(customer)
    session.commit()
    return customer

@pytest.fixture
def corporate_customer(session):
    corp_customer = CorporateCustomer(firstname='Hello', lastname='Fresh', username='hellofresh', password='123456', 
                                      address='23 Kingsland Road, Auckland', balance=0.0, maxCredit=1000.0)
    session.add(corp_customer)
    session.commit()
    return corp_customer

# Test each user type creation
def test_staff_creation(staff):
    assert staff.id is not None
    assert staff.firstname == 'Ying'
    assert staff.lastname == 'Zheng'
    assert staff.username == 'Ying'
    assert staff.dateJoined == date.today()
    assert staff.deptName == 'Sales'
    assert staff.check_password('123456') is True

def test_customer_creation(customer):
    assert customer.id is not None
    assert customer.firstname == 'Harry'
    assert customer.lastname == 'Potter'
    assert customer.username == 'Harry'
    assert customer.custAddress == '23 Kingsland Road, Auckland'
    assert customer.custBalance == 0.0
    assert customer.maxOwing == 100.0
    assert customer.check_password('123456') is True

def test_corporate_customer_creation(corporate_customer):
    assert corporate_customer.id is not None
    assert corporate_customer.firstname == 'Hello'
    assert corporate_customer.lastname == 'Fresh'
    assert corporate_customer.username == 'hellofresh'
    assert corporate_customer.custAddress == '23 Kingsland Road, Auckland'
    assert corporate_customer.custBalance == 0.0
    assert corporate_customer.maxCredit == 1000.0
    assert corporate_customer.discountRate == 0.10
    assert corporate_customer.check_password('123456') is True

# # Test methods of each user type
# def test_staff_list_of_customers(staff, customer, corporate_customer):
#     customers = staff.listOfCustomers
#     assert len(customers) == 2
#     assert any(c.firstname == 'Harry' for c in customers)
#     assert any(c.username == 'hellofresh' for c in customers)

# def test_staff_list_of_orders(staff, order):
#     orders = staff.listOfOrders
    

