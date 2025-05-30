from flask import Flask, redirect, url_for, g, session
from dotenv import load_dotenv
from init import init_app
from flask_wtf.csrf import CSRFProtect
from models import User

app = Flask(__name__)
app.config['SECRET_KEY'] = '7f8e9d0c1b2a3f4e5d6c7b8a9f0e1d2c'
csrf = CSRFProtect(app)

load_dotenv()

init_app(app)

@app.route('/')
def index():
    return redirect(url_for('auth.login'))

@app.before_request
def load_user():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)