from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from forms import TeamForm
from blueprints.auth import login_required
from models import Team, Player, Match, db
import os
from werkzeug.utils import secure_filename
from flask import current_app
import sqlalchemy.exc

team_bp = Blueprint('team', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'png'}

@team_bp.route('/dashboard')
@login_required
def dashboard():
    if g.user.role == 'Admin':
        teams = Team.query.all()
    else:
        teams = Team.query.filter_by(user_id=session['user_id']).all()
    return render_template('team/dashboard.html', teams=teams)

@team_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = TeamForm()
    if form.validate_on_submit():
        team = Team(
            name=form.name.data,
            coach=form.coach.data,
            founded_year=form.founded_year.data,
            user_id=session['user_id']
        )
        if form.logo.data:
            if allowed_file(form.logo.data.filename):
                filename = secure_filename(form.logo.data.filename)
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                form.logo.data.save(filepath)
                team.logo = filename
            else:
                flash('Invalid file type. Only JPG and PNG allowed.', 'danger')
                return render_template('team/create.html', form=form)
        db.session.add(team)
        db.session.commit()
        flash('Team created successfully!', 'success')
        return redirect(url_for('team.dashboard'))
    return render_template('team/create.html', form=form)

@team_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    team = Team.query.get_or_404(id)
    if team.user_id != session['user_id'] and g.user.role != 'Admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('team.dashboard'))
    form = TeamForm(obj=team)
    if form.validate_on_submit():
        team.name = form.name.data
        team.coach = form.coach.data
        team.founded_year = form.founded_year.data
        if form.logo.data:
            if allowed_file(form.logo.data.filename):
                filename = secure_filename(form.logo.data.filename)
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                form.logo.data.save(filepath)
                team.logo = filename
            else:
                flash('Invalid file type. Only JPG and PNG allowed.', 'danger')
                return render_template('team/edit.html', form=form, team=team)
        db.session.commit()
        flash('Team updated successfully!', 'success')
        return redirect(url_for('team.dashboard'))
    return render_template('team/edit.html', form=form, team=team)

@team_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    team = Team.query.get_or_404(id)
    if team.user_id != session['user_id'] and g.user.role != 'Admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('team.dashboard'))
    try:
        # Explicitly delete associated players to avoid ORM issues
        Player.query.filter_by(team_id=id).delete()
        db.session.delete(team)
        db.session.commit()
        flash('Team deleted successfully!', 'success')
    except sqlalchemy.exc.IntegrityError as e:
        db.session.rollback()
        flash('Error deleting team due to database constraints.', 'danger')
        print(f"IntegrityError: {e}")
    return redirect(url_for('team.dashboard'))

@team_bp.route('/view/<int:id>')
@login_required
def view(id):
    team = Team.query.get_or_404(id)
    if team.user_id != session['user_id'] and g.user.role != 'Admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('team.dashboard'))
    players = Player.query.filter_by(team_id=id).all()
    matches = Match.query.filter((Match.team1_id == id) | (Match.team2_id == id)).all()
    return render_template('team/view.html', team=team, players=players, matches=matches)