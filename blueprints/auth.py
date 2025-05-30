from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from forms import RegistrationForm, LoginForm
from functools import wraps
from database import db
from models import User
import sqlalchemy.exc

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        user = User.query.get(session['user_id'])
        if user.is_blocked:
            flash('Your account is blocked.', 'danger')
            return redirect(url_for('auth.logout'))
        g.user = user
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists.', 'danger')
            return render_template('auth/register.html', form=form)
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already exists.', 'danger')
            return render_template('auth/register.html', form=form)
        user = User(username=form.username.data, email=form.email.data, role='User')
        user.set_password(form.password.data)
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        except sqlalchemy.exc.IntegrityError as e:
            db.session.rollback()
            flash('Error creating account. Please try again.', 'danger')
            print(f"IntegrityError: {e}")
    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            if user.is_blocked:
                flash('Your account is blocked.', 'danger')
                return render_template('auth/login.html', form=form)
            session['user_id'] = user.id
            flash('Logged in successfully!', 'success')
            return redirect(url_for('team.dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('auth.login'))