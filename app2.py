from flask import Flask,render_template,jsonify,request, redirect, url_for, session
from src.pipeline.prediction_pipeline import CustomData,PredictPipeline
from src.auth_service import fetch_user_data, google_login, google_oauth_callback, fetch_google_fit_data
import os
import time
from datetime import datetime
#from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from hashlib import sha256
import config
import certifi
import uuid


application=Flask(__name__)
application.secret_key = "testing"
application.config.from_object(config)

def datetimeformat(value):
    timestamp = int(value) / 1000  # Convert nanoseconds to milliseconds
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

application.jinja_env.filters['datetimeformat'] = datetimeformat

client = MongoClient(config.MONGO_URI,tlsCAFile=certifi.where())
db = client["phi_pro"]
col = db["user_data"]


@application.route('/')
def loggin():
    return render_template('login.html')

@application.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = col.find_one({'email': email})
        if user and sha256(password.encode("utf-8")).hexdigest()==user['password']:
            session['email'] = email
            user_data = fetch_user_data(email)
            session['user_data'] = user_data
            return redirect(url_for('google_login_route'))
        else:
            return render_template('login.html', error='Invalid email or password')
    return render_template('signup.html')

@application.route('/signup_page')
def index():
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
        
        if password:
            hashed_password = sha256(password.encode("utf-8")).hexdigest()
            col.insert_one({'_id':uuid.uuid4().hex,'username': username, 'email': email,'password': hashed_password,
                            'age':age,'height':height,'weight':weight})
            return render_template('login.html')
        else:
            return render_template('signup.html')
    return render_template('signup.html')

@application.route('/google_login')
def google_login_route():
    return google_login()

@application.route('/callback')
def callback():
    return google_oauth_callback()

@application.route('/fetch_data')
def fetch_data():
    data = fetch_google_fit_data()
    session['data'] = data

    if 'error' in data:
        
        return render_template('home.html')
    
    # If data is successfully retrieved, return it in the template
    return render_template('home.html')

@application.route('/index')
def home_page():
    if 'email' in session and 'user_data' in session and 'data' in session:
        user_data = session['user_data']
        data = session['data']
        
        # Render the template with user and Google Fit data
        return render_template('home.html', user_data=user_data, data=data)

        
# #@application.route('/main_page')
# #def home_page():
#     return render_template("home.html")

# @application.route("/predict",methods=["GET", "POST"])
# def predict_datapoint():
#     if request.method=="GET":
#         return render_template("home.html")
    
#     else:
#         data=CustomData(
            
#             Income = float(request.form.get('Income')),
#             Customer_days = int(request.form.get('Customer_days')),
#             Total_Amount = int(request.form.get('Total_Amount')),
#             Total_Purchases = int(request.form.get('Total_Purchases')),
            
#             Child = int(request.form.get('Child')),
#             Total_offer = int(request.form.get('Total_offer'))
#         )
#         final_new_data=data.get_data_as_dataframe()
#         predict_pipeline=PredictPipeline()
#         pred=predict_pipeline.predict(final_new_data)
        
#         if pred == 1:
#             result = "This is our companay's Ideal customer"

#         else:
#             result = "This is not our companay's Ideal customer"
        
        
#         return render_template("form.html",final_result = result)
    

if __name__ == '__main__':
    application.run(host="127.0.0.1",port=5000,debug = True)