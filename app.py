from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Gantilah 'your_secret_key' dengan kunci rahasia yang kuat dan unik

# Data pengguna untuk keperluan contoh
users_data = {
    'diyan': {'password': 'wicak', 'name': 'Diyan'},
    'sandi': {'password': '123', 'name': 'sandi'},
    'fajar': {'password': '123', 'name': 'Fajar'},
    'syaif': {'password': '123', 'name': 'Syaif'},
    'kevin': {'password': '123', 'name': 'kevin'},
    'kimi': {'password': '123', 'name': 'kimi'},
    # Tambahkan pengguna lain jika diperlukan
}

# Data kuis dan materi pembelajaran
quiz_data = [
    {"question": "Apa fungsi dari perintah 'print' dalam Python?", "options": ["Menampilkan output", "Menerima input", "Melakukan perulangan", "Membuat fungsi"], "answer": "Menampilkan output", "name": "radio1"},
    {"question": "Apa hasil dari 3 * 4?", "options": ["5", "8", "10", "12"], "answer": "12", "name": "radio2"},
    {"question": "Apa yang dimaksud dengan variabel dalam pemrograman Python?", "options": ["Bahasa pemrograman", "Tipe data", "Nama untuk menyimpan nilai", "Fungsi matematika"], "answer": "Nama untuk menyimpan nilai", "name": "radio3"},
    {"question": "Bagaimana cara mengambil input dari pengguna dalam bahasa pemrograman Python?", "options": ["input()", "print()", "for loop", "while loop"], "answer": "input()", "name": "radio4"},
    {"question": "Apa itu 'if-else' statement dalam Python?", "options": ["Perulangan", "Kondisional (percabangan)", "Fungsi matematika", "Tipe data"], "answer": "Kondisional (percabangan)", "name": "radio5"},
    {"question": "Berapa hasil dari 2 ** 3?", "options": ["2", "4", "8", "16"], "answer": "8", "name": "radio6"},
    {"question": "Apa itu 'list' dalam Python?", "options": ["Struktur data untuk menyimpan nilai tunggal", "Struktur data untuk menyimpan multiple values", "Fungsi matematika", "Variabel"], "answer": "Struktur data untuk menyimpan multiple values", "name": "radio7"},
    {"question": "Apa yang akan dilakukan oleh perintah 'break' dalam loop?", "options": ["Melanjutkan ke iterasi berikutnya", "Mengakhiri loop", "Mengubah nilai variabel", "Menampilkan output"], "answer": "Mengakhiri loop", "name": "radio8"},
    {"question": "Apa itu 'function' dalam Python?", "options": ["Fungsi matematika", "Kondisional (percabangan)", "Struktur data", "Blok kode yang dapat dipanggil"], "answer": "Blok kode yang dapat dipanggil", "name": "radio9"},
    {"question": "Bagaimana cara menghitung panjang sebuah 'list'?", "options": ["count()", "length()", "size()", "len()"], "answer": "len()", "name": "radio10"},
]

learning_materials = [
    {"title": "Pengenalan Dasar Pemrograman Python", "content": "Python adalah bahasa pemrograman tingkat tinggi..."},
    {"title": "Variabel dan Tipe Data", "content": "Variabel digunakan untuk menyimpan nilai, dan Python memiliki berbagai tipe data..."},
    {"title": "Percabangan (if-else Statement)", "content": "Percabangan digunakan untuk membuat keputusan berdasarkan kondisi tertentu..."},
    {"title": "Perulangan (Loops)", "content": "Loops digunakan untuk melakukan iterasi atau pengulangan dalam program Python..."},
    {"title": "Struktur Data: List", "content": "List adalah struktur data yang dapat digunakan untuk menyimpan sekumpulan nilai..."},
    {"title": "Fungsi (Functions)", "content": "Fungsi digunakan untuk mengorganisir blok kode menjadi unit yang dapat dipanggil..."},
    {"title": "Operasi Matematika Dasar", "content": "Python mendukung berbagai operasi matematika seperti penjumlahan, pengurangan, perkalian, dan pembagian..."},
    {"title": "Manipulasi String", "content": "String adalah tipe data yang digunakan untuk menyimpan teks, dan Python menyediakan berbagai operasi untuk manipulasi string..."},
    {"title": "Percabangan Lanjutan", "content": "Selain 'if-else', Python juga mendukung percabangan lanjutan seperti 'elif'..."},
    {"title": "File Handling", "content": "Python dapat digunakan untuk membaca dan menulis file..."}
]

