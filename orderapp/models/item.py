from orderapp import db
from sqlalchemy import Boolean, Column, Integer, String, Float, ForeignKey, Date, Table, Enum
from sqlalchemy.orm import relationship

class Item(db.Model):
    """
    Base class for all items.
    Type: Veggie, PremadeBox.
    Stock: Number of items in stock.
    """
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    type = Column(String(50))
    stock = Column(Integer, default=0) 
    
    orderLines = relationship('OrderLine', back_populates='item')

    __mapper_args__ = {
        'polymorphic_identity': 'item',
        'polymorphic_on': type
    }

    def calculate_subtotal(self):
        # This method should be overridden in subclasses
        pass

    def get_price(self):
        # This method should be overridden in subclasses
        pass

class Veggie(Item):
    """
    Class for all veggies.
    VegName: Name of the veggie.
    """
    __tablename__ = 'veggies'

    id = Column(Integer, ForeignKey('items.id'), primary_key=True)
    vegName = Column(String(100), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'veggie',
    }

    def __init__(self, vegName, stock=0):
        super().__init__()
        self.vegName = vegName
        self.stock = stock

class WeightedVeggie(Veggie):
    """
    Subclass for weighted veggies.
    Weight: Weight of the veggie.
    WeightPerKilo: Price per kilogram of the veggie.
    """
    __tablename__ = 'weighted_veggies'

    id = Column(Integer, ForeignKey('veggies.id'), primary_key=True)
    weight = Column(Float, nullable=False)
    weightPerKilo = Column(Float, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'weighted_veggie',
    }

    def __init__(self, vegName, weight, weightPerKilo, stock=0):
        super().__init__(vegName, stock)
        self.weight = weight
        self.weightPerKilo = weightPerKilo

    def calculate_subtotal(self, quantity):
        """
        Return the subtotal of the veggie based on the purchased weight and price per kilogram.
        """
        return self.weightPerKilo * quantity
    
    def get_price(self):
        """
        Return the price per kilogram of the veggie.
        """
        return self.weightPerKilo

class PackVeggie(Veggie):
    """
    Subclass for pack veggies.
    NumOfPack: Number of packs in the veggie.
    PricePerPack: Price per pack of the veggie.
    """
    __tablename__ = 'pack_veggies'

    id = Column(Integer, ForeignKey('veggies.id'), primary_key=True)
    numOfPack = Column(Integer, nullable=False)
    pricePerPack = Column(Float, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'pack_veggie',
    }

    def __init__(self, vegName, numOfPack, pricePerPack, stock=0):
        super().__init__(vegName, stock)
        self.numOfPack = numOfPack
        self.pricePerPack = pricePerPack

    def calculate_subtotal(self, quantity):
        """
        Return the subtotal of the veggie based on the purchased quantity and price per pack.
        """
        return self.pricePerPack * quantity
    
    def get_price(self):
        """
        Return the price per pack of the veggie.
        """
        return self.pricePerPack

class UnitPriceVeggie(Veggie):
    """
    Subclass for unit price veggies.
    Quantity: Quantity of the veggie.
    PricePerUnit: Price per unit of the veggie.
    """
    __tablename__ = 'unit_price_veggies'

    id = Column(Integer, ForeignKey('veggies.id'), primary_key=True)
    quantity = Column(Integer, nullable=False)
    pricePerUnit = Column(Float, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'unit_price_veggie',
    }

    def __init__(self, vegName, quantity, pricePerUnit, stock=0):
        super().__init__(vegName, stock)
        self.quantity = quantity
        self.pricePerUnit = pricePerUnit

    def calculate_subtotal(self, quantity):
        """
        Return the subtotal of the veggie based on the purchased quantity and price per unit.
        """
        return self.pricePerUnit * quantity
    
    def get_price(self):
        """
        Return the price per unit of the veggie.
        """
        return self.pricePerUnit

# Table for the contents of a premade box
box_contents = Table('box_contents', db.Model.metadata,
    Column('box_id', Integer, ForeignKey('premade_boxes.id')),
    Column('veggie_id', Integer, ForeignKey('veggies.id')),
    Column('customer_id', Integer, ForeignKey('customers.id'), nullable=True),
    Column('order_id', Integer, ForeignKey('orders.id'), nullable=True),
)

class PremadeBox(Item):
    """
    Class for premade boxes.
    BoxSize: Size of the box.
    NumOfBoxes: Number of boxes in the premade box.
    Price: Price of the premade box.
    IsCustom: Whether the premade box is customized.
    """
    __tablename__ = 'premade_boxes'

    id = Column(Integer, ForeignKey('items.id'), primary_key=True)
    boxSize = Column(Enum('Small', 'Medium', 'Large'), nullable=False)
    numOfBoxes = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    isCustom = Column(Boolean, default=False)

    contents = relationship('Veggie', secondary=box_contents, backref='boxes')

    __mapper_args__ = {
        'polymorphic_identity': 'premade_box',
    }

    def __init__(self, boxSize, numOfBoxes, stock=0, isCustom=False):
        super().__init__()
        self.boxSize = boxSize
        self.numOfBoxes = numOfBoxes
        self.stock = stock
        self.price = self.get_price()
        self.isCustom = isCustom
    
    def get_default_contents(self):
        """
        Get the default contents of the box.
        """
        return db.session.query(Veggie).join(box_contents).filter(
            box_contents.c.box_id == self.id,
            box_contents.c.customer_id == None,
            box_contents.c.order_id == None
        ).all()
    
    def get_contents(self):
        """
        Get the contents of the all boxes.
        """
        return db.session.query(Veggie).join(box_contents).filter(
            box_contents.c.box_id == self.id
        ).all()
    
    def get_price(self):
        """
        Return the price of the premade box based on the size.
        """
        if self.boxSize == 'Small':
            return 10.0
        elif self.boxSize == 'Medium':
            return 25.0
        elif self.boxSize == 'Large':
            return 50.0

    def calculate_subtotal(self, quantity):
        """
        Return the subtotal of the premade box based on the purchased quantity and price.
        """
        return self.price * quantity

    def set_contents(self, veggies):
        """
        Set the default contents of the premade box.
        """
        available_veggies = [v for v in veggies if v.stock > 0]
        self.contents = available_veggies

    def create_custom_box(self, custom_veggie_ids, customer_id):
        """
        Create a new customized box.
        """
        custom_veggies = Veggie.query.filter(Veggie.id.in_(custom_veggie_ids)).all()
        
        new_box = PremadeBox(
            boxSize=self.boxSize,
            numOfBoxes=1,
            stock=1,
            isCustom=True
        )

        db.session.add(new_box)
        db.session.flush() 

        # Add the box contents with custom veggies
        for veggie in custom_veggies:
            db.session.execute(box_contents.insert().values(
                box_id=new_box.id,
                veggie_id=veggie.id,
                customer_id=customer_id,
                order_id=None  # This will be set when the order is placed
            ))
        
        return new_box
    