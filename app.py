from flask import Flask, render_template, redirect, url_for, jsonify
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField, IntegerField, validators
from wtforms_components import TimeField, DateField
from wtforms.fields.html5 import DateTimeLocalField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

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
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                if(user.user_type == True):
                    return redirect(url_for('dogsitter_dashboard'))
                else:
                    return redirect(url_for('dashboard'))

        #return '<h1>Invalid username or password</h1>'
        return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'

    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password, user_type=form.usertype.data)
        db.session.add(new_user)
        db.session.commit()

        #return '<h1>New user has been created!</h1>'
        return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

    return render_template('signup.html', form=form)


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


if __name__ == '__main__':
    app.run(debug=True)
