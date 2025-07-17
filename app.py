from flask import Flask, request, render_template_string
import mysql.connector
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

# MySQL connection setup
db = mysql.connector.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME')
)

cursor = db.cursor(dictionary=True)

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
            <input name="password" type="password" placeholder="Password" />
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

@app.route('/')
def home():
    return '''
        <h2 style="text-align:center;">SQL Injection Demo</h2>
        <div style="text-align:center;">
            <a href="/form-insecure">🔓 Insecure Login</a><br><br>
            <a href="/form-secure">🔐 Secure Login</a>
        </div>
    '''

@app.route('/form-insecure', methods=['GET', 'POST'])
def form_insecure():
    response = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        print(f"[INSECURE] Executing: {query}")
        try:
            cursor.execute(query)
            user = cursor.fetchall()
            print(user)
            response = f"✅ Welcome {user}" 
        except Exception as e:
            cursor.fetchall()
            response = f"❌ Error: {str(e)}"
            print(response)
    return render_template_string(HTML_TEMPLATE, form_type="Insecure", action="/form-insecure", response=response)

@app.route('/form-secure', methods=['GET', 'POST'])
def form_secure():
    response = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        print(f"[SECURE] Executing: {query} with {username}, {password}")
        try:
            cursor.execute(query, (username, password))
            user = cursor.fetchone()
            response = f"✅ Welcome {user['username']} (Secure)" if user else "❌ Invalid credentials"
        except Exception as e:
            response = f"❌ Error: {str(e)}"
    return render_template_string(HTML_TEMPLATE, form_type="Secure", action="/form-secure", response=response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8006 ,debug=True)
