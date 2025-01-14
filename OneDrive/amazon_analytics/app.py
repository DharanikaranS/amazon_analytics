from flask import Flask, render_template, request, jsonify, redirect, session
import mysql.connector
from mysql.connector import Error
import os
from product_context import ProductContext
import json
from command import SendThankYouEmailCommand

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secret key for session management

def create_db():
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="Dharani27#",
            database="ecommerce_analytics",
            pool_name="mypool",
            pool_size=5
        )
        if conn.is_connected():
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL
                )
            ''')
            conn.commit()
    except Error as e:
        print("Database error:", e)
    finally:
        if conn.is_connected():
            conn.close()
def get_connection():
    return mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="Dharani27#",
            database="ecommerce_analytics",
            pool_name="mypool",
            pool_size=5
    )

create_db()

@app.route('/')
def signup_form():
    return render_template('homepage.html')

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Email and password are required."}), 400

    username = email.split('@')[0] if '@' in email else None
    if not username:
        return jsonify({"message": "Invalid email format."}), 400

    conn = get_connection()
    c = conn.cursor()

    try:
        c.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                  (username, email, password))
        conn.commit()
    except mysql.connector.IntegrityError as e:
        print("Database error:", e)
        return jsonify({"message": "Email already registered."}), 400
    finally:
        if conn.is_connected():
         conn.close()

    return jsonify({"message": "Signup successful!"}), 200

@app.route('/login', methods=['POST'])
def login():
    
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Email and password are required."}), 400

    conn =mysql.connector.connect(
                host="127.0.0.1",
                user="root",
                password="Dharani27#",
                database="ecommerce_analytics"
            )
    c = conn.cursor()

    try:
        c.execute("SELECT id, password FROM users WHERE email = %s", (email,))
        result = c.fetchone()

        if result is None:
            return jsonify({"message": "User not found."}), 404

        user_id, stored_password = result

        if password == stored_password:
            session['user_id'] = user_id  # Set user in session
            session['user_email'] = email
             # Check if notifications are enabled for this user
            c.execute("SELECT notification_enabled FROM notifications WHERE user_id = %s", (user_id,))
            notification_status = c.fetchone()
            session['notification_enabled'] = notification_status[0] if notification_status else False

            return jsonify({"message": "Login successful!"}), 200
        else:
            return jsonify({"message": "Incorrect password."}), 401

    except Exception as e:
        print("Database error:", e)
        return jsonify({"message": "An error occurred. Please try again."}), 500
    finally:
        conn.close()

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')  # Redirect to home if not logged in

    user_id = session['user_id']
    conn =mysql.connector.connect(
                host="127.0.0.1",
                user="root",
                password="Dharani27#",
                database="ecommerce_analytics"
            )
    c = conn.cursor()

    c.execute( "select count(*) from amazon_products where product_type='mobilephones'")
    mobile=c.fetchone()

    c.execute( "select count(*) from amazon_products where product_type='laptop'")
    laptop=c.fetchone()

    c.execute( "select count(*) from amazon_products where product_type='camera'")
    camera=c.fetchone()

    c.execute( "select count(*) from amazon_products where product_type='clothing'")
    clothing=c.fetchone()

    c.execute( "select count(*) from amazon_products where product_type='sneaker'")
    sneaker=c.fetchone()

    c.execute("SELECT username FROM users WHERE id = %s", (user_id,))
    user_data = c.fetchone()
    conn.close()

    if user_data:
        username = user_data[0]
        return render_template('dashboard.html',username=username,mobile=mobile[0],laptop=laptop[0],camera=camera[0],clothing=clothing[0],sneaker=sneaker[0])
    else:
        return redirect('/')  # Redirect to home if user not found
    
@app.route('/product_dashboard/<category>')
def product_dashboard(category):
    if 'user_id' not in session:
        return redirect('/')
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    user_id = session['user_id']
    cursor.execute("SELECT username FROM users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    username=user_data['username']

    # Fetch brand names based on category
    cursor.execute("SELECT DISTINCT brand FROM amazon_products WHERE product_type = %s", (category,))
    brands = [row['brand'] for row in cursor.fetchall()]

    # Fetch data for discount analytics (brand vs discount)
    cursor.execute("""
        SELECT brand, AVG(discount_percentage) as avg_discount
        FROM discounted_products WHERE product_type = %s
        GROUP BY brand
    """, (category,))
    discount_data = [{"brand": row['brand'], "discount": row['avg_discount']} for row in cursor.fetchall()]

    cursor.execute("""
        SELECT brand, AVG(discount_percentage) as avg_discount
        FROM discounted_products WHERE product_type = %s
        GROUP BY brand
    """, (category,))
    discount_data = [{"brand": row['brand'], "discount": row['avg_discount']} for row in cursor.fetchall()]

    cursor.execute("""
        SELECT brand,avg_rating
        FROM frequent_brand_avg_rating WHERE product_type = %s
        GROUP BY brand
    """, (category,))
    brand_rating = [{"brand": row['brand'], "rating": row['avg_rating']} for row in cursor.fetchall()]

    # Fetch brand performance (brand percentage in category)
    cursor.execute("""
        SELECT brand, COUNT(*) * 100.0 / (SELECT COUNT(*) FROM amazon_products WHERE product_type = %s) AS percentage
        FROM amazon_products WHERE product_type = %s GROUP BY brand
    """, (category, category))
    brand_performance = [{"brand": row['brand'], "percentage": row['percentage']} for row in cursor.fetchall()]

    # Fetch price history (example data for simplicity)
    cursor.execute('''
    SELECT distinct(ap.brand),ap.product_name, ph.previous_price, ph.new_price, ph.change_date
    FROM price_history AS ph
    JOIN amazon_products AS ap ON ph.product_id = ap.id
    WHERE ap.product_type = %s
