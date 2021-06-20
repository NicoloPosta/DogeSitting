from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, time, date
from app import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    __tablename__='user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    user_type = db.Column(db.Boolean, nullable=False)#0 per utenti base, 1 per dogsitter
    sex = db.Column(db.String(), default="Non inserito")
    tel_number = db.Column(db.Integer, default=000)
    name = db.Column(db.String(20), default="Non inserito")
    surname = db.Column(db.String(20), default="Non Inserito")
    birth_date = db.Column(db.Date, default=datetime.utcnow)
    description = db.Column(db.String(200), default="Non inserito")
    picture = db.Column(db.String(40), default='/static/img/users/default.png')

    def __repr__(self):
        return f"User('{self.id}', '{self.username}', '{self.password}', '{self.email}', '{self.user_type}')"

    def as_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'password': self.password,
            'user_type': self.user_type,
            'sex': self.sex,
            'tel_number': self.tel_number,
            'name': self.name,
            'surname': self.surname,
            'birth_date': self.birth_date.isoformat(),
            'description': self.description,
            'picture': self.picture
        }


class AvailableDogsitter(db.Model):
    __tablename__='availabledogsitter'
    id = db.Column(db.Integer, primary_key=True)
    dogsitter_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    location = db.Column(db.String(200), nullable=False)
    max_dog_number = db.Column(db.Integer, nullable=False)
    appointment_day = db.Column(db.Date, nullable=False)
    appointment_start = db.Column(db.Time, nullable=False)
    appointment_end = db.Column(db.Time, nullable=False)
    appointment_cost = db.Column(db.Integer, nullable=False)


    def as_dict(self):
        return {
            'id': self.id,
            'dogsitter_id': self.dogsitter_id,
            'location': self.location,
            'max_dog_number': self.max_dog_number,
            'appointment_day': self.appointment_day.isoformat(),
            'appointment_start': self.appointment_start.isoformat(),
            'appointment_end': self.appointment_end.isoformat(),
            'appointment_cost': self.appointment_cost
        }


class Dog_per_Hours(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('availabledogsitter.id'))
    start = db.Column(db.Integer, nullable=False)
    end = db.Column(db.Integer, nullable=False)
    available_dog_number = db.Column(db.Integer, nullable=False)


class DogsittingAppointment(db.Model):
    __tablename__ = 'dogsittingappointment'
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('availabledogsitter.id'))
    userId = db.Column(db.Integer, db.ForeignKey('user.id'))
    dog_number = db.Column(db.Integer, nullable=False)
    appointment_date = db.Column(db.DateTime, default=datetime.utcnow)
    location = db.Column(db.String(200), nullable=False)
    appointment_start = db.Column(db.Time, nullable=False)
    appointment_end = db.Column(db.Time, nullable=False)
    appointment_cost = db.Column(db.Integer, nullable=False)

    def as_dict(self):
        return {
            'id': self.id,
            'appointment_id': self.appointment_id,
            'userId': self.userId,
            'dog_number': self.dog_number,
            'appointment_date': self.appointment_date.isoformat(),
            'appointment_start': self.appointment_start.isoformat(),
            'appointment_end': self.appointment_end.isoformat(),
            'location': self.location,
            'appointment_cost': self.appointment_cost
        }
