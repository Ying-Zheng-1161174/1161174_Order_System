import sys
import os
from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from orderapp import db
from orderapp.models.user import Staff, Customer, CorporateCustomer
from orderapp.models.item import WeightedVeggie, PackVeggie, UnitPriceVeggie, PremadeBox
from orderapp.models.order import Order, OrderLine
from orderapp.models.payment import CreditCardPayment, DebitCardPayment
from orderapp.config import Config

# current_dir = os.path.dirname(os.path.abspath(__file__))
# project_root = os.path.dirname(current_dir)
# sys.path.insert(0, project_root)

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Create engine using the configuration
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

# Create all tables
db.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

def insert_initial_data():

    # Create a staff member
    staff1 = Staff(firstname="Lucy", lastname="Baker", username="staff", password="123", deptName="Sales")
    session.add(staff1)

    # Create 3 private customers
    customers = [
        Customer(firstname="Ying", lastname="Zheng", username="ying", password="123", address="23 Kingsland Road, Auckland", balance=0.0, maxOwing=100.0),
        Customer(firstname="Harry", lastname="Potter", username="harry", password="123", address="3 North Road, Wellington", balance=0.0, maxOwing=100.0),
        Customer(firstname="Peter", lastname="Wu", username="peter", password="123", address="5 Lincoln Road, Christchurch", balance=0.0, maxOwing=100.0),
    ]
    session.add_all(customers)

    # Create 2 corporate customers
    corp_customers = [
        CorporateCustomer(firstname="Hello", lastname="Fresh", username="fresh", password="123", address="23 Commerce St, Wellington", balance=0.0, maxCredit=500.0),
        CorporateCustomer(firstname="Everyday", lastname="Veggies", username="veggies", password="123", address="45 Great South Road, Auckland", balance=0.0, maxCredit=1000.0),
    ]
    session.add_all(corp_customers)

    session.commit()

    # Create 10 different veggies
    veggies = [
        WeightedVeggie(vegName="Kumara", weight=1.0, weightPerKilo=3.99, stock=100),
        WeightedVeggie(vegName="Pumpkin", weight=1.0, weightPerKilo=2.99, stock=80),
        WeightedVeggie(vegName="Yam", weight=1.0, weightPerKilo=7.99, stock=50),
        WeightedVeggie(vegName="Taro", weight=1.0, weightPerKilo=6.99, stock=60),
        PackVeggie(vegName="Celery", numOfPack=1, pricePerPack=3.99, stock=75),
        PackVeggie(vegName="Lettuce", numOfPack=1, pricePerPack=2.99, stock=90),
        PackVeggie(vegName="Spinach", numOfPack=1, pricePerPack=3.50, stock=70),
        UnitPriceVeggie(vegName="Feijoa", quantity=1, pricePerUnit=0.99, stock=200),
        UnitPriceVeggie(vegName="Avocado", quantity=1, pricePerUnit=1.99, stock=150),
        UnitPriceVeggie(vegName="Cucumber", quantity=1, pricePerUnit=1.99, stock=100),  
    ]
    session.add_all(veggies)

    # Create default premade boxes with 3 sizes
    boxes = [
        PremadeBox(boxSize="Small", numOfBoxes=1, stock=30),
        PremadeBox(boxSize="Medium", numOfBoxes=1, stock=25),
        PremadeBox(boxSize="Large", numOfBoxes=1, stock=20),
    ]
    session.add_all(boxes)

    # Add some default veggies to the boxes
    boxes[0].set_contents(veggies[:3])
    boxes[1].set_contents(veggies[:6])
    boxes[2].set_contents(veggies)

    # Create some orders
    orders = [
        Order(orderNumber="1001", customer=customers[0], deliveryMethod="Delivery", paymentMethod="Credit Card"),
        Order(orderNumber="1002", customer=customers[1], deliveryMethod="Pickup", paymentMethod="Debit Card"),
        Order(orderNumber="1003", customer=corp_customers[0], deliveryMethod="Delivery", paymentMethod="Credit Card"),
    ]

    # Set specific order dates
    orders[0].orderDate = date(2024, 5, 7)
    orders[1].orderDate = date(2024, 8, 10)
    orders[2].orderDate = date(2024, 9, 15)

    session.add_all(orders)

    # Add items to orders
    order_lines = [
        OrderLine(order=orders[0], item=veggies[0], quantity=2),
        OrderLine(order=orders[0], item=boxes[0], quantity=1),
        OrderLine(order=orders[1], item=veggies[2], quantity=3),
        OrderLine(order=orders[2], item=boxes[2], quantity=1),
    ]
    session.add_all(order_lines)
    
    # Create some payments
    payments = [
        CreditCardPayment(paymentAmount=30.0, customer=customers[0], order=orders[0], cardExpiryDate=date.today() + timedelta(days=365), cardNumber="1234567890123456", cardType="Visa"),
        DebitCardPayment(paymentAmount=25.0, customer=customers[1], order=orders[1], bankName="ANZ Bank", debitCardNumber="9876543210987654"),
        CreditCardPayment(paymentAmount=60.0, customer=corp_customers[0], order=orders[2], cardExpiryDate=date.today() + timedelta(days=365), cardNumber="1234567890123456", cardType="Visa"),
    ]
    session.add_all(payments)

    # Commit the session
    session.commit()

if __name__ == "__main__":
    insert_initial_data()
    print("Initial data inserted successfully.")
