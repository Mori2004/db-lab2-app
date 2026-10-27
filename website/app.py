import os
import pymysql
import re
import bcrypt
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-secret-key")

# Setup upload folder
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_db_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "registration"),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )

def save_image(file):
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return filename
    return 'default.png'

# ==========================================
# 1. TO-DO & AUTHENTICATION ROUTES
# ==========================================
@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT todo_id, title, is_done, created_at FROM todos WHERE user_id = %s ORDER BY todo_id DESC;", (session["user_id"],))
        todos = cursor.fetchall()
    conn.close()
    return render_template("index.html", todos=todos, user_name=session.get("user_name"))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            flash('Invalid email format.', 'danger')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))

        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                conn.close()
                flash('Email already registered!', 'danger')
                return redirect(url_for('register'))

            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute("INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)", (name, email, hashed_pw))
            conn.commit()
        conn.close()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT user_id, name, password_hash FROM users WHERE email = %s;", (email,))
            user = cursor.fetchone()
        conn.close()

        if not user or not bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
            flash("Invalid email or password", "danger")
            return render_template("login.html", email=email)

        session["user_id"] = user["user_id"]
        session["user_name"] = user["name"]
        return redirect(url_for("index"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/todos/add", methods=["POST"])
def add_todo():
    if "user_id" not in session: return redirect(url_for("login"))
    title = request.form.get("title", "").strip()
    if title:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO todos (user_id, title) VALUES (%s, %s);", (session["user_id"], title))
        conn.close()
    return redirect(url_for("index"))

@app.route("/todos/<int:todo_id>/toggle", methods=["POST"])
def toggle_todo(todo_id):
    if "user_id" not in session: return redirect(url_for("login"))
    is_done = 1 if request.form.get("is_done") == "1" else 0
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("UPDATE todos SET is_done = %s WHERE todo_id = %s AND user_id = %s;", (is_done, todo_id, session["user_id"]))
    conn.close()
    return redirect(url_for("index"))

@app.route("/todos/<int:todo_id>/delete", methods=["POST"])
def delete_todo(todo_id):
    if "user_id" not in session: return redirect(url_for("login"))
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM todos WHERE todo_id = %s AND user_id = %s;", (todo_id, session["user_id"]))
    conn.close()
    return redirect(url_for("index"))

# ==========================================
# 2. LIBRARY ROUTES (IMAGE UPLOADS ADDED)
# ==========================================
@app.route('/books')
def list_books():
    if "user_id" not in session: return redirect(url_for("login"))
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("USE library")
        cursor.execute("SELECT * FROM BOOK")
        books = cursor.fetchall()
        cursor.execute("SELECT * FROM AUTHOR")
        authors = cursor.fetchall()
    conn.close()
    return render_template('books.html', books=books, authors=authors)

@app.route('/authors')
def list_authors():
    if "user_id" not in session: return redirect(url_for("login"))
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("USE library")
        cursor.execute("SELECT * FROM AUTHOR")
        authors = cursor.fetchall()
    conn.close()
    return render_template('authors.html', authors=authors)

@app.route('/books/add', methods=['POST'])
def add_book():
    if "user_id" not in session: return redirect(url_for("login"))
    title = request.form['title']
    price = request.form['price']
    author_id = request.form['author_id']
    image_filename = save_image(request.files.get('image'))
    
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("USE library")
        cursor.execute("INSERT INTO BOOK (title, price, author_id, image_filename) VALUES (%s, %s, %s, %s)", 
                       (title, price, author_id, image_filename))
        conn.commit()
    conn.close()
    flash('Book added successfully!', 'success')
    return redirect(url_for('list_books'))

@app.route('/authors/add', methods=['POST'])
def add_author():
    if "user_id" not in session: return redirect(url_for("login"))
    name = request.form['name']
    country = request.form['country']
    image_filename = save_image(request.files.get('image'))
    
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("USE library")
        cursor.execute("INSERT INTO AUTHOR (name, country, image_filename) VALUES (%s, %s, %s)", 
                       (name, country, image_filename))
        conn.commit()
    conn.close()
    flash('Author added successfully!', 'success')
    return redirect(url_for('list_authors'))

@app.route('/books/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    if "user_id" not in session: return redirect(url_for("login"))
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("USE library")
        cursor.execute("DELETE FROM BOOK WHERE book_id=%s", (book_id,))
        conn.commit()
    conn.close()
    flash('Book deleted!', 'danger')
    return redirect(url_for('list_books'))

@app.route('/authors/delete/<int:author_id>', methods=['POST'])
def delete_author(author_id):
    if "user_id" not in session: return redirect(url_for("login"))
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("USE library")
        cursor.execute("DELETE FROM AUTHOR WHERE author_id=%s", (author_id,))
        conn.commit()
    conn.close()
    flash('Author deleted!', 'danger')
    return redirect(url_for('list_authors'))

if __name__ == "__main__":
    app.run(debug=True)