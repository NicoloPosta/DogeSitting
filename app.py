from logging import error
from flask import Flask, json, render_template, redirect, url_for, jsonify, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField, IntegerField, validators, SubmitField
from wtforms_components import TimeField, DateField
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_json import as_json
import requests


app = Flask(__name__)
app.config['SECRET_KEY'] = 'WhenInDoubtWhipItOut'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from database import *
db.create_all()



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    usertype = BooleanField('tipo di utenza')
    #signup = SubmitField('Registrati')

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


@app.route('/dogsitter_profile_reroute', methods=['GET', 'POST'])
@login_required
def dogsitter_profile():

    if(current_user.user_type == True):
            return redirect(url_for('dogsitter_profile_render'))
    else:
        return redirect(url_for('dashboard'))


@app.route('/user_profile', methods=['GET', 'POST'])
@login_required
def user_profile():

    if(current_user.user_type == True):
            return redirect(url_for('dogsitter_dashboard'))
    else:
        return redirect(url_for('user_profile'))


@app.route('/add_appointment')
@login_required
def add_appointment():

    if(current_user.user_type == True):
            return redirect(url_for('appointment_form'))
    else:
        return redirect(url_for('dashboard'))


@app.route('/appointment_form', methods=['GET', 'POST'])
@login_required
def appointment_form():

    if(current_user.user_type == True):
        form = AppointmentForm()
        if form.validate_on_submit():
            new_appointment = AvailableDogsitter(dogsitter_id=current_user.id , max_dog_number=form.dog_number.data, location=form.location.data, appointment_day=form.date.data, appointment_start=form.time_start.data, appointment_end=form.time_end.data)
            db.session.add(new_appointment)
            db.session.commit()

        return render_template('appointment_form.html', form=form)
    else:
        return redirect(url_for('dashboard'))
        

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    '''
    if login_form.validate_on_submit():
        user = User.query.filter_by(username=login_form.username.data).first()
        if user:
            if check_password_hash(user.password, login_form.password.data):
                login_user(user, remember=login_form.remember.data)
                if(user.user_type == True):
                    return redirect(url_for('dogsitter_dashboard'))
                else:
                    return redirect(url_for('dashboard'))

        #return '<h1>Invalid username or password</h1>'
        return '<h1>' + login_form.username.data + ' ' + login_form.password.data + '</h1>'

    return render_template('login.html', form=login_form)
    '''
    if login_form.validate_on_submit():
        login_return = requests.post('http://localhost:5000/api/login',
            json={
                'username': login_form.username.data,
                'password': login_form.password.data
            }
        )

        if login_return.ok:
            user = User.query.filter_by(id=login_return.json()['user_id']).first()
            login_user(user, remember=True)
            if user.user_type:
                return redirect(url_for('dogsitter_dashboard'))
            else:
                return redirect(url_for('dashboard'))
        else:
            login_return = login_return.json()
            if 'username' in login_return:
                login_form.username.errors = [login_return['username']]
            if 'password' in login_return:
                login_form.password.errors = [login_return['password']]

    return render_template('login.html', form=login_form)


@app.route('/signup', methods=['GET','POST'])
def signup():
    signup_form = RegisterForm()

    '''
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password, user_type=form.usertype.data)
        db.session.add(new_user)
        db.session.commit()

        #return '<h1>New user has been created!</h1>'
        return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'
    return render_template('signup.html', form=form)
    '''
    '''
    if signup_form.signup.data and signup_form.validate():
    '''
    if signup_form.validate_on_submit():
        signup_return = requests.post('http://localhost:5000/api/signup',
            json={
                'username': signup_form.username.data,
                'email': signup_form.email.data,
                'password': signup_form.password.data,
                'user_type': signup_form.usertype.data
            }
        ) 

        if signup_return.ok:
            user = User.query.filter_by(id=signup_return.json()['user_id']).first()
            login_user(user, remember=True)
            if user.user_type:
                return redirect(url_for('dogsitter_dashboard'))
            else:
                return redirect(url_for('dashboard'))
        else:
            signup_return = signup_return.json()
            if 'email' in signup_return:
                signup_return.email.errors = [signup_return['email']]
            if 'username' in signup_return:
                signup_return.username.errors = [signup_return['username']]

    return render_template('signup.html', form=signup_form)




@app.route('/dogsitter_profile')
@login_required
def dogsitter_profile_render():
        return render_template('dogsitter_profile.html', id=current_user.id)


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username)


@app.route('/dogsitter_dashboard')
@login_required
def dogsitter_dashboard():
    return render_template('dogsitter_dashboard.html', name=current_user.username, id=current_user.id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


#Api routes
@app.route('/api/signup', methods=['POST'])
def profile_signup():

    new_user_data = request.json

    errors = {}

    #check if username already exists
    if User.query.filter_by(username=new_user_data['username']).first():
        errors['username'] = 'Username già in uso'
    #check if email already exists
    if User.query.filter_by(email=new_user_data['email']).first():
        errors['email'] = 'Email già in uso'

    if not errors:

        #Signup complited
        hashed_password = generate_password_hash(new_user_data['password'], method='sha256')
        new_user = User(username=new_user_data['username'], email=new_user_data['email'], password=hashed_password, user_type=new_user_data['user_type'])
        db.session.add(new_user)
        db.session.commit()
 

        return json.dumps({'user_id': new_user.id}), 200

    return json.dumps(errors), 400


@app.route('/api/login', methods=['POST'])
def profile_login():

    login_data = request.json

    user = User.query.filter_by(username=login_data['username']).first()
    if not user:
        return json.dumps({'username': "Username invalido"}), 400

    if check_password_hash(user.password, login_data['password']):
        return json.dumps({'user_id': user.id}), 200
    else:
        return json.dumps({'password': "Password errata"}), 400



#Utils forse da cambiare




if __name__ == '__main__':
    app.run(debug=True)
