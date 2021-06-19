from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, json, render_template, redirect, url_for, jsonify, request, abort
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
        return json.dumps({'username_login': "Username invalido"}), 400

    if check_password_hash(user.password, login_data['password']):
        return json.dumps({'user_id': user.id}), 200
    else:
        return json.dumps({'password': "Password errata"}), 400


@app.route('/api/appointment_list', methods=['POST'])
def api_appointment_list():

    search_data = request.json

    end_hour = int(time.fromisoformat(search_data['time_end']).strftime("%H"))

    start_hour = int(time.fromisoformat(search_data['time_start']).strftime("%H"))

    if end_hour <= start_hour:
        return {'hour_error': "L'ora finale è minore dell'iniziale"}, 404

    search_result = AvailableDogsitter.query.filter_by(location=search_data['location'],appointment_day=date.fromisoformat(search_data['date'])).all()

    

    if search_result == []:
        return {'no_results': "Non ho trovato appuntamenti"}, 404

    return_list=[]

    for appointment in search_result:

        appointment_id = appointment.id


        hours = Dog_per_Hours.query.filter_by(appointment_id=appointment_id).all()
        
        searched_dogsitter = User.query.filter_by(id = appointment.dogsitter_id).first()
        
        if hours[0].start <= start_hour and hours[-1].end >= end_hour:
            #significa che l'appuntamento può essere preso
            hour_count = end_hour - start_hour
            count = 0
            for hour in hours:
                if (hour.start >= start_hour) and (hour.end <= end_hour):
                    if hour.available_dog_number >= search_data['dog_number']:
                        count += 1

            if count == hour_count:
                appointment_dict = appointment.as_dict()
                appointment_dict['dogsitter_name'] = searched_dogsitter.name
                return_list.append(appointment_dict)
    
    if return_list == []:
        return {'no_results': "Non ho trovato appuntamenti"}, 404


    return {'return_list': return_list}, 200


@app.route('/api/book_appointment', methods=['POST'])
@login_required
def book_appointment_api():
    
    if(current_user.user_type == True):
            return redirect(url_for('dogsitter_dashboard'))
    else:
        
        booking_request = request.json

        valid_booking_check = requests.post('http://localhost:5000/api/appointment_list',
            json={
                'appointment_id': booking_request['appointment_id'],
                'user_id': booking_request['user_id'],
                'time_start': booking_request['time_start'],
                'time_end': booking_request['time_end'],
                'date': booking_request['date'],
                'dog_number': booking_request['dog_number'],
                'location': booking_request['location']
            })

        if valid_booking_check.ok:

            time1 = booking_request['time_start'][0:5]
            time2 = booking_request['time_end'][0:5]
            time_start = datetime.strptime(time1, "%H:%M").time()
            time_end = datetime.strptime(time2, "%H:%M").time()
            date =datetime.strptime(booking_request['date'], "%Y-%m-%d").date()

            new_dogsitting_appointment = DogsittingAppointment(appointment_id=booking_request['appointment_id'], userId=booking_request['user_id'], appointment_start=time_start, appointment_end=time_end, dog_number=booking_request['dog_number'], appointment_date=date, location=booking_request['location'])
            
            db.session.add(new_dogsitting_appointment)

            hours = Dog_per_Hours.query.filter_by(appointment_id=booking_request['appointment_id']).all()
                
            end_hour = int(time.fromisoformat(booking_request['time_end']).strftime("%H"))

            start_hour = int(time.fromisoformat(booking_request['time_start']).strftime("%H"))    

            if hours[0].start <= start_hour and hours[-1].end >= end_hour:
                
                hour_count = end_hour - start_hour
                for hour in hours:
                    if (hour.start >= start_hour) and (hour.end <= end_hour):
                        hour.available_dog_number -= booking_request['dog_number']

                        
            db.session.commit()

            return {'booking_status': "Prenotazione avvenuta con successo"}, 200

        else:
            return {'booking_statis': "Informazioni della prenotazione non valide, ricontrollare"}, 400


