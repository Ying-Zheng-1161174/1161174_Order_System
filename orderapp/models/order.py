from orderapp import db
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, Enum
from sqlalchemy.orm import relationship
from datetime import date


class Order(db.Model):
    """
    Order class.
    """
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    orderDate = Column(Date, nullable=False, default=date.today)
    orderNumber = Column(String(50), unique=True, nullable=False)
    deliveryMethod = Column(Enum('Delivery', 'Pickup'), nullable=False)
    orderStatus = Column(Enum('Pending', 'Processed','Completed','Cancelled'), nullable=False, default='Pending')
    paymentMethod = Column(Enum('Credit Card', 'Debit Card', 'Account'), nullable=False)
    customer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    customer = relationship('Customer', foreign_keys=[customer_id])
    payment = relationship('Payment', back_populates='order', uselist=False)
    order_lines = relationship('OrderLine', back_populates='order')

    @property
    def listOfItems(self):
        """
        Return the order lines in the order.
        """
        return self.order_lines

    def __init__(self, orderNumber, customer, deliveryMethod, paymentMethod, orderStatus='Pending'):
        self.orderNumber = orderNumber
        self.customer = customer
        self.deliveryMethod = deliveryMethod
        self.paymentMethod = paymentMethod
        self.orderStatus = orderStatus

    def calculate_total(self):
        """
        Calculate the total price of the order.
        Depends on the delivery method and the customer type.
        """
        if self.deliveryMethod == 'Delivery' and self.customer.type == 'private_customer':
            return sum(line.subtotal for line in self.order_lines) + 10.00
        elif self.deliveryMethod == 'Delivery' and self.customer.type == 'corporate_customer':
            return sum(line.subtotal for line in self.order_lines) * 0.9 + 10.00
        elif self.deliveryMethod == 'Pickup' and self.customer.type == 'private_customer':
            return sum(line.subtotal for line in self.order_lines)
        elif self.deliveryMethod == 'Pickup' and self.customer.type == 'corporate_customer':
            return sum(line.subtotal for line in self.order_lines) * 0.9

    def get_order_details(self):
        """
        Get the order details.
        """
        return {
            'id': self.id,
            'orderNumber': self.orderNumber,
            'orderDate': self.orderDate,
            'deliveryMethod': self.deliveryMethod,
            'paymentMethod': self.paymentMethod,
            'orderStatus': self.orderStatus,
            'total': self.calculate_total(),
            'items': [self._get_item_details(line) for line in self.order_lines],
            'customer': {
                'id': self.customer.id,
                'type': self.customer.type,
                'firstName': self.customer.firstname,
                'lastName': self.customer.lastname,
                'custAddress': self.customer.custAddress
            },
        }

    def _get_item_details(self, line):
        """
        Get details for a single item in the order.
        """
        if hasattr(line.item, 'vegName'):
            return {
                'name': line.item.vegName,
                'quantity': line.quantity,
                'unit_price': line.item.get_price(),
                'subtotal': line.subtotal
            }
        else:  
            # Premade Box
            return {
                'name': line.item.boxSize + ' Premade Box',
                'size': line.item.boxSize,
                'contents': [veggie.vegName for veggie in line.item.get_contents()],
                'quantity': line.quantity,
                'unit_price': line.item.get_price(),
                'subtotal': line.subtotal
            }
    
    def add_item(self, item, quantity):
        """
        Add an item to the order_lines list.
        """
        if item.stock < quantity:
            raise ValueError(f"Not enough stock. Available: {item.stock}, Requested: {quantity}")
        
        new_line = OrderLine(order=self, item=item, quantity=quantity)
        self.order_lines.append(new_line)
        
        db.session.add(new_line)
        db.session.commit()

    def update_stock(self):
        """
        Update the stock of items after receiving the payment.
        """
        for line in self.order_lines:
            item = line.item
            if item.stock < line.quantity:
                raise ValueError(f"Not enough stock for {item.vegName}. Available: {item.stock}, Ordered: {line.quantity}")
            
            item.stock -= line.quantity
            db.session.add(item)
        
        db.session.commit()    

class OrderLine(db.Model):
    """
    List of items in an order, displayed the item name, quantity, and subtotal.
    Each order can have multiple order lines.
    """
    __tablename__ = 'order_lines'

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    item_id = Column(Integer, ForeignKey('items.id'))
    quantity = Column(Integer, nullable=False)
    subtotal = Column(Float, nullable=False)

    order = relationship("Order", back_populates="order_lines")
    item = relationship("Item", back_populates="orderLines")

    def __init__(self, order, item, quantity):
        self.order = order
        self.item = item
        self.quantity = quantity
        self.subtotal = item.calculate_subtotal(quantity)
