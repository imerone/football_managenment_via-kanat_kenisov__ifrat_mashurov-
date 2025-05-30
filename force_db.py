from database import db
from app import app
from predict import train_model

with app.app_context():
    db.drop_all()
    db.create_all()
    train_model()
    print("Database recreated successfully.")