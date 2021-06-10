from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_restful import Api, Resource, marshal_with, reqparse, abort, fields

app = Flask(__name__)
api = Api(app)
appointment_put_parser = reqparse.RequestParser()
appointment_put_parser.add_argument("user_type", type=bool)
appointment_put_parser.add_argument("name", type=str, help="Nome dell'utente non inserito")
appointment_put_parser.add_argument("email", type=str, help="Email non inserita")
appointment_put_parser.add_argument("passwd", type=str, help="Password non inserita")

@app.route('/')
def index():
    return render_template('index.html')

resource_fields = {
    'email': fields.String,
    'username': fields.String,
    'password': fields.String,
    'user_type':  fields.Boolean
}

class Appointment(Resource):
    def post(self):
        request = appointment_put_parser.parse_args()
        users = UserTable(email=request['email'], username=request['name'], password=request['passwd'], user_type=request['user_type'])
        db.session.add(users)
        db.session.commit()
        return {"email":request['email'],
                "username":request['name'],
                "password":request['passwd'],
                "user_type":request['user_type'],
        }


class AppointmentList(Resource):
    @marshal_with(resource_fields)
    def get(self, appointment_number):
        tmp = UserTable.query.all()
        return tmp


api.add_resource(Appointment, "/appointment")
api.add_resource(AppointmentList, "/appointment/<int:appointment_number>")


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