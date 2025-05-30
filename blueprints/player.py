from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g
from models import Player, Team
from forms import PlayerForm
from blueprints.auth import login_required
import os
from werkzeug.utils import secure_filename
from flask import current_app
from database import db

player_bp = Blueprint('player', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'png'}

@player_bp.route('/create/<int:team_id>', methods=['GET', 'POST'])
@login_required
def create(team_id):
    team = Team.query.get_or_404(team_id)
    if team.user_id != session['user_id'] and g.user.role != 'Admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('team.dashboard'))
    form = PlayerForm()
    if form.validate_on_submit():
        player = Player(
            name=form.name.data,
            position=form.position.data,
            age=form.age.data,
            team_id=team_id
        )
        if form.photo.data:
            if allowed_file(form.photo.data.filename):
                filename = secure_filename(form.photo.data.filename)
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                form.photo.data.save(filepath)
                player.photo = filename
            else:
                flash('Invalid file type. Only JPG and PNG allowed.', 'danger')
                return render_template('player/create.html', form=form, team=team)
        db.session.add(player)
        db.session.commit()
        flash('Player created successfully!', 'success')
        return redirect(url_for('team.dashboard'))
    return render_template('player/create.html', form=form, team=team)

@player_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    player = Player.query.get_or_404(id)
    if player.team.user_id != session['user_id'] and g.user.role != 'Admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('team.dashboard'))
    form = PlayerForm(obj=player)
    if form.validate_on_submit():
        player.name = form.name.data
        player.position = form.position.data
        player.age = form.age.data
        if form.photo.data:
            if allowed_file(form.photo.data.filename):
                filename = secure_filename(form.photo.data.filename)
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                form.photo.data.save(filepath)
                player.photo = filename
            else:
                flash('Invalid file type. Only JPG and PNG allowed.', 'danger')
                return render_template('player/edit.html', form=form, player=player)
        db.session.commit()
        flash('Player updated successfully!', 'success')
        return redirect(url_for('team.dashboard'))
    return render_template('player/edit.html', form=form, player=player)

@player_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    player = Player.query.get_or_404(id)
    if player.team.user_id != session['user_id'] and g.user.role != 'Admin':
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('team.dashboard'))
    db.session.delete(player)
    db.session.commit()
    flash('Player deleted successfully!', 'success')
    return redirect(url_for('team.dashboard'))