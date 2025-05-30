from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
import os
from database import db

csrf = CSRFProtect()
migrate = Migrate()

def init_app(app):
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', '7f8e9d0c1b2a3f4e5d6c7b8a9f0e1d2c')  # Use env var
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///football.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'static/uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    app.config['SESSION_COOKIE_SECURE'] = False  # False for local dev
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = 1800

    db.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    from blueprints.auth import auth_bp
    from blueprints.team import team_bp
    from blueprints.player import player_bp
    from blueprints.match import match_bp
    from blueprints.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(team_bp, url_prefix='/team')
    app.register_blueprint(player_bp, url_prefix='/player')
    app.register_blueprint(match_bp, url_prefix='/match')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    with app.app_context():
        db.create_all()
        from predict import train_model
        train_model()