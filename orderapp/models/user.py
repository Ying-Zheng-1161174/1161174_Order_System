from orderapp import db, hashing, app
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, desc, func
from sqlalchemy.orm import relationship
from datetime import date, timedelta
from .item import Item, PackVeggie, PremadeBox, UnitPriceVeggie, Veggie, WeightedVeggie
from .order import Order, OrderLine
from .payment import Payment, CreditCardPayment, DebitCardPayment, AccountPayment
from sqlalchemy.orm import column_property
from sqlalchemy import join
from collections import defaultdict

class User(db.Model):
    """
    Base class for all users.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    firstname = Column(String(100), nullable=False)
    lastname = Column(String(100), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    type = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': type
    }

    def __init__(self, firstname, lastname, username, password):
        self.firstname = firstname
        self.lastname = lastname
        self.username = username
        self.set_password(password)
  
    def set_password(self, password):
        """
        Hash password.
        """
        self.password_hash = hashing.hash_value(password, salt=app.config['PASSWORD_SALT'])

    def check_password(self, password):
        """
        Check password, return True if correct.
        """
        return hashing.check_value(self.password_hash, password, salt=app.config['PASSWORD_SALT'])
    
    def __str__(self):
        return f"{self.firstname} {self.lastname} ({self.username})"

class Staff(User):
    """
    Staff class.
    """
    __tablename__ = 'staffs'

    id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    dateJoined = Column(Date, nullable=False, default=date.today)
    deptName = Column(String(100), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'staff',
    }

    @property
    def listOfCustomers(self):
        """
        List all the customers.
        """
        return db.session.query(Customer).all()
    
    @property
    def listOfOrders(self):
        """
        List all the orders and ordered by order date.
        """
        orders = db.session.query(Order).order_by(
            desc(Order.orderDate)).all()
        return [{'order': order, 'total': order.calculate_total()} for order in orders]
    
    @property
    def premadeBoxes(self):
        """
        List all the default premade boxes.
        """
        return db.session.query(PremadeBox).filter(PremadeBox.isCustom == False).all()
    
    @property
    def veggies(self):
        """
        List all the veggies.
        """
        return db.session.query(Veggie).all()

    def __init__(self, firstname, lastname, username, password, deptName, dateJoined=None):
        super().__init__(firstname, lastname, username, password)
        self.deptName = deptName
        self.dateJoined = dateJoined or date.today()

    def update_order_status(self, order_id, new_status):
        """
        Update the status of an order.
        Including 'Pending', 'Processing', 'Completed', 'Cancelled'.
        Return the updated order if successful.
        """
        order = db.session.query(Order).filter(Order.id == order_id).first()
        if order:
            order.orderStatus = new_status
            db.session.commit()
        return order
    
    def get_weekly_sales(self):
        """
        Get total sales for each week of each month across all years.
        Return a dictionary with the week number, month, and year as the key, and the total sales as the value.
        """
        weekly_sales = defaultdict(float)

        # Get all orders
        orders = Order.query.all()

        for order in orders:
            year = order.orderDate.year
            month = order.orderDate.month
            day = order.orderDate.day
            
            # Calculate the week number (1-5)
            week_number = (day - 1) // 7 + 1
            
            # Create a key for this week
            week_key = f"week{week_number}/{month:02d}/{year}"
            
            # Add the order total to the appropriate week
            weekly_sales[week_key] += order.calculate_total()

        # Sort the dictionary by date
        sorted_weekly_sales = dict(sorted(weekly_sales.items(), 
                                          key=lambda x: (int(x[0].split('/')[-1]),  # year
                                                         int(x[0].split('/')[1]),   # month
                                                         int(x[0].split('week')[1].split('/')[0]))))  # week

        return sorted_weekly_sales

    def get_monthly_sales(self):
        """
        Get total sales for each month of the current year.
        Return a dictionary with the month and year as the key, and the total sales as the value.
        """
        current_year = date.today().year
        start_date = date(current_year, 1, 1)
        end_date = date(current_year, 12, 31)

        orders = Order.query.filter(Order.orderDate.between(start_date, end_date)).all()

        monthly_sales = defaultdict(float)
        for order in orders:
            month_key = f"{order.orderDate.month:02d}/{current_year}"
            monthly_sales[month_key] += order.calculate_total()

        return dict(monthly_sales)

    def get_yearly_sales(self):
        """
        Get total sales for the current year.
        Return a dictionary with the year as the key, and the total sales as the value.
        """
        current_year = date.today().year
        start_date = date(current_year, 1, 1)
        end_date = date(current_year, 12, 31)

        orders = Order.query.filter(Order.orderDate.between(start_date, end_date)).all()
        total_sales = sum(order.calculate_total() for order in orders)

        return {str(current_year): total_sales}

    def get_popular_items(self):
        """
        List the most popular items based on order count.
        """
        popular_items = db.session.query(Item, func.count(OrderLine.id).label('order_count')).\
                        join(OrderLine).group_by(Item.id).order_by(desc('order_count')).limit(5).all()
    
        return [
            {
                'item': item,
                'item_name': self._get_item_name(item),
                'order_count': order_count
            }
            for item, order_count in popular_items
        ]

    def get_unpopular_items(self):
        """
        List the least popular items, including those never ordered.
        """
        subquery = db.session.query(
            Item.id,
            func.count(OrderLine.id).label('order_count')
        ).outerjoin(OrderLine).group_by(Item.id).subquery()

        unpopular_items = db.session.query(Item, func.coalesce(subquery.c.order_count, 0).label('order_count')).\
            outerjoin(subquery, Item.id == subquery.c.id).\
            order_by(func.coalesce(subquery.c.order_count, 0), Item.id).\
            limit(5).all()

        return [
            {
                'item': item,
                'item_name': self._get_item_name(item),
                'order_count': order_count
            }
            for item, order_count in unpopular_items
        ]
    
    def _get_item_name(self, item):
        """
        Helper method to get the name of the item based on its type.
        """
        if isinstance(item, Veggie):
            return item.vegName
        elif isinstance(item, PremadeBox):
            return f"{item.boxSize} Premade Box"

    def __str__(self):
        return f"{super().__str__()} - Staff in {self.deptName}"

class Customer(User):
    """
    Customer class.
    """
    __tablename__ = 'customers'

    id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    custAddress = Column(String(255), nullable=False)
    custBalance = Column(Float, nullable=False, default=0.00)
    maxOwing = Column(Float, nullable=False, default=100.00) 
    payments = relationship("Payment", back_populates="customer")

    __mapper_args__ = {
        'polymorphic_identity': 'private_customer',
    }

    def __init__(self, firstname, lastname, username, password, address, balance, maxOwing):
        super().__init__(firstname, lastname, username, password)
        self.custAddress = address
        self.custBalance = balance
        self.maxOwing = maxOwing

    def view_profile(self):
        """
        View the user's profile.
        Return a dictionary with the user's first name, last name, username, address, balance, and max owing.
        """
        return {
            'firstname': self.firstname,
            'lastname': self.lastname,
            'username': self.username,
            'address': self.custAddress,
            'balance': self.custBalance,
            'maxOwing': self.maxOwing
        }

    def view_veggies(self):
        """
        View all the available vegetables.
        """
        return {
            'weighted': self.view_weighted_veggies(),
            'pack': self.view_pack_veggies(),
            'unit_price': self.view_unit_price_veggies()
        }
    
    def view_weighted_veggies(self):
        """
        View all available weighted vegetables.
        Return a list of dictionaries with the id, name, weight, weight per kilo, and stock.
        """
        weighted_veggies = db.session.query(WeightedVeggie).filter(WeightedVeggie.stock > 0).all()
        return [{
            'id': veggie.id,
            'vegName': veggie.vegName,
            'weight': veggie.weight,
            'weightPerKilo': veggie.weightPerKilo,
            'stock': veggie.stock
        } for veggie in weighted_veggies]

    def view_pack_veggies(self):
        """
        View all available pack vegetables.
        Return a list of dictionaries with the id, name, number of packs, price per pack, and stock.
        """
        pack_veggies = db.session.query(PackVeggie).filter(PackVeggie.stock > 0).all()
        return [{
            'id': veggie.id,
            'vegName': veggie.vegName,
            'numOfPack': veggie.numOfPack,
            'pricePerPack': veggie.pricePerPack,
            'stock': veggie.stock
        } for veggie in pack_veggies]

    def view_unit_price_veggies(self):
        """
        View all available unit price vegetables.
        Return a list of dictionaries with the id, name, price per unit, and stock.
        """
        unit_price_veggies = db.session.query(UnitPriceVeggie).filter(UnitPriceVeggie.stock > 0).all()
        return [{
            'id': veggie.id,
            'vegName': veggie.vegName,
            'pricePerUnit': veggie.pricePerUnit,
            'stock': veggie.stock
        } for veggie in unit_price_veggies]
    
    def view_premade_boxes(self):
        """
        View all the available default non-customized premade boxes.
        Return a list of dictionaries with the id, name, number of boxes, stock, price, and contents.
        """
        boxes = db.session.query(PremadeBox).filter(
            PremadeBox.stock > 0,
            PremadeBox.isCustom == False  
        ).all()

        return [{
            'id': box.id,
            'boxSize': box.boxSize,
            'numOfBoxes': box.numOfBoxes,
            'stock': box.stock, 
            'price': box.get_price(),
            'contents': [veggie.vegName for veggie in box.get_contents()]
        } for box in boxes]
    
    def place_order(self, delivery_method, payment_method):
        """
        Create a new order object to place an order.
        Return the new order if successful.
        """

        # Get the maximum order number from the database and increment it
        max_order_number = db.session.query(func.max(Order.orderNumber)).scalar() or 999
        new_order_number = max(int(max_order_number) + 1, 1000)

        # Create a new order
        order = Order(orderNumber=str(new_order_number), 
                      customer=self, 
                      deliveryMethod=delivery_method, 
                      paymentMethod=payment_method)
        
        db.session.add(order)
        db.session.commit()

        return order

    def make_payment(self, amount, payment_method, order=None, **kwargs):
        """
        Make a payment for the order or the balance.
        Use **kwargs to accept additional parameters for different payment methods.
        Return True if successful.
        """

        # Validate amount
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise ValueError("Invalid payment amount")
    
        if payment_method == 'Credit Card':
            required_fields = ['cardExpiryDate', 'cardNumber', 'cardType']
            if not all(field in kwargs for field in required_fields):
                raise ValueError("Credit Card payment requires cardExpiryDate, cardNumber, and cardType")
            payment = CreditCardPayment(paymentAmount=amount, customer=self, order=order,
                                        cardExpiryDate=kwargs['cardExpiryDate'],
                                        cardNumber=kwargs['cardNumber'],
                                        cardType=kwargs['cardType'])
        elif payment_method == 'Debit Card':
            required_fields = ['bankName', 'debitCardNumber']
            if not all(field in kwargs for field in required_fields):
                raise ValueError("Debit Card payment requires bankName and debitCardNumber")
            payment = DebitCardPayment(paymentAmount=amount, customer=self, order=order,
                                    bankName=kwargs['bankName'],
                                    debitCardNumber=kwargs['debitCardNumber'])
        elif payment_method == 'Account':
            payment = AccountPayment(paymentAmount=amount, customer=self, order=order)
            # If payment method is Account, update the customer's balance
            payment.process_payment()
        else:
            raise ValueError(f"Invalid payment method: {payment_method}")
        
        db.session.add(payment)
        db.session.commit()
        return True  

    def add_to_balance(self, amount):
        """
        Add amount to the customer's balance.
        Return the updated balance.
        """
        self.custBalance += amount
        db.session.commit()
        return self.custBalance

    def view_order_history(self):
        """
        View the order history for a specific customer.
        Order by orderDate in descending order.
        Return a list of dictionaries with the order and total.
        """

        # Join Order and Payment tables
        query = db.session.query(Order, Payment).\
            outerjoin(Payment, Order.id == Payment.order_id).\
            filter(Order.customer_id == self.id).\
            order_by(Order.orderDate.desc()) 
        
        # Initialize lists to store valid orders and orders to delete
        valid_orders = []
        orders_to_delete = []
        
        # Only order with payment is valid, otherwise delete
        for order, payment in query:
            if payment:
                valid_orders.append({'order': order, 'total': order.calculate_total()})
            else:
                orders_to_delete.append(order)

        # Remove orders without payments
        for order in orders_to_delete:
            db.session.delete(order)

        # Commit the changes to the database
        db.session.commit()
        return valid_orders

    def cancel_order(self, order_id):
        """
        Cancel the order and restore stock.
        Return True if successful.
        """
        try:
            order = Order.query.get(order_id)
            if order.orderStatus == 'Pending':
                order.orderStatus = 'Cancelled'

                # Restore stock for each item in the order
                for order_line in order.order_lines:
                    item = order_line.item
                    item.stock += order_line.quantity

                # Refund the customer's balance if the payment method is Account
                if order.paymentMethod == 'Account':
                    refund_amount = order.calculate_total()
                    # Ensure the balance doesn't go below 0
                    self.custBalance = max(0, self.custBalance - refund_amount)

                db.session.commit()
                return True
            
        except Exception:
            return False
    
    def view_payment_history(self):
        """
        View the payment history.
        Return a list of dictionaries with the date, amount, method, and order number.
        """
        payment_history = []
        for payment in self.payments:
            payment_info = {
                'date': payment.paymentDate,
                'amount': payment.paymentAmount,
                'method': payment.type,
                'order_number': payment.order.orderNumber
            }
            payment_history.append(payment_info)
        return payment_history
    
    def __str__(self):
        return f"{super().__str__()} - Customer with balance ${self.custBalance}"

class CorporateCustomer(Customer):
    """
    Corporate customer class.
    """
    __tablename__ = 'corporate_customers'

    id = Column(Integer, ForeignKey('customers.id'), primary_key=True)
    discountRate = Column(Float, nullable=False, default=0.10)
    _maxCredit = Column('maxCredit', Float, nullable=False)

    # Use column_property to link maxOwing and maxCredit
    maxOwing = column_property(Customer.maxOwing)

    __mapper_args__ = {
        'polymorphic_identity': 'corporate_customer',
    }

    def __init__(self, firstname, lastname, username, password, address, balance, maxCredit, discountRate=0.10):
        super().__init__(firstname, lastname, username, password, address, balance, maxOwing=maxCredit)
        self.discountRate = discountRate
        self._maxCredit = maxCredit

    @property
    def maxCredit(self):
        return self._maxCredit

    @maxCredit.setter
    def maxCredit(self, value):
        self._maxCredit = value
        self.maxOwing = value

    def apply_discount(self, amount):
        """
        Apply the discount to the corporate customer.
        Return the amount after discount.
        """
        return amount * (1 - self.discountRate)

    def __str__(self):
        return f"{super().__str__()} - Corporate Customer with {self.discountRate*100}% discount"





