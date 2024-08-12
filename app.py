from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
import mysql.connector
from mysql.connector import Error
import logging
import sys
from dotenv import load_dotenv
import os
import uuid

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
    connection = db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM informasi')
    informasi_list = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('informasi.html', informasi_list=informasi_list, active_page='informasi')

@app.route('/informasi/<int:id>')
def informasi_detail(id):
    connection = db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM informasi WHERE id = %s', (id,))
    informasi_item = cursor.fetchone()
    cursor.close()
    connection.close()
    return render_template('informasi_detail.html', informasi_item=informasi_item)

@app.route('/struktur')
def struktur():
    connection = db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM struktur')
    struktur_list = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('struktur.html', struktur_list=struktur_list, active_page='struktur')

@app.route('/galeri')
def galeri():
    connection = db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM galeri')
    galeri_list = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('galeri.html', galeri_list=galeri_list, active_page='galeri')

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

    connection = db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute('SELECT COUNT(*) AS count FROM informasi')
    informasi_count = cursor.fetchone()['count']

    cursor.execute('SELECT COUNT(*) AS count FROM struktur')
    struktur_count = cursor.fetchone()['count']

    cursor.execute('SELECT COUNT(*) AS count FROM galeri')
    galeri_count = cursor.fetchone()['count']

    cursor.close()
    connection.close()

    return render_template('admin/dashboard.html', 
                           informasi_count=informasi_count, 
                           struktur_count=struktur_count, 
                           galeri_count=galeri_count,
                           active_page='dashboard')

# Route Admin Informasi
@app.route('/admin/informasi', methods=['GET', 'POST'])
def admin_informasi():
    if 'logged_in' not in session:
        return redirect(url_for('admin_login'))

    connection = db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == 'POST':
        judul = request.form.get('judul')
        isi = request.form.get('isi')
        tanggal = request.form.get('tanggal')
        file = request.files.get('gambar')

        if file and file.filename:
            filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
        else:
            filename = None

        try:
            cursor.execute(
                'INSERT INTO informasi (judul, isi, tanggal, gambar) VALUES (%s, %s, %s, %s)',
                (judul, isi, tanggal, filename)
            )
            connection.commit()
            flash('Informasi added successfully!', 'success')
        except Error as e:
            logging.error(f"Error inserting data: {str(e)}")
            flash('Error adding informasi', 'danger')
        finally:
            cursor.close()
            connection.close()

    connection = db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM informasi')
    informasi_list = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('admin/informasi.html', informasi_list=informasi_list, active_page='informasi')

@app.route('/admin/informasi/edit/<int:id>', methods=['GET', 'POST'])
def edit_informasi(id):
    if 'logged_in' not in session:
        return redirect(url_for('admin_login'))

    connection = db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == 'POST':
        judul = request.form['judul']
        isi = request.form['isi']
        tanggal = request.form['tanggal']
        if 'gambar' in request.files:
            file = request.files['gambar']
            if file:
                filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                cursor.execute('UPDATE informasi SET judul = %s, isi = %s, tanggal = %s, gambar = %s WHERE id = %s', (judul, isi, tanggal, filename, id))
        else:
            cursor.execute('UPDATE informasi SET judul = %s, isi = %s, tanggal = %s WHERE id = %s', (judul, isi, tanggal, id))
        connection.commit()
        cursor.close()
        connection.close()
        flash('Informasi updated successfully!', 'success')
        return redirect(url_for('admin_informasi'))

    cursor.execute('SELECT * FROM informasi WHERE id = %s', (id,))
    informasi_item = cursor.fetchone()
    cursor.close()
    connection.close()

    return render_template('admin/edit_informasi.html', informasi_item=informasi_item)

@app.route('/admin/informasi/delete/<int:id>', methods=['POST'])
def delete_informasi(id):
    if 'logged_in' not in session:
        return redirect(url_for('admin_login'))

    connection = db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute('DELETE FROM informasi WHERE id = %s', (id,))
        connection.commit()
        flash('Informasi deleted successfully!', 'success')
    except Error as e:
        logging.error(f"Error deleting data: {str(e)}")
        flash('Error deleting informasi', 'danger')
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('admin_informasi'))

