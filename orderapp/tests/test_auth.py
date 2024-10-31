# tests/test_auth.py
import pytest
from orderapp.models.user import Customer

class MockSession(dict):
    """Mock session that works like Flask session"""
    def pop(self, key, default=None):
        return super().pop(key, default)

@pytest.fixture
def mock_session():
    """Create a mock session"""
    return MockSession()

@pytest.fixture
def test_customer():
    """Create a real customer instance for testing"""
    customer = Customer(
        firstname="Ying",
        lastname="Zheng",
        username="ying",
        password="123",
        address="23 Kingsland Road, Auckland",
        balance=0.0,
        maxOwing=100.0
    )
    customer.set_password("123")
    return customer

def login_user(user, password, session):
    """Simulate login logic"""
    if user and user.check_password(password):
        session['loggedin'] = True
        session['id'] = user.id
        session['username'] = user.username
        session['role'] = user.type
        return True
    return False

def logout_user(session):
    """Simulate logout logic"""
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('role', None)
    session.pop('cart', None)

def test_successful_login(test_customer, mock_session):
    """Test successful login with correct password"""
    result = login_user(test_customer, "123", mock_session)
    
    assert result is True
    assert mock_session['loggedin'] is True
    assert mock_session['username'] == 'ying'
    assert mock_session['role'] == 'private_customer'

def test_failed_login_wrong_password(test_customer, mock_session):
    """Test login with wrong password"""
    result = login_user(test_customer, "122", mock_session)
    
    assert result is False
    assert 'loggedin' not in mock_session

def test_logout(mock_session):
    """Test logout functionality"""
    # Set up session data
    mock_session.update({
        'loggedin': True,
        'id': 1,
        'username': 'testuser',
        'role': 'private_customer',
    })
    
    logout_user(mock_session)
    
    # Verify session data is cleared
    assert 'loggedin' not in mock_session
    assert 'id' not in mock_session
    assert 'username' not in mock_session
    assert 'role' not in mock_session