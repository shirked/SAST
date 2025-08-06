# app.py - SECURE VERSION
from flask import Flask, request, render_template_string
import sqlite3
import os # Import os module for environment variables

app = Flask(__name__)
# Secure Fix 1: Get secret key from environment variable
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "fallback_insecure_key_for_dev_only")

DATABASE = 'blog.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY, author TEXT, content TEXT)')
        db.commit()

@app.route('/')
def index():
    db = get_db()
    comments = db.execute('SELECT * FROM comments').fetchall()
    db.close()
    # Secure Fix 2: Use Jinja2's auto-escaping for content (Flask does this by default if not using |safe)
    # For demonstration, explicitly show how to render safely if |safe was removed
    return render_template_string('''
        <h1>Simple Blog</h1>
        {% for comment in comments %}
            <p><b>{{ comment.author }}</b>: {{ comment.content }}</p>
        {% endfor %}
        <hr>
        <h2>Add a Comment</h2>
        <form action="/add_comment" method="post">
            Author: <input type="text" name="author"><br>
            Comment: <textarea name="content"></textarea><br>
            <input type="submit" value="Submit">
        </form>
    ''', comments=comments)

@app.route('/add_comment', methods=['POST'])
def add_comment():
    author = request.form['author']
    content = request.form['content']

    db = get_db()
    # Secure Fix 3: Use parameterized queries to prevent SQL Injection
    db.execute("INSERT INTO comments (author, content) VALUES (?, ?)", (author, content))
    db.commit()
    db.close()
    return "Comment added! <a href='/'>Go back</a>"

if __name__ == '__main__':
    init_db()
    app.run(debug=True)