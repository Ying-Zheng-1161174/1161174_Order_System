from flask import Flask, abort, render_template, request, url_for, redirect, session
from orderapp import app, db
from orderapp.decorators import isLoggedIn
from orderapp.models.item import PackVeggie, PremadeBox, box_contents, UnitPriceVeggie, WeightedVeggie
from orderapp.models.order import Order
from orderapp.models.user import Customer
from datetime import datetime

@app.route('/profile')
@isLoggedIn
def profile():
    """Return the user's profile details."""
    try:
        # Query the database to get the Customer instance
        customer = Customer.query.get_or_404(session['id'])
        
        if customer:
            # Retrieve the profile data
            profile = customer.view_profile()
            return render_template('profile.html', profile=profile)
        else:
            return render_template('error.html', error="User not found")
    
    except Exception as e:
        return render_template('error.html', error=str(e))


@app.route('/view_veggies')
@isLoggedIn
def view_veggies():
    """View all the available vegetables and premade boxes."""
    try:
        customer = Customer.query.get_or_404(session['id'])

        # Get all the available veggies and premade boxes
        veggies = customer.view_veggies()
        premade_boxes = customer.view_premade_boxes()
        return render_template('veggies.html', veggies=veggies, premade_boxes=premade_boxes)
    
    except Exception as e:
        return render_template('error.html', error=str(e))


@app.route('/add_to_cart', methods=['POST'])
@isLoggedIn
def add_to_cart():
    """Add an item to the customer's cart so they can start to placing an order."""
    
    try:
        item_id = request.form['item_id']
        item_type = request.form['item_type']
        quantity = request.form['quantity']
        customize_box = request.form.get('customize_box')

        # Validate and convert quantity to float
        try:
            quantity = float(quantity)
            if quantity <= 0:
                return redirect(url_for('view_veggies', error="Please enter a valid quantity"))
        except ValueError:
            return redirect(url_for('view_veggies', error="Please enter a valid number for quantity"))
        
        # Get the item from the database
        if item_type == 'weighted':
            item = WeightedVeggie.query.get_or_404(item_id)
        elif item_type == 'pack':
            item = PackVeggie.query.get_or_404(item_id)
        elif item_type == 'unit_price':
            item = UnitPriceVeggie.query.get_or_404(item_id)
        elif item_type == 'premade_box':
            item = PremadeBox.query.get_or_404(item_id)
            
            # Create a customized premade box if it is a customized premade box
            if customize_box and request.form.getlist('custom_veggies'):
                custom_veggie_ids = request.form.getlist('custom_veggies')
                item = item.create_custom_box(custom_veggie_ids, session['id'])
                db.session.commit()
                # Update item_id 
                item_id = item.id  
            else:
                # Use the original box if not customized
                item = item

        else:
            return render_template('error.html', error="Invalid item type")
     
        # Check if the cart exists in the session
        if 'cart' not in session:
            session['cart'] = []

        # Calculate subtotal for an item
        subtotal = item.calculate_subtotal(quantity)

        # Add the item to the cart
        cart_item = next((i for i in session['cart'] if i['id'] == int(item_id) and i['type'] == item_type), None)
        
        # If the item is already in the cart, update the quantity and subtotal
        if cart_item:
            cart_item['quantity'] += quantity
            cart_item['subtotal'] = round(float(cart_item['subtotal']) + subtotal, 2)

        # If the item is not in the cart, add it to the cart
        else:
            session['cart'].append({
                'id': int(item_id),
                'type': item_type,
                'name': item.vegName if hasattr(item, 'vegName') else f"{item.boxSize} Premade Box",
                'price': float(item.get_price()),  
                'quantity': quantity,
                'subtotal': round(float(subtotal), 2)
            })

        session.modified = True
        return redirect(url_for('view_veggies', msg="Item added to cart successfully."))
    
    except Exception as e:
        return render_template('error.html', error=str(e))


@app.route('/view_cart')
@isLoggedIn
def view_cart():
    """View the items in the customer's cart."""
    try:
        # Get the customer from the database
        customer = Customer.query.get_or_404(session['id'])
        # Get the cart from the session
        cart = session.get('cart', [])
        # Calculate the subtotal of the items in the cart
        subtotal = sum(float(item['subtotal']) for item in cart)

        # Fetch box contents for premade boxes
        for item in cart:
            if item['type'] == 'premade_box':
                box = PremadeBox.query.get(item['id'])
                if box:
                    item['contents'] = [veggie.vegName for veggie in box.get_contents()]
                    
        # If the customer is a corporate customer, apply a 10% discount
        if session.get('role') == 'corporate_customer':
            subtotal = customer.apply_discount(subtotal)
        return render_template('cart.html', cart=cart, subtotal=subtotal)
    
    except Exception as e:
        return render_template('error.html', error=str(e))


