from flask import Flask, render_template, request, url_for, redirect
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import session
from orderapp import app
from orderapp.models.user import User

PASSWORD_SALT = app.config['PASSWORD_SALT']

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page."""
    if request.method == 'GET':
        return render_template('login.html')
    
    else:
        # Create variables for access
        userName = request.form['username']
        userPassword = request.form['password']
        
        try:
            # Check if username exists 
            user = User.query.filter_by(username=userName).first()

            # Check if password is correct
            if user and user.check_password(userPassword):
                # If password correct, create session data
                session['loggedin'] = True
                session['id'] = user.id
                session['username'] = user.username
                session['role'] = user.type
                return redirect(url_for('home')) 
            else:
                return render_template('login.html', error='Incorrect username or password')
            
        except Exception as e:
            return render_template('error.html', error=str(e))   

        
@app.route('/logout')
def logout():
    # Remove session data when logout.
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('role', None)
    if 'cart' in session:
        session.pop('cart', None)

    # Redirect to login page
    return redirect(url_for('home'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error='Page not found'), 404