''', (category,))
    price_history = cursor.fetchall()

    # Fetch feedback for the category
    ''' cursor.execute("SELECT feedback FROM product_feedback WHERE product_type = %s", (category,))
    feedbacks = [row['feedback'] for row in cursor.fetchall()]'''

    conn.close()
    
    return render_template(
        'productdash.html',
        username=username,
        category=category,
        brands=brands,
        discount_data=discount_data,
        brand_performance=brand_performance,
        brand_rating=brand_rating,
        price_history=price_history,
        
    )


@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Clear user session
    session.pop('notification_enabled', None)  # Clear notification setting in session
    return redirect('/')

def get_all_products():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM amazon_products")  # Fetch all products
    products = cursor.fetchall()
    conn.close()
    return products
@app.route('/filter_products', methods=['GET'])
def filter_products():
    price_range = request.args.get('price')  # Get the price filter value
    rating = request.args.get('rating')      # Get the rating filter value
    brand = request.args.get('brand')        # Get the brand filter value

    # Initialize query components
    query = "SELECT * FROM amazon_products WHERE 1=1"
    params = []

    # Price Range Filtering
    if price_range:
        if price_range == '30000+':
            query += " AND current_price >= %s"
            params.append(30000)
        else:
            min_price, max_price = map(int, price_range.split('-'))
            query += " AND current_price BETWEEN %s AND %s"
            params.extend([min_price, max_price])

    # Rating Filtering
    if rating:
        query += " AND rating >= %s"
        params.append(int(rating))

    # Brand Filtering
    if brand:
        query += " AND brand = %s"
        params.append(brand)

    # Execute the query with parameters
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, tuple(params))
    products = cursor.fetchall()
    conn.close()

    # Pass the filtered products to the template
    return render_template('filtered_products.html', products=products)
import json

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    if 'user_id' not in session:
        return jsonify({"message": "User not logged in."}), 401

    data = request.get_json()
    print("Received feedback data:", data)
    feedback = data.get('feedback')
    email = session.get('user_email') 

    if not feedback:
        return jsonify({"message": "Feedback cannot be empty."}), 400

    feedback_data = {
        "email": email,
        "feedback": feedback
    }

    # Write feedback to a JSON file
    feedback_file_path = 'feedback.json'
    try:
        if os.path.exists(feedback_file_path):
            with open(feedback_file_path, 'r+') as file:
                feedback_list = json.load(file)
                feedback_list.append(feedback_data)
                file.seek(0)
                json.dump(feedback_list, file, indent=4)
        else:
            with open(feedback_file_path, 'w') as file:
                json.dump([feedback_data], file, indent=4)
    except Exception as e:
        print("Error writing to JSON:", e)
        return jsonify({"message": "Error saving feedback."}), 500
    
    # Execute the thank-you email command
    email_command = SendThankYouEmailCommand(email, feedback)
    email_command.execute()

    return jsonify({"message": "Feedback submitted successfully!"}), 200

   


if __name__ == '__main__':
    app.run(debug=True)