# Route Admin Struktur
@app.route('/admin/struktur', methods=['GET', 'POST'])
def admin_struktur():
    if 'logged_in' not in session:
        return redirect(url_for('admin_login'))

    connection = db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == 'POST':
        nama = request.form.get('nama')
        posisi = request.form.get('posisi')
        file = request.files.get('gambar')

        if file and file.filename:
            filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
        else:
            filename = None

        try:
            cursor.execute(
                'INSERT INTO struktur (nama, posisi, gambar) VALUES (%s, %s, %s)',
                (nama, posisi, filename)
            )
            connection.commit()
            flash('Struktur added successfully!', 'success')
        except Error as e:
            logging.error(f"Error inserting data: {str(e)}")
            flash('Error adding struktur', 'danger')
        finally:
            cursor.close()
            connection.close()

    connection = db_connection() 
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM struktur')
    struktur_list = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('admin/struktur.html', struktur_list=struktur_list, active_page='struktur')

@app.route('/admin/struktur/edit/<int:id>', methods=['GET', 'POST'])
def edit_struktur(id):
    if 'logged_in' not in session:
        return redirect(url_for('admin_login'))

    connection = db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == 'POST':
        nama = request.form['nama']
        posisi = request.form['posisi']
        if 'gambar' in request.files:
            file = request.files['gambar']
            if file:
                filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                cursor.execute('UPDATE struktur SET nama = %s, posisi = %s, gambar = %s WHERE id = %s', (nama, posisi, filename, id))
        else:
            cursor.execute('UPDATE struktur SET nama = %s, posisi = %s WHERE id = %s', (nama, posisi, id))
        connection.commit()
        cursor.close()
        connection.close()
        flash('Struktur updated successfully!', 'success')
        return redirect(url_for('admin_struktur'))

    cursor.execute('SELECT * FROM struktur WHERE id = %s', (id,))
    struktur_item = cursor.fetchone()
    cursor.close()
    connection.close()

    return render_template('admin/edit_struktur.html', struktur_item=struktur_item)

@app.route('/admin/struktur/delete/<int:id>', methods=['POST'])
def delete_struktur(id):
    if 'logged_in' not in session:
        return redirect(url_for('admin_login'))

    connection = db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute('DELETE FROM struktur WHERE id = %s', (id,))
        connection.commit()
        flash('Struktur deleted successfully!', 'success')
    except Error as e:
        logging.error(f"Error deleting data: {str(e)}")
        flash('Error deleting struktur', 'danger')
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('admin_struktur'))

# Route Admin Galeri
@app.route('/admin/galeri', methods=['GET', 'POST'])
def admin_galeri():
    if 'logged_in' not in session:
        return redirect(url_for('admin_login'))

    connection = db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == 'POST':
        if 'add' in request.form:
            file = request.files['file']
            keterangan = request.form['keterangan']
            if file:
                filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                try:
                    cursor.execute('INSERT INTO galeri (foto, keterangan) VALUES (%s, %s)', (filename, keterangan))
                    connection.commit()
                    flash('Galeri added successfully!', 'success')
                except Error as e:
                    logging.error(f"Error inserting data: {str(e)}")
                    flash('Error adding galeri', 'danger')
        elif 'delete' in request.form:
            id = request.form['id']
            try:
                cursor.execute('DELETE FROM galeri WHERE id = %s', (id,))
                connection.commit()
                flash('Galeri deleted successfully!', 'success')
            except Error as e:
                logging.error(f"Error deleting data: {str(e)}")
                flash('Error deleting galeri', 'danger')

    cursor.execute('SELECT * FROM galeri')
    galeri_list = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('admin/galeri.html', galeri_list=galeri_list, active_page='galeri')

@app.route('/admin/galeri/edit/<int:id>', methods=['GET', 'POST'])
def edit_galeri(id):
    if 'logged_in' not in session:
        return redirect(url_for('admin_login'))

    connection = db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == 'POST':
        keterangan = request.form['keterangan']
        if 'file' in request.files:
            file = request.files['file']
            if file:
                filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                cursor.execute('UPDATE galeri SET foto = %s, keterangan = %s WHERE id = %s', (filename, keterangan, id))
        else:
            cursor.execute('UPDATE galeri SET keterangan = %s WHERE id = %s', (keterangan, id))
        connection.commit()
        cursor.close()
        connection.close()
        flash('Galeri updated successfully!', 'success')
        return redirect(url_for('admin_galeri'))

    cursor.execute('SELECT * FROM galeri WHERE id = %s', (id,))
    galeri_item = cursor.fetchone()
    cursor.close()
    connection.close()

    return render_template('admin/edit_galeri.html', galeri_item=galeri_item)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(debug=True)