@app.route('/process_payment', methods=['POST'])
@isLoggedIn
def process_payment():
    """Get the delivery method, total price, and payment method, allow user to place an order and make payment."""
    try:
        # Get the delivery method from the form
        delivery_method = request.form.get('delivery_method')

        # For delivery, add $10 to the total price
        if delivery_method == 'Delivery':
            total_price = round(float(request.form.get('subtotal')) + 10.00, 2)
        # For pickup, the total price is the subtotal of the items in the cart
        else: 
            total_price = round(float(request.form.get('subtotal')), 2)
        return render_template('process_payment.html', total_price=total_price, delivery_method=delivery_method)
    
    except Exception as e:
        return render_template('error.html', error=str(e))


@app.route('/place_order_and_process_payment', methods=['GET', 'POST'])
@isLoggedIn
def place_order_and_process_payment():
    """Create an order object and allow user to make payment."""
    try:
        # Get the variables from the form
        payment_method = request.form.get('payment_method')
        delivery_method = request.form.get('delivery_method')
        total_price = request.form.get('total_price')

        # Get the customer from the database
        customer = Customer.query.get_or_404(session['id'])

        # Place an order
        order = customer.place_order(delivery_method, payment_method)

        # Add the items to the order
        cart = session.get('cart', [])
        for item in cart:
            item_id = item['id']
            item_type = item['type']
            quantity = item['quantity']

            # Get the item from the database based on its type
            if item_type == 'weighted':
                item = WeightedVeggie.query.get_or_404(item_id)
            elif item_type == 'pack':
                item = PackVeggie.query.get_or_404(item_id)
            elif item_type == 'unit_price':
                item = UnitPriceVeggie.query.get_or_404(item_id)
            elif item_type == 'premade_box':
                item = PremadeBox.query.get_or_404(item_id)
            else:
                raise ValueError(f"Invalid item type: {item_type}")
            
            order.add_item(item, quantity)

        # Process Credit Card, Debit Card payment
        if payment_method != 'Account':
            return render_template('card_payment.html', 
                                   total_price=total_price, 
                                   payment_method=payment_method, 
                                   order=order,
                                   currentdate = datetime.now().date())
        # Process Account payment
        else:
            customer_balance = customer.custBalance
            max_owning = customer.maxOwing
            # Check if the customer can charge from their account based on the updated balance
            can_charge = False
            if customer_balance + float(total_price) <= max_owning:
                can_charge = True   

            return render_template('account_payment.html', 
                                   total_price=round(float(total_price), 2), 
                                   customer_balance=customer_balance,
                                   max_owning=max_owning,
                                   can_charge=can_charge,
                                   order=order)

    except Exception as e:
        return render_template('error.html', error=str(e))


@app.route('/add_credit_card_payment', methods=['POST'])
@isLoggedIn
def add_credit_card_payment():
    """Add a credit card payment to the database."""
    try:
        # Get the variables from the form
        card_type = request.form.get('card_type')
        card_number = request.form.get('card_number')
        card_expiry_date = request.form.get('card_expiry_date')
        total_price = float(request.form.get('total_price'))
        order_id = int(request.form.get('order_id'))

        # Get the customer from the database
        customer = Customer.query.get_or_404(session['id'])

        # Get the order from the database
        order = Order.query.get_or_404(order_id)

        # Make the payment
        customer.make_payment(
            total_price, 
            'Credit Card', 
            order, 
            cardExpiryDate=card_expiry_date, 
            cardNumber=card_number, 
            cardType=card_type)
        
        # Add order_id to the box_contents table
        for item in session.get('cart', []):
            if item['type'] == 'premade_box':
                box = PremadeBox.query.get(item['id'])
                box.order_id = order_id
                db.session.commit()

        # Update the stock of items after receiving the payment
        order.update_stock()
        
        # Clear the cart
        session.pop('cart', None)
        return redirect(url_for('order_details', order_id=order_id, msg="Thank you! Your order was placed successfully."))

    except Exception as e:
        return render_template('error.html', error=str(e))


@app.route('/add_debit_card_payment', methods=['POST'])
@isLoggedIn
def add_debit_card_payment():
    """Add a debit card payment to the database."""
    try:
        # Get the variables from the form
        bank_name = request.form.get('bank_name')
        debit_card_number = request.form.get('debit_card_number')
        total_price = float(request.form.get('total_price'))
        order_id = int(request.form.get('order_id'))

        # Get the customer from the database
        customer = Customer.query.get_or_404(session['id'])

        # Get the order from the database
        order = Order.query.get_or_404(order_id)

        # Make the payment
        customer.make_payment(
            total_price, 
            'Debit Card', 
            order, 
            bankName=bank_name, 
            debitCardNumber=debit_card_number)
        
        # Add order_id to the box_contents table
        for item in session.get('cart', []):
            if item['type'] == 'premade_box':
                box = PremadeBox.query.get(item['id'])
                box.order_id = order_id
                db.session.commit()
        
        # Update the stock of items after receiving the payment
        order.update_stock()
        
        # Clear the cart
        session.pop('cart', None)
        return redirect(url_for('order_details', order_id=order_id, msg="Thank you! Your order was placed successfully."))

    except Exception as e:
        return render_template('error.html', error=str(e))


