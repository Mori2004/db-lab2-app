import os
import pymysql
import re
import bcrypt
from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-secret-key")

def get_db_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "registration"),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )

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

@app.route("/todos/<int:todo_id>/edit", methods=["POST"])
def edit_todo(todo_id):
    if "user_id" not in session: return redirect(url_for("login"))
    new_title = request.form.get("title", "").strip()
    if new_title:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("UPDATE todos SET title = %s WHERE todo_id = %s AND user_id = %s;", (new_title, todo_id, session["user_id"]))
        conn.close()
    return redirect(url_for("index"))

# ==========================================
# 2. LIBRARY CRUD ROUTES (LAB 3 & LAB 4)
# ==========================================
@app.route('/books')
def list_books():
    if "user_id" not in session: return redirect(url_for("login"))
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("USE library")
        cursor.execute("""
            SELECT b.*, a.name AS author_name, p.name AS publisher_name, c.name AS category_name
            FROM BOOK b
            JOIN AUTHOR a ON b.author_id = a.author_id
            LEFT JOIN PUBLISHER p ON b.publisher_id = p.publisher_id
            LEFT JOIN CATEGORY c ON b.category_id = c.category_id
            ORDER BY b.book_id ASC
        """)
        books = cursor.fetchall()
        cursor.execute("SELECT * FROM AUTHOR ORDER BY name ASC")
        authors = cursor.fetchall()
        cursor.execute("SELECT * FROM PUBLISHER ORDER BY name ASC")
        publishers = cursor.fetchall()
        cursor.execute("SELECT * FROM CATEGORY ORDER BY name ASC")
        categories = cursor.fetchall()
    conn.close()
    return render_template(
        'books.html',
        books=books,
        authors=authors,
        publishers=publishers,
        categories=categories
    )

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
    title = request.form['title'].strip()
    price = request.form['price']
    publish_year = request.form.get('publish_year') or None
    author_id = request.form['author_id']
    publisher_id = request.form.get('publisher_id') or None
    category_id = request.form.get('category_id') or None
    
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("USE library")
        cursor.execute(
            """
            INSERT INTO BOOK (title, price, publish_year, author_id, publisher_id, category_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (title, price, publish_year, author_id, publisher_id, category_id)
        )
        conn.commit()
    conn.close()
    flash('Book added successfully!', 'success')
    return redirect(url_for('list_books'))

@app.route('/authors/add', methods=['POST'])
def add_author():
    if "user_id" not in session: return redirect(url_for("login"))
    name = request.form['name']
    country = request.form['country']
    
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("USE library")
        cursor.execute("INSERT INTO AUTHOR (name, country) VALUES (%s, %s)", 
                       (name, country))
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

# ==========================================
# 3. LAB 4 - PART II SEARCH & REPORT ROUTES
# ==========================================
@app.route('/search-books', methods=['GET'])
def search_books():
    if "user_id" not in session: return redirect(url_for("login"))
    keyword = request.args.get('keyword', '').strip()
    min_price = request.args.get('min_price', '').strip()
    max_price = request.args.get('max_price', '').strip()
    category_id = request.args.get('category_id', '').strip()

    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("USE library")
        cursor.execute("SELECT * FROM CATEGORY ORDER BY name ASC")
        categories = cursor.fetchall()

        # Prepared statement with placeholders (%s) for F2.1 Bonus
        sql = """
            SELECT b.book_id, b.title, b.price, b.publish_year,
                   a.name AS author_name, p.name AS publisher_name, c.name AS category_name
            FROM BOOK b
            JOIN AUTHOR a ON b.author_id = a.author_id
            LEFT JOIN PUBLISHER p ON b.publisher_id = p.publisher_id
            LEFT JOIN CATEGORY c ON b.category_id = c.category_id
            WHERE 1=1
        """
        params = []

        if keyword:
            sql += " AND b.title LIKE %s"
            params.append(f"%{keyword}%")

        if min_price and max_price:
            sql += " AND b.price BETWEEN %s AND %s"
            params.extend([float(min_price), float(max_price)])
        elif min_price:
            sql += " AND b.price >= %s"
            params.append(float(min_price))
        elif max_price:
            sql += " AND b.price <= %s"
            params.append(float(max_price))

        if category_id:
            sql += " AND b.category_id = %s"
            params.append(int(category_id))

        sql += " ORDER BY b.price ASC"
        cursor.execute(sql, tuple(params))
        books = cursor.fetchall()
    conn.close()

    return render_template(
        'search_books.html',
        books=books,
        categories=categories,
        keyword=keyword,
        min_price=min_price,
        max_price=max_price,
        selected_category=category_id
    )


@app.route('/catalogue')
def catalogue():
    if "user_id" not in session: return redirect(url_for("login"))
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("USE library")
        cursor.execute("""
            SELECT b.book_id, b.title, b.price, b.publish_year,
                   a.name AS author_name, p.name AS publisher_name, c.name AS category_name
            FROM BOOK b
            JOIN AUTHOR a ON b.author_id = a.author_id
            LEFT JOIN PUBLISHER p ON b.publisher_id = p.publisher_id
            LEFT JOIN CATEGORY c ON b.category_id = c.category_id
            ORDER BY b.book_id ASC
        """)
        books = cursor.fetchall()
    conn.close()
    return render_template('catalogue.html', books=books)


@app.route('/reports')
def reports():
    if "user_id" not in session: return redirect(url_for("login"))
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("USE library")
        # F2.3 (a)
        cursor.execute("""
            SELECT c.name AS category_name, COUNT(b.book_id) AS book_count, AVG(b.price) AS avg_price
            FROM CATEGORY c
            LEFT JOIN BOOK b ON c.category_id = b.category_id
            GROUP BY c.category_id, c.name
        """)
        category_stats = cursor.fetchall()

        # F2.3 (b)
        cursor.execute("""
            SELECT a.author_id, a.name AS author_name, COUNT(b.book_id) AS book_count
            FROM AUTHOR a
            JOIN BOOK b ON a.author_id = b.author_id
            GROUP BY a.author_id, a.name
            HAVING COUNT(b.book_id) >= 2
        """)
        prolific_authors = cursor.fetchall()

        # F2.3 (c)
        cursor.execute("""
            SELECT SUM(price) AS total_price, MIN(price) AS smallest_price, MAX(price) AS largest_price
            FROM BOOK
        """)
        library_summary = cursor.fetchone()
    conn.close()
    return render_template(
        'reports.html',
        category_stats=category_stats,
        prolific_authors=prolific_authors,
        library_summary=library_summary
    )


@app.route('/loans')
def loans():
    if "user_id" not in session: return redirect(url_for("login"))
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("USE library")
        # F2.4 (a)
        cursor.execute("""
            SELECT l.loan_id, b.title AS book_title, m.name AS member_name, l.loan_date
            FROM LOAN l
            JOIN BOOK b ON l.book_id = b.book_id
            JOIN MEMBER m ON l.member_id = m.member_id
            WHERE l.return_date IS NULL
        """)
        unreturned_loans = cursor.fetchall()

        # F2.4 (b)
        cursor.execute("""
            SELECT m.member_id, m.name, m.email, m.join_date
            FROM MEMBER m
            LEFT JOIN LOAN l ON m.member_id = l.member_id
            WHERE l.loan_id IS NULL
        """)
        inactive_members = cursor.fetchall()

        # F2.4 (c)
        cursor.execute("""
            SELECT b.book_id, b.title, b.price, b.publish_year
            FROM BOOK b
            LEFT JOIN LOAN l ON b.book_id = l.book_id
            WHERE l.loan_id IS NULL
        """)
        unborrowed_books = cursor.fetchall()
    conn.close()
    return render_template(
        'loans.html',
        unreturned_loans=unreturned_loans,
        inactive_members=inactive_members,
        unborrowed_books=unborrowed_books
    )


@app.route('/most-borrowed')
def most_borrowed():
    if "user_id" not in session: return redirect(url_for("login"))
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("USE library")
        # F2.5 (a)
        cursor.execute("""
            SELECT b.book_id, b.title, COUNT(l.loan_id) AS loan_count
            FROM BOOK b
            JOIN LOAN l ON b.book_id = l.book_id
            GROUP BY b.book_id, b.title
            ORDER BY loan_count DESC
            LIMIT 3
        """)
        top_books = cursor.fetchall()

        # F2.5 (b)
        cursor.execute("""
            SELECT m.member_id, m.name, m.email, COUNT(l.loan_id) AS loan_count
            FROM MEMBER m
            JOIN LOAN l ON m.member_id = l.member_id
            GROUP BY m.member_id, m.name, m.email
            ORDER BY loan_count DESC
            LIMIT 1
        """)
        top_member = cursor.fetchone()
    conn.close()
    return render_template('most_borrowed.html', top_books=top_books, top_member=top_member)


@app.route('/authors-books')
def authors_books():
    if "user_id" not in session: return redirect(url_for("login"))
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("USE library")
        # F2.6 (a)
        cursor.execute("""
            SELECT a.author_id, a.name, a.country, COUNT(b.book_id) AS book_count
            FROM AUTHOR a
            LEFT JOIN BOOK b ON a.author_id = b.author_id
            GROUP BY a.author_id, a.name, a.country
        """)
        author_counts = cursor.fetchall()

        # F2.6 (b)
        cursor.execute("""
            SELECT b.book_id, b.title, a.name AS author_name, p.name AS publisher_name, a.country
            FROM BOOK b
            JOIN AUTHOR a ON b.author_id = a.author_id
            JOIN PUBLISHER p ON b.publisher_id = p.publisher_id
            WHERE a.country = p.country
        """)
        local_books = cursor.fetchall()
    conn.close()
    return render_template('authors_books.html', author_counts=author_counts, local_books=local_books)


if __name__ == "__main__":
    app.run(debug=True)