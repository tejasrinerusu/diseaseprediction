from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
database = 'database.db'

# Database setup
def init_db():
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL,
            qualification TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Routes
@app.route('/')
def index():
    return redirect(url_for('register'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first-name']
        last_name = request.form['last-name']
        email = request.form['email']
        phone = request.form['phone']
        qualification = request.form['qualification']
        password = request.form['password']
        
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            return "User already exists. Please log in."
        
        cursor.execute('INSERT INTO users (first_name, last_name, email, phone, qualification, password) VALUES (?, ?, ?, ?, ?, ?)', 
                       (first_name, last_name, email, phone, qualification, password))
        conn.commit()
        conn.close()
        
        return redirect(url_for('login'))
    
    return render_template('reg.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            return redirect(url_for('predict_disease'))
        else:
            return "Invalid credentials. Please try again."
    
    return render_template('login.html')

@app.route('/predict_disease')
def predict_disease():
    # This would redirect to your Streamlit application for disease prediction
    os.system('streamlit run prediction.py')
    return "Redirecting to disease prediction..."

if __name__ == "__main__":
    app.run(debug=True, port=5001)