@app.route('/add_account_payment', methods=['POST'])
@isLoggedIn
def add_account_payment():
    """Add an account payment to the database and update the customer's balance."""
    try:
        # Get the variables from the form
        total_price = float(request.form.get('total_price'))
        order_id = int(request.form.get('order_id'))

        # Get the customer from the database
        customer = Customer.query.get_or_404(session['id'])
        
        # Get the order from the database
        order = Order.query.get_or_404(order_id)

        # Make the payment
        customer.make_payment(total_price, 'Account', order)

        # Update box_contents with order_id for a premade box in the cart
        for item in session.get('cart', []):
            if item['type'] == 'premade_box':
                db.session.execute(
                    box_contents.update()
                    .where(box_contents.c.box_id == item['id'])
                    .values(order_id=order_id)
                )
        db.session.commit()

        # Update the stock of items after receiving the payment
        order.update_stock()

        # Clear the cart
        session.pop('cart', None)
        return redirect(url_for('order_details', order_id=order_id, msg=f'Charge from account successful! New balance: ${customer.custBalance}'))

    except Exception as e:
        return render_template('error.html', error=str(e))

            
@app.route('/order_history')
@isLoggedIn
def order_history():
    """View the order histories."""
    try:
        # Get the customer and customer's balance from the database
        customer = Customer.query.get_or_404(session['id'])
        customer_balance = customer.custBalance
        # Get customer's order history
        order_history = customer.view_order_history()

        return render_template('order_history.html', order_history=order_history, customer_balance=customer_balance)
    
    except Exception as e:
        return render_template('error.html', error=str(e))
    

@app.route('/order_details/<int:order_id>')
@isLoggedIn
def order_details(order_id):
    """View the order details."""
    try:
        # Get the order and its details from the database
        order = Order.query.get_or_404(order_id)
        order_details = order.get_order_details()

        return render_template('order_details.html', order=order_details, order_id=order_id)
    
    except Exception as e:
        return render_template('error.html', error=str(e))


@app.route('/cancel_order/<int:order_id>')
@isLoggedIn
def cancel_order(order_id):
    """Cancel the order."""
    try:
        # Get the order and customer from the database
        order = Order.query.get_or_404(order_id)
        customer = Customer.query.get_or_404(session['id'])

        # Cancel the order
        customer.cancel_order(order_id)

        # Initialize a message after cancelling the order
        msg = ""
        if order.paymentMethod == 'Account':
            msg = f"Order #{order.orderNumber} cancelled successfully. New balance: ${customer.custBalance}"
        else:
            msg = f"Order #{order.orderNumber} cancelled successfully."

        return redirect(url_for('order_details', order_id=order_id, msg=msg))
    
    except Exception as e:
        return render_template('error.html', error=str(e))


@app.route('/pay_balance', methods=['GET', 'POST'])
@isLoggedIn
def pay_balance():
    """Pay the balance."""

    # Get the customer and customer's balance from the database
    customer = Customer.query.get_or_404(session['id'])
    customer_balance = customer.custBalance

    try:
        if request.method == 'GET':
            return render_template('pay_balance.html', 
                                   customer_balance=customer_balance,
                                   currentdate = datetime.now().date())
    
        else:
            # Get the variables from the form
            paid_amount = float(request.form.get('paid_amount'))
            # Make payment for the balance
            customer.custBalance -= paid_amount
            db.session.commit()
            # Display the updated balance after the payment
            return redirect(url_for('pay_balance', msg=f"Payment of ${paid_amount} successful."))
    
    except Exception as e:
        return render_template('error.html', error=str(e))
            
            
@app.route('/payment_history')
@isLoggedIn
def payment_history():
    """View the payment history."""
    try:
        # Get the customer and their payment history from the database
        customer = Customer.query.get_or_404(session['id'])
        payment_history = customer.view_payment_history()
        return render_template('payment_history.html', payment_history=payment_history)
    
    except Exception as e:
        return render_template('error.html', error=str(e))
        

@app.route('/clear_cart')
@isLoggedIn
def clear_cart():
    """Clear the cart."""
    session.pop('cart', None)
    return redirect(url_for('view_cart'))
