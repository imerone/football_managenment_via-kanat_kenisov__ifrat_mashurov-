# football_management

football_management/
├── app.py
├── models.py
├── forms.py
├── report.tex
├── blueprints/
│   ├── __init__.py
│   ├── auth.py
│   ├── team.py
│   ├── player.py
│   ├── match.py
├── static/
│   ├── css/
│   │   ├── style.css
│   ├── uploads/
├── templates/
│   ├── base.html
│   ├── auth/
│   │   ├── login.html
│   │   ├── register.html
│   ├── team/
│   │   ├── dashboard.html
│   │   ├── create.html
│   │   ├── edit.html
│   ├── player/
│   │   ├── create.html
│   │   ├── edit.html
│   ├── match/
│   │   ├── create.html
│   │   ├── edit.html
│   │   ├── list.html
│   │   ├── search.html

Football Management System
A Flask-based web application for managing football teams, players, and matches, with user authentication, role-based access, and AI-powered match outcome prediction.
Features

User Authentication: Register, login, and logout functionality.
Team Management: Create, edit, delete, and view teams with logos.
Player Management: Add, edit, and delete players with photos.
Match Management: Schedule, edit, delete, and search matches.
AI Integration: Predict match outcomes using a logistic regression model based on team size and average player age.
Role-Based Access:
User: Default role, can manage own teams/players/matches.
Admin: Can manage all data, block/unblock users, and change user roles.



Setup

Clone the repository:git clone https://github.com/imerone/football_management.git
cd football_management


Create a virtual environment and install dependencies:python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt


Set up environment variables:Create a .env file with:SECRET_KEY=your-secret-key


Initialize the database:python force_db.py


Run the application:python app.py

Access at http://localhost:5000.

AI Integration: Match Outcome Prediction

Purpose: Predicts the likely outcome (Team 1 win, Team 2 win, or draw) for a match based on team size and average player age.
Implementation:
Uses scikit-learn's LogisticRegression model.
Trained on historical match data (team player count, average player age, and past scores).
Model is saved as match_predictor.pkl in static/uploads.
Accessible via a "Predict Outcome" button on match create/edit pages.


How It Works:
Features: Difference in player count and average player age between teams.
Labels: 1 (Team 1 wins), 0 (draw), -1 (Team 2 wins) based on match scores.
Training occurs on app startup and database reset.
Predictions are fetched via /match/predict/<team1_id>/<team2_id> using AJAX.


Limitations:
Requires sufficient match data for accurate predictions.
Simple model; could be enhanced with more features (e.g., player performance stats).



Role-Based Access

User Role: Assigned to new users. Can manage their own teams, players, and matches.
Admin Role: Can manage all teams/players/matches, block/unblock users, and change roles via /admin/users.
Security:
Blocked users cannot log in.
Admin actions are restricted by the admin_required decorator.
CSRF protection is enabled for all forms.



Database Schema

User: id, username, password_hash, email, created_at, role (User/Admin), is_blocked (boolean).
Team: id, name, coach, founded_year, logo, user_id (foreign key).
Player: id, name, position, age, photo, team_id (foreign key).
Match: id, team1_id, team2_id, score, date.

Future Improvements

Add unit tests for routes and models.
Enhance AI model with more features (e.g., player performance stats).
Integrate LaTeX report generation for match summaries.
Add pagination for large lists of matches/users.
Deploy to a production server (e.g., Heroku, Render).