user_scores = {}
user_answers = {}

# Decorator untuk menentukan rute halaman utama
@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html', static_url_path="/PYTHON/static/style.css")


# Decorator untuk menangani metode POST dari halaman login
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if username in users_data and password == users_data[username]['password']:
        session['username'] = username
        session['user_name'] = users_data[username]['name']
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html', error='Username atau password salah')


# Decorator untuk melindungi halaman dashboard agar hanya dapat diakses setelah login
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['user_name'])
    else:
        return redirect(url_for('home'))


# Decorator untuk melindungi halaman kuis agar hanya dapat diakses setelah login
@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'username' in session:
        if request.method == 'POST':
            # Proses jawaban dari formulir kuis yang dikirimkan
            user_answers_list = request.form.getlist('answer')
            correct_answer = quiz_data[session['question_index']]['answer']
            user_answers[session['question_index']] = {"user_answer": user_answers_list, "correct_answer": correct_answer}

            if user_answers_list == [correct_answer]:
                # Jika jawaban benar, tambahkan skor
                user_scores[session['username']] = user_scores.get(session['username'], 0) + 1

            session['question_index'] += 1

            if session['question_index'] < len(quiz_data):
                return render_template('quiz.html', quiz_data=quiz_data, question_index=session['question_index'])
            else:
                # Jika kuis selesai, simpan ke Excel dan kembali ke dashboard
                save_quiz_results_to_excel()
                return redirect(url_for('score'))
        else:
            # Atur indeks pertanyaan untuk sesi pengguna
            session['question_index'] = 0
            return render_template('quiz.html', quiz_data=quiz_data, question_index=session['question_index'])

    else:
        return redirect(url_for('home'))


# Fungsi untuk menyimpan hasil kuis ke file Excel
def save_quiz_results_to_excel():
    # Cek apakah file Excel sudah ada
    try:
        existing_data = pd.read_excel('quiz_results.xlsx')
    except FileNotFoundError:
        # Jika file belum ada, buat DataFrame kosong
        existing_data = pd.DataFrame(columns=['Username', 'Question Index', 'User Answer', 'Correct Answer'])

    new_data = {
        'Username': [],
        'Question Index': [],
        'User Answer': [],
        'Correct Answer': [],
    }

    for question_index, answer in user_answers.items():
        for i in range(len(answer['user_answer'])):
            new_data['Username'].append(session['username'])
            new_data['Question Index'].append(question_index)
            new_data['User Answer'].append(answer['user_answer'][i])
            new_data['Correct Answer'].append(answer['correct_answer'])

    # Gabungkan data baru dengan data yang sudah ada
    combined_data = pd.concat([existing_data, pd.DataFrame(new_data)])

    # Simpan ke file Excel tanpa index
    combined_data.to_excel('quiz_results.xlsx', index=False)



# Rute untuk menampilkan skor dan jawaban
@app.route('/score')
def score():
    if 'username' in session:
        return render_template('score.html', user_scores=user_scores, user_answers=user_answers)
    else:
        return redirect(url_for('home'))


# Decorator untuk melindungi halaman materi pembelajaran agar hanya dapat diakses setelah login
@app.route('/learning_materials')
def learning_materials_page():
    if 'username' in session:
        return render_template('learning_materials.html', learning_materials=learning_materials)
    else:
        return redirect(url_for('home'))


# Decorator untuk logout
@app.route('/logout')
def logout():
    # Saat pengguna logout, simpan hasil kuis ke Excel dan bersihkan data pengguna
    save_quiz_results_to_excel()
    session.pop('username', None)
    user_scores.clear()
    user_answers.clear()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
