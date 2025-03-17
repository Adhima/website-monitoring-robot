from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Konfigurasi MySQL di Laragon
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Sesuaikan dengan user MySQL Anda
app.config['MYSQL_PASSWORD'] = ''  # Sesuaikan dengan password MySQL Anda
app.config['MYSQL_DB'] = 'flask_login'  # Sesuaikan dengan nama database Anda

mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')  # Menghindari error KeyError
    password = request.form.get('password')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
    account = cursor.fetchone()

    if account:
        session['loggedin'] = True
        session['id'] = account['id']
        session['username'] = account['username']
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html', error="Username atau password salah!", username=username)

@app.route('/dashboard')
def dashboard():
    if 'loggedin' in session:
        return render_template('dashboard.html', username=session["username"])
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
