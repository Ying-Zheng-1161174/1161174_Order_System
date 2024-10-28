from flask import redirect
from flask import url_for
from flask import render_template
from flask import session
from functools import wraps

def isLoggedIn(f):
    """
    Login is required for accessing a route, if user is not logged in,
    they will be redirected to the login page.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'loggedin' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def isAuthorized(allowed_roles=None):
    """
    Check if the user has the required role.
    """
    if allowed_roles is None:
        allowed_roles = []

    def my_decorator(f):
        @wraps(f)
        def my_wrapper(*args, **kwargs):
            if 'loggedin' in session:
                # Check if the user has an allowed role
                if session.get('role') in allowed_roles:
                    return f(*args, **kwargs)
                return render_template('error.html', error='Access Denied')
            else:
                return redirect(url_for('login'))
        return my_wrapper
    return my_decorator
