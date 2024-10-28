from flask import Flask, abort, render_template, request, url_for, redirect, session
from orderapp import app, db
from orderapp.decorators import isLoggedIn, isAuthorized
from orderapp.models.item import PackVeggie, PremadeBox, box_contents, UnitPriceVeggie, Veggie, WeightedVeggie
from orderapp.models.order import Order
from orderapp.models.user import Customer, User
from datetime import datetime

@app.route('/view_all_veggies')
@isLoggedIn
@isAuthorized(allowed_roles=['staff'])
def view_all_veggies():
    """View a list of all the veggies."""
    try:
        # Get staff instance
        staff = User.query.get_or_404(session['id'])
        
        veggies = staff.veggies
        premade_boxes = staff.premadeBoxes

        # Categorize veggies
        weighted_veggies = [v for v in veggies if isinstance(v, WeightedVeggie)]
        pack_veggies = [v for v in veggies if isinstance(v, PackVeggie)]
        unit_price_veggies = [v for v in veggies if isinstance(v, UnitPriceVeggie)]
        
        return render_template('all_veggies.html', 
                            weighted_veggies=weighted_veggies,
                            pack_veggies=pack_veggies,
                            unit_price_veggies=unit_price_veggies,
                            premade_boxes=premade_boxes)
    except Exception as e:
        return render_template('error.html', error=str(e))


@app.route('/view_all_orders')
@isLoggedIn
@isAuthorized(allowed_roles=['staff'])
def view_all_orders():
    """View a list of all the orders."""

    try:
        # Get staff instance and order history
        staff = User.query.get_or_404(session['id'])
        order_history = staff.listOfOrders

        return render_template('order_history.html', order_history=order_history)
    except Exception as e:
        return render_template('error.html', error=str(e))


@app.route('/update_order_status', methods=['POST'])
@isLoggedIn
@isAuthorized(allowed_roles=['staff'])
def update_order_status():
    """Update the status of an order."""

    try:
        # Get the order ID and new status from the form
        order_id = request.form.get('order_id')
        new_status = request.form.get('new_status')

        # Get staff instance and update order status
        staff = User.query.get_or_404(session['id'])
        staff.update_order_status(order_id, new_status)

        return redirect(url_for('order_details', order_id=order_id, msg="Order status updated successfully."))
    
    except Exception as e:
        return render_template('error.html', error=str(e))


@app.route('/customer_list')
@isLoggedIn
@isAuthorized(allowed_roles=['staff'])
def customer_list():
    """View a list of all the customers."""

    try:
        # Get staff instance and a list of all customers
        staff = User.query.get_or_404(session['id'])
        customer_list = staff.listOfCustomers
        return render_template('customer_list.html', customer_list=customer_list)
    
    except Exception as e:
        return render_template('error.html', error=str(e))


@app.route('/customer_details/<int:customer_id>')
@isLoggedIn
@isAuthorized(allowed_roles=['staff'])
def customer_details(customer_id):
    """View the details of a customer."""

    try:
        # Get the Customer instance
        customer = Customer.query.get_or_404(customer_id)
        
        if customer:
            # Retrieve the profile data
            profile = customer.view_profile()
            return render_template('profile.html', profile=profile)
        else:
            return render_template('error.html', error="Customer not found.")
    
    except Exception as e:
        return render_template('error.html', error=str(e))


@app.route('/report')
@isLoggedIn
@isAuthorized(allowed_roles=['staff'])
def report():
    """View the summary report of sales."""

    try:
        # Get staff instance 
        staff = User.query.get_or_404(session['id'])

        # Get the weekly, monthly, and yearly sales
        weekly_sales = staff.get_weekly_sales()
        monthly_sales = staff.get_monthly_sales()
        yearly_sales = staff.get_yearly_sales()
        return render_template('report.html', weekly_sales=weekly_sales, monthly_sales=monthly_sales, yearly_sales=yearly_sales)
    
    except Exception as e:
        return render_template('error.html', error=str(e))
    

@app.route('/popularity')
@isLoggedIn
@isAuthorized(allowed_roles=['staff'])
def popularity():
    """View the popular and unpopular items."""

    try:
        # Get staff instance
        staff = User.query.get_or_404(session['id'])   

        # Get the popular and unpopular items
        popular_items = staff.get_popular_items()
        unpopular_items = staff.get_unpopular_items()

        return render_template('popularity.html', popular_items=popular_items, unpopular_items=unpopular_items)

    except Exception as e:
        return render_template('error.html', error=str(e))