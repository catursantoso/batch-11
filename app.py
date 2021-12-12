from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask.helpers import flash
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate('firebase.json')
firebase_admin.initialize_app(cred)

database = firestore.client()

app = Flask(__name__)
app.secret_key = 'ljaodhfvbhjafdpicvaghi0fuqwyvf098q374r9832y40r8173ycr-9813y4rv9387yr9jaihdfiouahasdf'



@app.route('/')
def index():
    if 'login' not in session:
        return redirect(url_for('login'))
    listMahasiswa = []
    docs = database.collection('users').order_by('nilai', direction=firestore.Query.DESCENDING).stream()
    for doc in docs:
        mhs = doc.to_dict()
        mhs['id'] = doc.id
        listMahasiswa.append(mhs)
    return render_template('index.html', listMahasiswa=listMahasiswa)
    # untuk menampilkan dalam bentuk API
    # return jsonify(listMahasiswa)

@app.route('/api/<uid>')
def detailMhs(uid):
    mhs = database.collection('users').document(uid).get().to_dict()
    return jsonify(mhs['deskripsi'])

@app.route('/dashboard', methods = ['GET', 'POST'])
def dashboard():
    if 'login' not in session:
        return redirect(url_for('login'))
    
    if request.method == "POST":
        # update data
        doc_ref = database.collection('users').document(session['user_id'])
        data  = {
            'nama': request.form['username'],
            'nilai': int(request.form['nilai']),
            'deskripsi': request.form['deskripsi']
        }
        doc_ref.update(data)
        session['pengguna'] = data
        return render_template('dashboard.html')
    # untuk mengupdate session jika ada perubahan
    session['pengguna'] = database.collection('users').document(session['user_id']).get().to_dict()
    # untuk mengupdate session jika ada perubahan

    return render_template('dashboard.html')

@app.route('/about')
def about():
    if 'login' not in session:
        return redirect(url_for('login'))
    mhs = database.collection('users').document(session['user_id']).get().to_dict()
    return render_template('about.html', mhs=mhs)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    pesan = ''
    if request.method == 'POST':

        docs = database.collection('users').stream()
        for doc in docs:
            mhs = doc.to_dict()
            if request.form['username'] == mhs['nama']:
                if request.form['password'] == mhs['password']:
                    session['login'] = True
                    session['pengguna'] = mhs
                    # untuk menampilkan id di dashboard
                    session['user_id'] = doc.id
                    return redirect(url_for('index'))
                else:
                    pesan = 'Password anda salah'
                break
            else:
                pesan = 'Username anda salah'
    return render_template('login.html', pesan = pesan, status = 'danger')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/hapus/<uid>')
def hapus(uid):
    database.collection('users').document(uid).delete()
    return redirect(url_for('index'))



@app.route('/register', methods = ['GET', 'POST'])
def register():
    pesan = ""
    if request.method == 'POST':
        data = {
            'nama': request.form['username'],
            'nilai': int(request.form['nilai']),
            'deskripsi': request.form['deskripsi'],
            'password': request.form['password']
        }
        database.collection('users').add(data)
        pesan = 'Akun berhasil dibuat'
        return render_template('login.html', pesan=pesan , status = 'success')
    return render_template('register.html', pesan=pesan)




if __name__ == '__main__':
    app.run(debug=True)