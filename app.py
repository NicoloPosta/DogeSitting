from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
app = Flask(__name__)

@app.route('/')
def index():
    return "Dio Dio"


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class DogsittingAppointment(db.model):
    prenotation_number = db.column(db.Integer, primary_key=True)
    dogsitter_name = db.column(db.String(), nullable=False)
    dog_number = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)


if __name__ == "__main__":
    app.run(debug=True)