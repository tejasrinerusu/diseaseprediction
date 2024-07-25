from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import subprocess
import pickle

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection
def get_db_connection():
    conn = sqlite3.connect('/Users/tejasrinerusu/Desktop/users.db')
    conn.row_factory = sqlite3.Row
    return conn

# Load models
diabetes_model = pickle.load(open('/Users/tejasrinerusu/Desktop/diabetes_model.sav', 'rb'))
heart_disease_model = pickle.load(open('/Users/tejasrinerusu/Desktop/heart_disease_model.sav', 'rb'))
parkinsons_model = pickle.load(open('/Users/tejasrinerusu/Desktop/parkinsons_model.sav', 'rb'))

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        qualification = request.form['qualification']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match!')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (first_name, last_name, email, phone, qualification, password) VALUES (?, ?, ?, ?, ?, ?)',
                         (first_name, last_name, email, phone, qualification, hashed_password))
            conn.commit()
            flash('Registration successful!')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already registered!')
            return redirect(url_for('register'))
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            # Start Streamlit as a subprocess
            streamlit_script = '/Users/tejasrinerusu/Desktop/diabetes.py'
            streamlit_command = f'streamlit run {streamlit_script}'
            subprocess.Popen(streamlit_command, shell=True)
            return redirect(url_for('streamlit_redirect'))
        else:
            flash('Incorrect email or password!')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/streamlit_redirect')
def streamlit_redirect():
    return redirect("http://localhost:8501")

@app.route('/predict_diabetes', methods=['POST'])
def predict_diabetes():
    user_input = [float(request.form.get('Pregnancies')),
                  float(request.form.get('Glucose')),
                  float(request.form.get('BloodPressure')),
                  float(request.form.get('SkinThickness')),
                  float(request.form.get('Insulin')),
                  float(request.form.get('BMI')),
                  float(request.form.get('DiabetesPedigreeFunction')),
                  float(request.form.get('Age'))]
    prediction = diabetes_model.predict([user_input])
    result = 'The person is diabetic' if prediction[0] == 1 else 'The person is not diabetic'
    return render_template('index.html', diabetes_result=result)

@app.route('/predict_heart', methods=['POST'])
def predict_heart():
    user_input = [float(request.form.get('age')),
                  float(request.form.get('sex')),
                  float(request.form.get('cp')),
                  float(request.form.get('trestbps')),
                  float(request.form.get('chol')),
                  float(request.form.get('fbs')),
                  float(request.form.get('restecg')),
                  float(request.form.get('thalach')),
                  float(request.form.get('exang')),
                  float(request.form.get('oldpeak')),
                  float(request.form.get('slope')),
                  float(request.form.get('ca')),
                  float(request.form.get('thal'))]
    prediction = heart_disease_model.predict([user_input])
    result = 'The person has heart disease' if prediction[0] == 1 else 'The person does not have heart disease'
    return render_template('index.html', heart_result=result)

@app.route('/predict_parkinsons', methods=['POST'])
def predict_parkinsons():
    user_input = [float(request.form.get('fo')),
                  float(request.form.get('fhi')),
                  float(request.form.get('flo')),
                  float(request.form.get('Jitter_percent')),
                  float(request.form.get('Jitter_Abs')),
                  float(request.form.get('RAP')),
                  float(request.form.get('PPQ')),
                  float(request.form.get('DDP')),
                  float(request.form.get('Shimmer')),
                  float(request.form.get('Shimmer_dB')),
                  float(request.form.get('APQ3')),
                  float(request.form.get('APQ5')),
                  float(request.form.get('APQ')),
                  float(request.form.get('DDA')),
                  float(request.form.get('NHR')),
                  float(request.form.get('HNR')),
                  float(request.form.get('RPDE')),
                  float(request.form.get('DFA')),
                  float(request.form.get('spread1')),
                  float(request.form.get('spread2')),
                  float(request.form.get('D2')),
                  float(request.form.get('PPE'))]
    prediction = parkinsons_model.predict([user_input])
    result = "The person has Parkinson's disease" if prediction[0] == 1 else "The person does not have Parkinson's disease"
    return render_template('index.html', parkinsons_result=result)

if __name__ == '__main__':
    app.run(debug=True)
