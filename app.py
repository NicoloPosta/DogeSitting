from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_restful import Api, Resource, reqparse, abort

app = Flask(__name__)
api = Api(app)
appointment_put_parser = reqparse.RequestParser()


@app.route('/')
def index():
    return render_template('index.html')


class Appointment(Resource):
    def put(self):
        args = appointment_put_parser.parse_args()
        return {args}, 200


api.add_resource(Appointment, "/appointment")


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class DogsittingAppointment(db.Model):
    prenotation_number = db.Column(db.Integer, primary_key=True)
    dogsitter_name = db.Column(db.String(), nullable=False)
    dog_number = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)


class UserTable(db.Model):
    email = db.Column(db.String(), primary_key=True)
    username = db.Column(db.String(), nullable=False)
    password = db.Column(db.String(), nullable=False)
    user_type = db.Column(db.Boolean, nullable=False)#0 per utenti base, 1 per dogsitter


if __name__ == "__main__":
    app.run(debug=True)