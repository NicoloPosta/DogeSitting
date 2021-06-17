from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField, IntegerField, validators, SubmitField
from wtforms_components import TimeField, DateField
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import InputRequired, Email, Length


class SearchForm(FlaskForm):
    location = StringField('Posizione', validators=[InputRequired()])
    date = DateField('Data appuntamento', validators=[InputRequired()])
    dog_number = IntegerField('Numero Cani', validators=[InputRequired(), validators.NumberRange(min=1, max=99, message="Numero di cani non valido...")])
    time_start = TimeField('Orario inizio', format='%H:%M', validators=[InputRequired()])
    time_end = TimeField('Orario fine', format='%H:%M', validators=[InputRequired()])
    search = SubmitField('Cerca')

class UserForm(FlaskForm):
    name = StringField('Nome', validators=[Length(min=1, max=15)])
    surname = StringField('Cognome', validators=[Length(min=1, max=25)])
    sex = StringField('Sesso', validators=[Length(min=1, max=15)])
    tel_number = IntegerField('Numero di telefono')
    birth_date = DateField('Data di nascita')
    description = StringField('Descrizione', validators=[Length(min=1, max=200)])
    submit = SubmitField('Modifica')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember me')
    login = SubmitField('Login')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Email non valida'), Length(max=50)])
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    usertype = BooleanField('Dogsitter')
    register = SubmitField('Signup')

class AppointmentForm(FlaskForm):
    dog_number = IntegerField('Numero Cani', validators=[InputRequired(), validators.NumberRange(min=1, max=99, message="Numero di cani non valido...")])
    location = StringField('Posizione', validators=[InputRequired()])
    date = DateField('Data appuntamento', validators=[InputRequired()])
    time_start = TimeField('Orario inizio', format='%H:%M', validators=[InputRequired()])
    time_end = TimeField('Orario fine', format='%H:%M', validators=[InputRequired()])


    
    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False
        
        if self.time_end.data <= self.time_start.data:
            self.time_end.errors.append("Inserire un orario valido")
            return False

        return True



