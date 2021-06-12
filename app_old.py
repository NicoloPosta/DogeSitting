from flask import Flask, render_template, request
from flask_restful import Api, Resource, marshal_with, reqparse, abort, fields, inputs
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import login

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
from database import *

user_put_parser = reqparse.RequestParser()
user_put_parser.add_argument("user_type", type=bool)
user_put_parser.add_argument("name", type=str, help="Nome dell'utente non inserito")
user_put_parser.add_argument("email", type=str, help="Email non inserita")
user_put_parser.add_argument("passwd", type=str, help="Password non inserita")


schedule_put_parser = reqparse.RequestParser()
schedule_put_parser.add_argument("dogsitter_id", type=int)
schedule_put_parser.add_argument("location", type=str)
schedule_put_parser.add_argument("date_start", type=str)
schedule_put_parser.add_argument("date_end", type=str)
schedule_put_parser.add_argument("max_dogs", type=int)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/appointment')
def appointment():
    return render_template('appointment.html')


resource_fields_schedules = {
    'appointment_id': fields.Integer,
    'dogsitter_id': fields.Integer,
    'location': fields.String,
    'appointment_start': fields.DateTime,
    'appointment_end': fields.DateTime,
    'max_dog_number': fields.Integer
}

resource_fields_users = {
    'id': fields.Integer,
    'email': fields.String,
    'username': fields.String,
    'password': fields.String,
    'user_type':  fields.Boolean
}

class AddUsers(Resource):
    def post(self):
        request = user_put_parser.parse_args()

        #controlla se la lista è vuote e inizializza il primo elemento id a 0
        if not UserTable.query.all():
            users = UserTable(id=0,email=request['email'], username=request['name'], password=request['passwd'], user_type=request['user_type'])
            try:
                db.session.add(users)
                db.session.commit()
                return 200
            except:
                return 'Non è stato possibile inserire i dati',400
        #se la lista non è vuota tutti gli id successivi saranno impostati ad il valore dell'id precedente aumentato di 1 
        else:
            max_id = db.session.query(db.func.max(UserTable.id)).scalar()
            users = UserTable(id=(max_id+1), email=request['email'], username=request['name'], password=request['passwd'], user_type=request['user_type'])
            try:
                db.session.add(users)
                db.session.commit()
                return 200
            except:
                return 'Non è stato possibile inserire i dati',400
                

class User(Resource):
    @marshal_with(resource_fields_users)
    def get(self, user_id):
        try:
            return UserTable.query.filter_by(id=user_id).first()
        except:
            return 404


class UsersList(Resource):
    @marshal_with(resource_fields_users)
    def get(self):
        try:
            tmp = UserTable.query.all()
            return tmp
        except:
            return 404


class AddSchedule(Resource):
    def post(self):
        request = schedule_put_parser.parse_args()
        print(request['date_start'])
        tempo = datetime.strptime(request['date_start'],'%Y-%m-%dT%H:%M')
        print(tempo)

        #controlla se la lista è vuote e inizializza il primo elemento id a 0
        if not AvailableDogsitter.query.all():
            schedule = AvailableDogsitter(appointment_id=0,location=request['location'], appointment_start=request['date_start'], appointment_end=request['date_end'], max_dog_number=request['max_dogs'])
            try:
                db.session.add(schedule)
                db.session.commit()
                return 200
            except:
                return 'Non è stato possibile inserire i dati del primo utente'
        #se la lista non è vuota tutti gli id successivi saranno impostati ad il valore dell'id precedente aumentato di 1 
        else:
            max_id = db.session.query(db.func.max(AvailableDogsitter.appointment_id)).scalar()
            schedule = AvailableDogsitter(appointment_id=(max_id+1),location=request['location'], appointment_start=request['date_start'], appointment_end=request['date_end'], max_dog_number=request['max_dogs'])
            try:
                db.session.add(schedule)
                db.session.commit()
                return 200
            except:
                return 'Non è stato possibile inserire i dati'


class ScheduleList(Resource):
    @marshal_with(resource_fields_schedules)
    def get(self):
        try:
            tmp = AvailableDogsitter.query.all()
            return tmp
        except:
            return {"message":"Query non effettuata correttamente"}, 404



api.add_resource(AddUsers, "/api/add_users")
api.add_resource(UsersList, "/api/users")
api.add_resource(User, "/api/user/<int:user_id>")
api.add_resource(AddSchedule, "/api/add_schedule")
api.add_resource(ScheduleList, "/api/schedule_list")


if __name__ == "__main__":
    app.run(debug=True)