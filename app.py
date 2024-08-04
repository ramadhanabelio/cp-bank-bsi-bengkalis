from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'

dummy_username = 'admin'
dummy_password = 'password123'

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
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username == dummy_username and password == dummy_password:
            session['logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Username atau Password salah!', 'danger')
            return redirect(url_for('admin_login'))
    
    return render_template('admin/login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'logged_in' in session:
        return render_template('admin/dashboard.html')
    else:
        flash('Anda harus login terlebih dahulu!', 'warning')
        return redirect(url_for('admin_login'))

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
    session.pop('logged_in', None)
    flash('Anda telah berhasil logout.', 'success')
    return redirect(url_for('admin_login'))

if __name__ == '__main__':
    app.run(debug=True)
