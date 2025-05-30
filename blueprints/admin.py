from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import User
from forms import UserManagementForm
from functools import wraps
from database import db

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('auth.login'))
        user = User.query.get(session['user_id'])
        if user.role != 'Admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('team.dashboard'))
        if user.is_blocked:
            flash('Your account is blocked.', 'danger')
            return redirect(url_for('auth.logout'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/users', methods=['GET'])
@admin_required
def manage_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/user/<int:id>/manage', methods=['GET', 'POST'])
@admin_required
def manage_user(id):
    user = User.query.get_or_404(id)
    form = UserManagementForm(obj=user)
    if form.validate_on_submit():
        user.role = form.role.data
        user.is_blocked = form.is_blocked.data
        db.session.commit()
        flash(f'User {user.username} updated successfully.', 'success')
        return redirect(url_for('admin.manage_users'))
    return render_template('admin/manage_user.html', form=form, user=user)