from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_restful import Api, Resource, marshal_with, reqparse, abort, fields

app = Flask(__name__)
api = Api(app)
user_put_parser = reqparse.RequestParser()
user_put_parser.add_argument("user_type", type=bool)
user_put_parser.add_argument("name", type=str, help="Nome dell'utente non inserito")
user_put_parser.add_argument("email", type=str, help="Email non inserita")
user_put_parser.add_argument("passwd", type=str, help="Password non inserita")

@app.route('/')
def index():
    return render_template('index.html')

resource_fields = {
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
    @marshal_with(resource_fields)
    def get(self, user_id):
        try:
            return UserTable.query.filter_by(id=user_id).first()
        except:
            return 404


class UsersList(Resource):
    @marshal_with(resource_fields)
    def get(self):
        try:
            tmp = UserTable.query.all()
            return tmp
        except:
            return 404


api.add_resource(AddUsers, "/api/add_users")
api.add_resource(UsersList, "/api/users")
api.add_resource(User, "/api/user/<int:user_id>")


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


class UserTable(db.Model):
    __tablename__= 'usertable'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(), nullable=False, unique=True)
    username = db.Column(db.String(), nullable=False)
    password = db.Column(db.String(), nullable=False)
    user_type = db.Column(db.Boolean, nullable=False)#0 per utenti base, 1 per dogsitter


class DogsittingAppointment(db.Model):
    __tablename__ = 'dogsittingappointment'
    prenotation_number = db.Column(db.Integer, primary_key=True)
    dogsitter_name = db.Column(db.String(), nullable=False)
    dog_number = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    userId = db.Column(db.Integer, db.ForeignKey('usertable.id'))


if __name__ == "__main__":
    app.run(debug=True)