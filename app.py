from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
from mysql.connector import Error
import logging
import sys
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

logging.basicConfig(level=logging.DEBUG)

def db_connection():
    try:
        connection = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            database=app.config['MYSQL_DB'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD']
        )
        if connection.is_connected():
            logging.info("Database connection successful")
            return connection
        else:
            raise Exception("Connection is None")
    except Error as e:
        logging.error(f"Database connection failed: {str(e)}")
        sys.exit("Database connection failed")

# Route Guest
@app.route('/')
def beranda():
    return render_template('landing-page.html', active_page='beranda')

@app.route('/informasi')
def informasi():
    return render_template('informasi.html', active_page='informasi')

@app.route('/struktur')
def struktur():
    return render_template('struktur.html', active_page='struktur')

@app.route('/galeri')
def galeri():
    return render_template('galeri.html', active_page='galeri')

# Route Admin
@app.route('/master', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        try:
            connection = db_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute('SELECT * FROM admin WHERE username = %s AND password = %s', (username, password))
            admin = cursor.fetchone()
            
            if admin:
                session['logged_in'] = True
                session['username'] = username
                return redirect(url_for('admin_dashboard'))
            else:
                error = 'Invalid username or password'
        except Exception as e:
            error = f"Error connecting to the database: {str(e)}"
            logging.error(error)
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
        
    return render_template('admin/login.html', error=error)
    
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'logged_in' not in session:
        return redirect(url_for('admin_login'))
    return render_template('admin/dashboard.html')

@app.route('/admin/informasi')
def admin_informasi():
    return render_template('admin/informasi.html')

@app.route('/admin/struktur')
def admin_struktur():
    return render_template('admin/struktur.html')

@app.route('/admin/galeri')
def admin_galeri():
    return render_template('admin/galeri.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(debug=True)
