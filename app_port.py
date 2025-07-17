from flask import Flask, request, render_template_string
from multiprocessing import Process
import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()

# HTML UI template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>SQL Injection Demo</title>
    <style>
        body {
            font-family: Arial;
            background-color: #f7f7f7;
            padding: 50px;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            width: 400px;
            margin: auto;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        h2 {
            text-align: center;
            margin-top: 0;
        }
        input {
            width: 100%%;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
            border: 1px solid #ccc;
        }
        button {
            width: 100%%;
            padding: 10px;
            background: #28a745;
            color: white;
            border: none;
            border-radius: 5px;
        }
        .response {
            margin-top: 20px;
            font-weight: bold;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>{{ form_type }} Login</h2>
        <form method="POST" action="{{ action }}">
            <input name="username" placeholder="Username" required />
            <input name="password" type="password" placeholder="Password" required />
            <button type="submit">Login</button>
        </form>
        {% if response %}
        <div class="response">{{ response }}</div>
        {% endif %}
        <p style="text-align:center; margin-top:20px;">
            <a href="/">Home</a>
        </p>
    </div>
</body>
</html>
'''

# Shared DB connection
def get_db():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )

# Insecure app
def run_insecure():
    app = Flask(__name__)

    @app.route('/', methods=['GET', 'POST'])
    def login_insecure():
        response = None
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
            print(f"[INSECURE] {query}")
            try:
                db = get_db()
                cursor = db.cursor(dictionary=True)
                cursor.execute(query)
                user = cursor.fetchall()
                print(user)
                response = f"✅ Welcome {user} (Insecure)" if user else "❌ Invalid credentials"
                cursor.close()
                db.close()
            except Exception as e:
                response = f"❌ Error: {str(e)}"
        return render_template_string(HTML_TEMPLATE, mode="Insecure", response=response)

    app.run(host="0.0.0.0", port=8007)

# Secure app
def run_secure():
    app = Flask(__name__)

    @app.route('/', methods=['GET', 'POST'])
    def login_secure():
        response = None
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            query = "SELECT * FROM users WHERE username = %s AND password = %s"
            try:
                db = get_db()
                cursor = db.cursor(dictionary=True)
                cursor.execute(query, (username, password))
                user = cursor.fetchone()
                response = f"✅ Welcome {user['username']} (Secure)" if user else "❌ Invalid credentials"
                cursor.close()
                db.close()
            except Exception as e:
                response = f"❌ Error: {str(e)}"
        return render_template_string(HTML_TEMPLATE, mode="Secure", response=response)

    app.run(host="0.0.0.0", port=8006)

# Run both apps in parallel
if __name__ == '__main__':
    p1 = Process(target=run_insecure)
    p2 = Process(target=run_secure)
    p1.start()
    p2.start()
    p1.join()
    p2.join()

