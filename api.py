from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, json, render_template, redirect, url_for, jsonify, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import requests
from database import *
from form import *
from app import app, login_manager


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


@app.route('/api/appointment_list', methods=['POST'])
def api_appointment_list():

    search_data = request.json

    end_hour = int(time.fromisoformat(search_data['time_end']).strftime("%H"))

    start_hour = int(time.fromisoformat(search_data['time_start']).strftime("%H"))

    search_result = AvailableDogsitter.query.filter_by(location=search_data['location'],appointment_day=date.fromisoformat(search_data['date'])).all()
        
    if search_result == []:
        return {'no_results': "Non ho trovato appuntamenti che soddisfano la ricerca in quel giorno o luogo"}, 400

    return_list=[]

    for appointment in search_result:

        appointment_id = appointment.id


        hours = Dog_per_Hours.query.filter_by(appointment_id=appointment_id).all()
        
        if hours[0].start <= start_hour and hours[-1].end >= end_hour:
            #significa che l'appuntamento può essere preso
            hour_count = end_hour - start_hour
            count = 0
            for hour in hours:
                if (hour.start >= start_hour) and (hour.end <= end_hour):
                    if hour.available_dog_number >= search_data['dog_number']:
                        count += 1

            if count == hour_count:
                return_list.append(appointment.as_dict())
    
    if return_list == []:
        return {'no_results': "Non ho trovato appuntamenti che soddisfano la fascia oraria richiesta o i cani richiesti"}, 400


    return {'return_list': return_list}, 200


@app.route('/api/add_appointment', methods=['POST'])
def add_appointment_api():

    appointment_data = request.json

    appointments = AvailableDogsitter.query.filter_by(dogsitter_id=appointment_data['dogsitter_id'], appointment_day=date.fromisoformat(appointment_data['date'])).all()

    for appointment in appointments:

        # inizia e finisce all'interno di un altro appuntamento
        # inizio_nuovo >= inizio_vecchio and fine_nuovo <= fine vecchio

        # inizia prima ma finisce nel mentre di uno vecchio
        # inizio_nuovo < inizio_vecchio and (fine_nuovo < fine_vecchio and fine_nuovo > inizio_vecchio)

        # inizia nel mentre di uno vecchio e finisce dopo uno vecchio
        # fine_nuovo > fine_vecchio and (inizio_nuovo > inizio_vecchio and inizio_nuovo < fine_vecchio)

        if appointment.appointment_start <= time.fromisoformat(appointment_data['time_start']) and appointment.appointment_end >= time.fromisoformat(appointment_data['time_end']):
            return json.dumps({'time_start': "La fascia oraria scelta si sovrappone ad una già inserita"}), 400

        if  time.fromisoformat(appointment_data['time_start']) < appointment.appointment_start and (time.fromisoformat(appointment_data['time_end']) < appointment.appointment_end and time.fromisoformat(appointment_data['time_end']) > appointment.appointment_start):
            return json.dumps({'time_start': "La fascia oraria scelta si sovrappone ad una già inserita"}), 400

        if time.fromisoformat(appointment_data['time_end']) > appointment.appointment_end and ( time.fromisoformat(appointment_data['time_start']) > appointment.appointment_start and time.fromisoformat(appointment_data['time_start']) < appointment.appointment_end):
            return json.dumps({'time_start': "La fascia oraria scelta si sovrappone ad una già inserita"}), 400

    new_appointment = AvailableDogsitter(dogsitter_id=appointment_data['dogsitter_id'] , max_dog_number=appointment_data['dog_number'], location=appointment_data['location'], appointment_day=date.fromisoformat(appointment_data['date']), appointment_start=time.fromisoformat(appointment_data['time_start']), appointment_end=time.fromisoformat(appointment_data['time_end']))

    
    end_hour = int(time.fromisoformat(appointment_data['time_end']).strftime("%H"))

    start_hour = int(time.fromisoformat(appointment_data['time_start']).strftime("%H"))

    hour_number = end_hour - start_hour

    db.session.add(new_appointment)
    db.session.commit()


    for i in range(hour_number):
        
        new_dog_per_hour = Dog_per_Hours(appointment_id=new_appointment.id, start=start_hour, end=(start_hour+1), available_dog_number=new_appointment.max_dog_number)
        start_hour += 1
        db.session.add(new_dog_per_hour)
        db.session.commit()


    return json.dumps({'appointment_id': new_appointment.id}), 200
