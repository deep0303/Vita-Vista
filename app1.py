from flask import Flask, render_template, request, redirect, url_for, session
from src.auth_service import fetch_user_data, google_login, fetch_google_fit_data
from src.auth_service import google_oauth_callback
from src.utils import create_dataframe, standardize_data, make_prediction, generate_health_recommendations, extract_recommendations
import os
import time
from datetime import datetime
from pymongo import MongoClient
from hashlib import sha256
import config
import certifi
import uuid
import pandas as pd  # Import pandas

application = Flask(__name__)
application.secret_key = "testing"
application.config.from_object(config)

def datetimeformat(value):
    timestamp = int(value) / 1000  # Convert nanoseconds to milliseconds
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

# Add the datetimeformat filter to Jinja2 environment
application.jinja_env.filters['datetimeformat'] = datetimeformat

# MongoDB connection setup
client = MongoClient(config.MONGO_URI, tlsCAFile=certifi.where())
db = client["phi_pro"]
col = db["user_data"]

@application.route('/')
def login_page():
    return render_template('login.html')

@application.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = col.find_one({'email': email})
        user_data = fetch_user_data(email)
        # Verify email and password
        if user and sha256(password.encode("utf-8")).hexdigest() == user['password']:
            session['email'] = email
            session['user_data'] = user_data
            
            oauth_success = google_login(email)

            if oauth_success:
                # Fetch Google Fit data if OAuth succeeds
                google_fit_data = fetch_google_fit_data()
                google_fit_data = {
                    'steps': 7842,
                    'heart_rate': 68,
                    'calories': 322.968,
                    'sleep': 7.7
                }
                
                session['google_fit_data'] = google_fit_data

                if 'error' in google_fit_data:
                    return render_template('index.html', error='Failed to retrieve Google Fit data')

                return render_template('index.html', user_data=user_data, google_fit_data=google_fit_data)
            else:
                return render_template('login.html', error="Google OAuth failed")
        else:
            return render_template('login.html', error='Invalid email or password')

@application.route('/signup_page')
def signup_page():
    return render_template('signup.html')

@application.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        age = request.form['age']
        height = request.form['height']
        weight = request.form['weight']
        gender = request.form['gender']
        
        if password:
            hashed_password = sha256(password.encode("utf-8")).hexdigest()
            col.insert_one({'_id': uuid.uuid4().hex, 'username': username, 'email': email,
                            'password': hashed_password, 'age': age,
                            'height': height, 'weight': weight, 'gender': gender})
            return redirect(url_for('login_page'))
        else:
            return render_template('signup.html', error="Please provide a password")
    
    return render_template('signup.html')


@application.route('/callback')
def callback():
    return google_oauth_callback()

@application.route('/index')
def dashboard_page():
    if 'email' in session and 'user_data' in session and 'google_fit_data' in session:
        user_data = session['user_data']
        google_fit_data = session['google_fit_data']
        
        return render_template('index.html', user_data=user_data, google_fit_data=google_fit_data)

@application.route('/recommend', methods=['GET', 'POST'])
def recommendation_page():
    if request.method == 'POST':
        medical_condition = request.form.get('medical_condition')
        allergies = request.form.get('allergies')
        currentdietplan = request.form.get('currentdietplan')
        currentexercises = request.form.get('currentexercises')
    
        if not medical_condition or not allergies or not currentdietplan or not currentexercises:
            # If form data is missing, return an error message
            return render_template('home.html', error="Please provide all required inputs.")
    
        if 'email' in session and 'user_data' in session and 'google_fit_data' in session:
             user_data = session['user_data']
             google_fit_data = session['google_fit_data']
        
             df = create_dataframe(user_data, google_fit_data)
        
        # Standardize the data
             scaled_df = standardize_data(df)
        
        # Make a prediction using the scaled data
             prediction = make_prediction(scaled_df)

             gender = user_data.get('gender', 'N/A')

             recommendations = generate_health_recommendations(
                 health_status=prediction,
                 medical_condition=medical_condition,
                 allergies=allergies,
                 currentdietplan=currentdietplan,
                 currentexercises=currentexercises,
                 gender=gender
             )

             dietary_recommendations = extract_recommendations(recommendations, 'Dietary Recommendations')
             exercise_plan = extract_recommendations(recommendations, 'Exercise Plan')

        return render_template(
            'home.html',
            prediction=prediction,
            dietary_recommendations=dietary_recommendations,
            exercise_plan=exercise_plan,
        )

    return render_template('home.html')

@application.route('/consultation')
def consult():
    return render_template("consultation.html")
 
@application.route('/profile')
def profile(username):
    user_data = col.find_one({'username': username})
    
    if not user_data:
        return "User not found", 404
    
    user_data['_id'] = str(user_data['_id'])
    return render_template('profile.html', user=user_data)



if __name__ == '__main__':
    application.run(host="127.0.0.1", port=5000, debug=True)
