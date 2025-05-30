from sklearn.linear_model import LogisticRegression
from models import Match, Team
from database import db
import numpy as np

def train_model():
    try:
        matches = Match.query.filter(Match.score.isnot(None)).all()
        if len(matches) < 10:
            print("Not enough matches to train model.")
            return
        
        X = []
        y = []
        for match in matches:
            if not match.score or '-' not in match.score:
                continue
            team1_goals, team2_goals = map(int, match.score.split('-'))
            X.append([match.team1_id, match.team2_id, team1_goals - team2_goals])
            y.append(1 if team1_goals > team2_goals else (0 if team1_goals == team2_goals else -1))
        
        if len(set(y)) < 2:
            print("Not enough outcome classes to train model.")
            return
        
        model = LogisticRegression()
        model.fit(X, y)
        print("Model trained successfully.")
    except Exception as e:
        print(f"Error training model: {e}")

def predict_outcome(team1_id, team2_id):
    matches = Match.query.filter(
        ((Match.team1_id == team1_id) | (Match.team2_id == team1_id) |
         (Match.team1_id == team2_id) | (Match.team2_id == team2_id)) &
        (Match.score.isnot(None))
    ).all()
    
    if len(matches) < 5:
        team1 = Team.query.get(team1_id)
        team2 = Team.query.get(team2_id)
        return f"Insufficient data. Default prediction: {team1.name} 1-1 {team2.name}"
    
    X = []
    for match in matches:
        if not match.score or '-' not in match.score:
            continue
        team1_goals, team2_goals = map(int, match.score.split('-'))
        X.append([match.team1_id, match.team2_id, team1_goals - team2_goals])
    
    if not X:
        team1 = Team.query.get(team1_id)
        team2 = Team.query.get(team2_id)
        return f"Insufficient data. Default prediction: {team1.name} 1-1 {team2.name}"
    
    try:
        model = LogisticRegression()
        y = [1 if x[2] > 0 else (0 if x[2] == 0 else -1) for x in X]
        model.fit(X, y)
        prediction = model.predict([[team1_id, team2_id, 0]])
        team1 = Team.query.get(team1_id)
        team2 = Team.query.get(team2_id)
        if prediction[0] == 1:
            return f"Predicted: {team1.name} wins 2-1"
        elif prediction[0] == 0:
            return f"Predicted: {team1.name} 1-1 {team2.name}"
        else:
            return f"Predicted: {team2.name} wins 2-1"
    except ValueError as e:
        raise ValueError("No sufficient data to make a prediction. Add more matches with valid scores.")