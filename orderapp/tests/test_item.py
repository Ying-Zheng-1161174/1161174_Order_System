import pytest
from unittest.mock import Mock, patch
from orderapp.models.item import WeightedVeggie, PackVeggie, UnitPriceVeggie, PremadeBox

@pytest.fixture(scope='function')
def mock_db_session():
    """Mock database session for testing"""
    with patch('orderapp.db.session') as mock_session:
        yield mock_session

@pytest.fixture(scope='function')
def test_weighted_veggie(mock_db_session):
    """Create a test weighted veggie"""
    weighted_veggie = WeightedVeggie(
        vegName='Carrot',
        weight=1.0,
        weightPerKilo=1.99,
        stock=10
    )
    mock_db_session.add(weighted_veggie)
    mock_db_session.commit()
    return weighted_veggie

@pytest.fixture(scope='function')
def test_pack_veggie(mock_db_session):
    """Create a test pack veggie"""
    pack_veggie = PackVeggie(
        vegName='Avocado',
        numOfPack=1.0,
        pricePerPack=3.99,
        stock=10
    )
    mock_db_session.add(pack_veggie)
    mock_db_session.commit()
    return pack_veggie

@pytest.fixture(scope='function')
def test_unit_price_veggie(mock_db_session):
    """Create a test unit price veggie"""
    unit_price_veggie = UnitPriceVeggie(
        vegName='Cucumber',
        quantity=1.0,
        pricePerUnit=2.99,
        stock=10
    )
    mock_db_session.add(unit_price_veggie)
    mock_db_session.commit()
    return unit_price_veggie

@pytest.fixture(scope='function')
def test_premade_box(mock_db_session):
    """Create a test premade box"""
    premade_box = [
        PremadeBox(
            boxSize='Small',
            numOfBoxes=1,
            stock=10
        ),
        PremadeBox(
            boxSize='Medium',
            numOfBoxes=1,
            stock=10
        ),
        PremadeBox(
            boxSize='Large',
            numOfBoxes=1,
            stock=10
        )
    ]
    mock_db_session.add(premade_box)
    mock_db_session.commit()
    return premade_box

# Basic creation tests
def test_weighted_veggie_attributes(test_weighted_veggie):
    assert test_weighted_veggie.vegName == 'Carrot'
    assert test_weighted_veggie.weight == 1.0
    assert test_weighted_veggie.weightPerKilo == 1.99
    assert test_weighted_veggie.stock == 10

def test_pack_veggie_attributes(test_pack_veggie):
    assert test_pack_veggie.vegName == 'Avocado'
    assert test_pack_veggie.numOfPack == 1.0
    assert test_pack_veggie.pricePerPack == 3.99
    assert test_pack_veggie.stock == 10

def test_unit_price_veggie_attributes(test_unit_price_veggie):
    assert test_unit_price_veggie.vegName == 'Cucumber'
    assert test_unit_price_veggie.quantity == 1.0
    assert test_unit_price_veggie.pricePerUnit == 2.99
    assert test_unit_price_veggie.stock == 10

def test_premade_box_attributes(test_premade_box):
    assert test_premade_box[0].boxSize == 'Small'
    assert test_premade_box[0].numOfBoxes == 1
    assert test_premade_box[0].stock == 10
    assert test_premade_box[0].price == 10.00
    assert test_premade_box[1].boxSize == 'Medium'
    assert test_premade_box[1].numOfBoxes == 1
    assert test_premade_box[1].stock == 10
    assert test_premade_box[1].price == 25.00
    assert test_premade_box[2].boxSize == 'Large'
    assert test_premade_box[2].numOfBoxes == 1
    assert test_premade_box[2].stock == 10
    assert test_premade_box[2].price == 50.00

# Veggies methods tests
def test_weighted_veggie_calculate_subtotal(test_weighted_veggie):
    quantity = 5
    assert test_weighted_veggie.calculate_subtotal(quantity) == quantity * 1.99

def test_pack_veggie_calculate_subtotal(test_pack_veggie):
    quantity = 5
    assert test_pack_veggie.calculate_subtotal(quantity) == quantity * 3.99

def test_unit_price_veggie_calculate_subtotal(test_unit_price_veggie):
    quantity = 5
    assert test_unit_price_veggie.calculate_subtotal(quantity) == quantity * 2.99

def test_get_price_weighted_veggie(test_weighted_veggie):
    assert test_weighted_veggie.get_price() == 1.99

def test_get_price_pack_veggie(test_pack_veggie):
    assert test_pack_veggie.get_price() == 3.99

def test_get_price_unit_price_veggie(test_unit_price_veggie):
    assert test_unit_price_veggie.get_price() == 2.99

# Premade box methods tests
def test_premade_box_calculate_subtotal(test_premade_box):
    quantity = 5
    assert test_premade_box[0].calculate_subtotal(quantity) == quantity * 10.00
    assert test_premade_box[1].calculate_subtotal(quantity) == quantity * 25.00
    assert test_premade_box[2].calculate_subtotal(quantity) == quantity * 50.00

def test_get_price_premade_box(test_premade_box):
    assert test_premade_box[0].get_price() == 10.00
    assert test_premade_box[1].get_price() == 25.00
    assert test_premade_box[2].get_price() == 50.00

def test_premade_box_set_contents(test_premade_box, test_weighted_veggie, test_pack_veggie, test_unit_price_veggie, mock_db_session):
    # Use veggie instances from fixtures
    mock_veggies = [
        test_weighted_veggie,  
        test_pack_veggie,
        test_unit_price_veggie
    ]
    
    # Set contents for the first box
    box = test_premade_box[0]
    box.set_contents(mock_veggies)
    
    # Verify contents were set
    assert len(box.contents) == 3
    assert any(v.vegName == 'Carrot' for v in box.contents)
    assert any(v.vegName == 'Avocado' for v in box.contents)
    assert any(v.vegName == 'Cucumber' for v in box.contents)

def test_create_custom_box(test_premade_box, test_weighted_veggie, test_pack_veggie, test_unit_price_veggie, mock_db_session):
    # Use veggie instances from fixtures
    mock_veggies = [
        test_weighted_veggie,
        test_pack_veggie,
        test_unit_price_veggie
    ]
    
    # Mock the Veggie.query
    with patch('orderapp.models.item.Veggie') as mock_veggie_class:
        mock_query = Mock()
        mock_query.filter.return_value.all.return_value = mock_veggies
        mock_veggie_class.query = mock_query
        
        # Create custom box
        box = test_premade_box[0]
        custom_veggie_ids = [1, 2]  # Mock IDs
        customer_id = 1
        
        custom_box = box.create_custom_box(custom_veggie_ids, customer_id)
        
        # Verify the custom box properties
        assert custom_box.boxSize == box.boxSize
        assert custom_box.numOfBoxes == 1
        assert custom_box.stock == 1
        assert custom_box.isCustom == True
        assert custom_box.price == box.price
        
        # Verify the session interactions
        mock_db_session.add.assert_called_once()
        mock_db_session.flush.assert_called_once()
        
        # Verify box_contents insertion was called
        assert mock_db_session.execute.call_count == 3  # Once for each veggie