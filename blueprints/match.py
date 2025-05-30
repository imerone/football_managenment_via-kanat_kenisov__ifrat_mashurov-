from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, g
from models import Match, Team
from forms import MatchForm, SearchForm
from blueprints.auth import login_required
from predict import predict_outcome, train_model
from database import db
from datetime import datetime
import sqlalchemy.exc

match_bp = Blueprint('match', __name__)

@match_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = MatchForm()
    teams = Team.query.all() if g.user.role == 'Admin' else Team.query.filter_by(user_id=session['user_id']).all()
    
    if not teams:
        flash('No teams available. Please create a team first.', 'danger')
        return redirect(url_for('team.create'))
    
    form.team1_id.choices = [(team.id, team.name) for team in teams]
    form.team2_id.choices = [(team.id, team.name) for team in teams]
    prediction = None
    
    if request.method == 'POST':
        print(f"Raw form data: {request.form}")
        print(f"Date field value: {request.form.get('date')}")
        
    if form.validate_on_submit():
        print(f"Validated form data: {form.data}")
        if form.team1_id.data == form.team2_id.data:
            flash('Teams cannot play against themselves.', 'danger')
            return render_template('match/create.html', form=form, teams=teams, prediction=prediction)
        
        match = Match(
            team1_id=form.team1_id.data,
            team2_id=form.team2_id.data,
            score=form.score.data,
            date=form.date.data
        )
        try:
            db.session.add(match)
            db.session.commit()
            train_model()  # Retrain model after adding a match
            flash('Match created successfully!', 'success')
            return redirect(url_for('match.list'))
        except sqlalchemy.exc.IntegrityError as e:
            db.session.rollback()
            flash('Error creating match due to database constraints.', 'danger')
            print(f"IntegrityError: {e}")
    else:
        print(f"Form errors: {form.errors}")
    
    return render_template('match/create.html', form=form, teams=teams, prediction=prediction)

@match_bp.route('/list')
@login_required
def list():
    if g.user.role == 'Admin':
        matches = Match.query.all()
    else:
        matches = Match.query.join(Team, Match.team1_id == Team.id).filter(Team.user_id == session['user_id']).all()
    for match in matches:
        days_until = (match.date - datetime.utcnow()).days
        match.days_until = max(0, days_until) if days_until > 0 else 0
    return render_template('match/list.html', matches=matches)

@match_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    match = Match.query.get_or_404(id)
    if match.team1.user_id != session['user_id'] and g.user.role != 'Admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('match.list'))
    form = MatchForm(obj=match)
    teams = Team.query.all() if g.user.role == 'Admin' else Team.query.filter_by(user_id=session['user_id']).all()
    form.team1_id.choices = [(team.id, team.name) for team in teams]
    form.team2_id.choices = [(team.id, team.name) for team in teams]
    prediction = None
    if form.validate_on_submit():
        if form.team1_id.data == form.team2_id.data:
            flash('Teams cannot play against themselves.', 'danger')
            return render_template('match/edit.html', form=form, match=match, teams=teams, prediction=prediction)
        match.team1_id = form.team1_id.data
        match.team2_id = form.team2_id.data
        match.score = form.score.data
        match.date = form.date.data
        try:
            db.session.commit()
            train_model()  # Retrain model after editing a match
            flash('Match updated successfully!', 'success')
            return redirect(url_for('match.list'))
        except sqlalchemy.exc.IntegrityError as e:
            db.session.rollback()
            flash('Error updating match due to database constraints.', 'danger')
            print(f"IntegrityError: {e}")
    return render_template('match/edit.html', form=form, match=match, teams=teams, prediction=prediction)

@match_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    match = Match.query.get_or_404(id)
    if match.team1.user_id != session['user_id'] and g.user.role != 'Admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('match.list'))
    try:
        db.session.delete(match)
        db.session.commit()
        train_model()  # Retrain model after deleting a match
        flash('Match deleted successfully!', 'success')
    except sqlalchemy.exc.IntegrityError as e:
        db.session.rollback()
        flash('Error deleting match due to database constraints.', 'danger')
        print(f"IntegrityError: {e}")
    return redirect(url_for('match.list'))

@match_bp.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    form = SearchForm()
    matches = []
    if form.validate_on_submit():
        query = f"%{form.query.data}%"
        if g.user.role == 'Admin':
            matches = Match.query.join(Team, Match.team1_id == Team.id).filter(
                (Team.name.ilike(query)) | (Match.score.ilike(query))
            ).all()
        else:
            matches = Match.query.join(Team, Match.team1_id == Team.id).filter(
                (Team.user_id == session['user_id']) & 
                ((Team.name.ilike(query)) | (Match.score.ilike(query)))
            ).all()
    return render_template('match/search.html', form=form, matches=matches)

@match_bp.route('/predict/<int:team1_id>/<int:team2_id>')
@login_required
def predict(team1_id, team2_id):
    team1 = Team.query.get(team1_id)
    team2 = Team.query.get(team2_id)
    if not team1 or not team2:
        return jsonify({'error': 'One or both teams not found.'}), 404
    if (team1.user_id != session['user_id'] or team2.user_id != session['user_id']) and g.user.role != 'Admin':
        return jsonify({'error': 'Unauthorized access.'}), 403
    try:
        prediction = predict_outcome(team1_id, team2_id)
        return jsonify({'prediction': prediction})
    except ValueError as e:
        print(f"Prediction error: {e}")
        return jsonify({'error': str(e)}), 400