from flask import Flask, render_template, url_for, request, redirect, g
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id


@app.route('/')
def landing():
    return render_template('landing.html')


@app.route('/assignment/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        new_task = Todo(content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/assignment/')
        except:
            return 'There was an issue adding your task'

    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('assignment/index.html', tasks=tasks)


@app.route('/assignment/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/assignment/')
    except:
        return 'There was a problem deleting that task'


@app.route('/assignment/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)

    if request.method == 'POST':
        task.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/assignment/')
        except:
            return 'There was an issue updating your task'

    else:
        return render_template('assignment/update.html', task=task)

###################################################


DATABASE = "test.db"  # SQLite database file

# Ensure database exists
def get_db():
    if not hasattr(g, "_database"):
        g._database = sqlite3.connect(DATABASE)
        g._database.row_factory = sqlite3.Row  # Allow dictionary-like access
    return g._database


@app.teardown_appcontext
def close_connection(exception):
    db1 = getattr(g, "_database", None)
    if db1 is not None:
        db1.close()


# Create the database table if it doesn't exist
def initialize_db():
    db1 = get_db()
    db1.execute(
        """
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workout_type TEXT NOT NULL,
            duration INTEGER NOT NULL,
            date TEXT NOT NULL
        )
        """
    )
    db1.commit()



'''
# Initialize database table
initialize_db()
'''


# Routes
'''@app.route('/')
def landing():
    return render_template('landing.html')
'''

@app.route('/finalproject/')
def dashboard():
    return render_template("finalproject/dashboard.html")


@app.route('/finalproject/log_workout', methods=["GET", "POST"])
def log_workout():
    if request.method == "POST":
        workout_type = request.form['workout_type']
        duration = request.form['duration']
        date = request.form['date']

        db1 = get_db()
        db1.execute(
            "INSERT INTO workouts (workout_type, duration, date) VALUES (?, ?, ?)",
            (workout_type, duration, date),
        )
        db1.commit()
        return redirect(url_for("view_logs"))

    return render_template("finalproject/log_workout.html")


@app.route('/finalproject/view_logs')
def view_logs():
    db1 = get_db()
    logs = db1.execute("SELECT * FROM workouts").fetchall()
    return render_template("finalproject/view_log.html", logs=logs)


@app.route('/finalproject/update_workout/<int:id>', methods=["GET", "POST"])
def update_workout(id):
    db1 = get_db()
    if request.method == "POST":
        workout_type = request.form['workout_type']
        duration = request.form['duration']
        date = request.form['date']

        db1.execute(
            "UPDATE workouts SET workout_type=?, duration=?, date=? WHERE id=?",
            (workout_type, duration, date, id),
        )
        db1.commit()
        return redirect(url_for("view_logs"))

    workout = db1.execute("SELECT * FROM workouts WHERE id=?", (id,)).fetchone()
    return render_template("finalproject/update_workout.html", workout=workout)


@app.route('/finalproject/delete_workout/<int:id>', methods=["GET"])
def delete_workout(id):
    db1 = get_db()
    db1.execute("DELETE FROM workouts WHERE id=?", (id,))
    db1.commit()
    return redirect(url_for("view_logs"))

###################################################

if __name__ == "__main__":
    with app.app_context():
        initialize_db()
    app.run(debug=True)
