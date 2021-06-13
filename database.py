from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date, time
from app import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    __tablename__='user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    user_type = db.Column(db.Boolean, nullable=False)#0 per utenti base, 1 per dogsitter
    sex = db.Column(db.String(), default=None)
    tel_number = db.Column(db.Integer, default=None)
    name = db.Column(db.String(20), default=None)
    surname = db.Column(db.String(20), default=None)
    birth_date = db.Column(db.Date, default=None)
    description = db.Column(db.String(200), default=None)

    def __repr__(self):
        return f"User('{self.id}', '{self.username}', '{self.password}', '{self.email}', '{self.user_type}')"

    def as_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'password': self.password,
            'user_type': self.user_type
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
    
    def __repr__(self):
        return f"User('{self.id}', '{self.dogsitter_id}', '{self.location}', '{self.max_dog_number}', '{self.appointment_day}', '{self.appointment_start}', '{self.appointment_end}')"

    def as_dict(self):
        return {
            'id': self.id,
            'dogsitter_id': self.dogsitter_id,
            'location': self.location,
            'max_dog_number': self.max_dog_number,
            'appointment_day': self.appointment_day,
            'appointment_start': self.appointment_start,
            'appointment_end': self.appointment_end
        }


class DogsittingAppointment(db.Model):
    __tablename__ = 'dogsittingappointment'
    prenotation_number = db.Column(db.Integer, primary_key=True)
    dogsitter_name = db.Column(db.String(200), nullable=False)
    dog_number = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'))