@app.route('/api/delete_dogsitter_appointment_api', methods=['DELETE'])
@login_required
def delete_dogsitter_appointment_api():

    dogsitter_appointment_id = request.json

    appointment = AvailableDogsitter.query.filter_by(id=dogsitter_appointment_id['appointment_id']).first()

    if not appointment:
        return {'error': 'Appuntamento non trovato'}, 404

    if appointment.dogsitter_id != current_user.id or current_user.user_type != True:
        return {'error': 'Richiesta fatta da utente non possessore della prenotazione'}, 400
    else:

        prenotations = DogsittingAppointment.query.filter_by(appointment_id=dogsitter_appointment_id['appointment_id']).all()

        for prenotation in prenotations:
            db.session.delete(prenotation)

        hours = Dog_per_Hours.query.filter_by(appointment_id=dogsitter_appointment_id['appointment_id']).all()

        for hour in hours:
            db.session.delete(hour)

        db.session.delete(appointment)
        db.session.commit()

        return {'errors': 'Nessun errore riscontrato'}, 200



@app.route('/api/dogsitter_appointment_list_api', methods=['GET'])
@login_required
def dogsitter_appointment_list_api():

    dogsitter_appointment_user_id = request.json

    if current_user.id == dogsitter_appointment_user_id['user_id']:

        if current_user.user_type == True:

            availability_list = AvailableDogsitter.query.filter_by(dogsitter_id=current_user.id).all()

            availability_list_serializable = []

            prenotation_list_serializable = []

            for elem in availability_list:
                # rendere restfull 
                prenotation_list = DogsittingAppointment.query.filter_by(appointment_id=elem.id).all()

                for elem_prenotation in prenotation_list:
                    prenotation_list_serializable.append(elem_prenotation.as_dict())

                availability_list_serializable.append(elem.as_dict())

            return {'return_list': availability_list_serializable, 'prenotation_list': prenotation_list_serializable}, 200
        else:
            return {'error': 'Richiesta da parte di un utente non dogsitter'}, 400
    else:
        return {'error': 'Richiesta da parte di un utente diverso da quello loggato'}, 400


@app.route('/api/delete_booked_prenotation_by_id', methods=['DELETE'])
@login_required
def delete_booked_prenotation_by_id():
    
    prenotation_to_be_deleted = request.json

    prenotation = DogsittingAppointment.query.filter_by(id=prenotation_to_be_deleted['prenotation_id']).first()

    if not prenotation:
        return {'error': 'Prenotazione non trovata'}, 404

    if prenotation.userId != current_user.id:
        return {'error': 'La prenotazione non è stata effettuata da questo utente'}, 401

    hours = Dog_per_Hours.query.filter_by(appointment_id=prenotation.appointment_id).all()

    end_hour = int(prenotation.appointment_end.strftime("%H"))

    start_hour = int(prenotation.appointment_start.strftime("%H"))

    if hours[0].start <= start_hour and hours[-1].end >= end_hour:
        
        hour_count = end_hour - start_hour
        for hour in hours:
            if (hour.start >= start_hour) and (hour.end <= end_hour):
                hour.available_dog_number += prenotation.dog_number

    db.session.delete(prenotation)
    db.session.commit()

    return {'errors': 'Nessun errore riscontrato'}, 200


@app.route('/api/user_booked_appointment', methods=['GET'])
@login_required
def user_booked_appointment_api():

    user_booked_appointment_data = request.json

    return_list = DogsittingAppointment.query.filter_by(userId=user_booked_appointment_data['id']).all()

    for i in range(0, len(return_list)):
        return_list[i] = return_list[i].as_dict()

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


@app.route('/api/user_profile', methods=['POST','GET'])
@login_required
def user_profile_api():

    requested_user = request.json

    if current_user.id == requested_user['user_id']:

        user_data = User.query.filter_by(id=requested_user['user_id']).first()
  

        return {'user_data': user_data.as_dict()}, 200
    
    else:
        return {'error': "Richiesta fatta da utente non proprietario del profilo"}, 400


@app.route('/api/update_user_profile', methods=['PUT'])
@login_required
def update_user_profile_api():
    
    user_data = request.json

    if current_user.id == user_data['user_id']:

        update_user_data = User.query.filter_by(id=user_data['user_id']).first()
        update_user_data.name = user_data['name']
        update_user_data.surname = user_data['surname']
        update_user_data.sex = user_data['sex']
        update_user_data.birth_date = date.fromisoformat(user_data['birth_date'])
        update_user_data.tel_number = user_data['tel_number']
        update_user_data.description = user_data['description']

        db.session.commit()
        return {'message': 'Dati inviati con successo'}, 200

    else:

        return {'error': "Richiesta fatta da utente non proprietario del profilo"}, 400
