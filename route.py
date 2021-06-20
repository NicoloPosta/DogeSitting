from posixpath import split
from flask_wtf import form
from werkzeug.utils import secure_filename
from os import path, makedirs, remove
from api import *
from app import current_dir
first_click = True


# route principale 
@app.route('/', methods=['GET', 'POST'])
def index():

    # instanzia i form LoginForm, RegisterForm e SearchForm
    login_form = LoginForm()
    signup_form = RegisterForm()

    search_form = SearchForm()

    if login_form.login.data:
        if login_form.validate():
            #chiama la Api per effettuare il login
            login_return = requests.post('http://localhost:5000/api/login',
                json={
                    'username': login_form.username.data,
                    'password': login_form.password.data
                }
            )
            # se la query ritorna ok allora viene effettuato il login, altrimenti lacia un errore
            if login_return.ok:
                user = User.query.filter_by(id=login_return.json()['user_id']).first()
                login_user(user, remember=True)
                if user.user_type:
                    return redirect(url_for('dogsitter_dashboard'))
                else:
                    return redirect(url_for('dashboard'))
            else:
                login_return = login_return.json()
                if 'username_login' in login_return:
                    login_form.username.errors = [login_return['username_login']]
                if 'password' in login_return:
                    login_form.password.errors = [login_return['password']]

    if signup_form.register.data:
        if signup_form.validate():
            # effettua un richiesta all' Api per il signup
            signup_return = requests.post('http://localhost:5000/api/signup',
                json={
                    'username': signup_form.username.data,
                    'email': signup_form.email.data,
                    'password': signup_form.password.data,
                    'user_type': signup_form.usertype.data
                }
            ) 
            # dopo aver creato un nuovo utente nel db e aver ritornato con successo l'Api effettua il login del unovo utente creato
            if signup_return.ok:
                user = User.query.filter_by(id=signup_return.json()['user_id']).first()
                login_user(user, remember=True)
                if user.user_type:
                    return redirect(url_for('dogsitter_dashboard'))
                else:
                    return redirect(url_for('dashboard'))
            # altrimenti ritorna errore
            else:
                signup_return = signup_return.json()
                if 'email' in signup_return:
                    signup_form.email.errors = [signup_return['email']]
                if 'username' in signup_return:
                    signup_form.username.errors = [signup_return['username']]
    # se viene effettuata la ricerca dell'appuntamento anche senza il login si viene reindirizzati alla pagina appointment_list
    if search_form.search.data and search_form.validate():
        return appointment_list(search_form)

    return render_template('index.html', form_login=login_form, form_register=signup_form, search_form=search_form)

#effettua il login dell'utente
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# route per cancellare la disponibilità data dal dogsitter
@app.route('/delete_dogsitter_appointment/<appointment_id>', methods=['GET','POST'])
@login_required
def delet_dogsitter_appointment(appointment_id):
    
    appointment_id = int(appointment_id)
    # effettua una richiesta delete all'Api
    return_request = requests.delete('http://localhost:5000/api/delete_dogsitter_appointment_api',
        json={
            'appointment_id': appointment_id
        },
        cookies=request.cookies
        )
    # se l'Api ritorna ok allora si viene reindirizzati alla dogsitter dashboard
    if return_request.ok:
        return redirect(url_for('dogsitter_dashboard'))
    else:
        return_request = return_request.json()
        if return_request['error'] == 'Appuntamento non trovato':
            return{'error': return_request['error']}, 404
        else:
            return{'error': return_request['error']}, 401


# route per eliminare la prenotazione effettuata dall'utente
@app.route('/delete_booked_prenotation/<requested_prenotation_id>', methods=['GET','POST'])
@login_required
def delete_booked_prenotation(requested_prenotation_id):

    requested_prenotation_id = int(requested_prenotation_id)
    # viene effettuata la richiesta delete all'Api
    return_request = requests.delete('http://localhost:5000/api/delete_booked_prenotation_by_id',
        json={
            'prenotation_id': requested_prenotation_id
        },
        cookies=request.cookies
    )

    if return_request.ok:
        return redirect(url_for('dashboard'))
    else:
        return_request = return_request.json()
        if return_request['error'] == 'Prenotazione non trovata':
            return{'error': return_request['error']}, 404
        else:
            return{'error': return_request['error']}, 401



# permette all'utente di cercare gli appuntamenti disponibili in base alla posizione, data, ora inizio, ora fine e numero di cani
@app.route('/appointment_list', methods=['GET','POST'])
def appointment_list(search_form=None):

    login_form = LoginForm()
    signup_form = RegisterForm()

    if not search_form:
        search_form = SearchForm()

    if search_form.search.data and search_form.validate():

        search_return = requests.get('http://localhost:5000/api/appointment_list',
            json={
                'location': search_form.location.data,
                'date': search_form.date.data.isoformat(),
                'dog_number': search_form.dog_number.data,
                'time_start': search_form.time_start.data.isoformat(),
                'time_end': search_form.time_end.data.isoformat(),
            }
        )

        if search_return.ok:
            search_return = search_return.json()
            return render_template('appointment_list.html', appointments_list=search_return['return_list'], search_form=search_form, form_login=login_form, form_register=signup_form)
        # in base a dove viene effettuato l'errore viene ritornato un feedback video che informa l'utente
        else:
            search_return = search_return.json()
            if 'no_results' in search_return:
                search_form.location.errors = [search_return['no_results']]
            if 'hour_error' in search_return:
                search_form.time_start.errors = [search_return['hour_error']]

    return render_template('appointment_list.html', appointments_list=[], search_form=search_form, form_login=login_form, form_register=signup_form)


# permette all'utente di prenotarsi ad un appuntamento passandogli tutti i parametri necessari nell' URL
@app.route('/book_appointment/<int:appointment_id>/<time_start>/<time_end>/<date>/<int:dog_number>/<location>/<appointment_cost>', methods=['GET','POST'])
@login_required
def book_appointment(appointment_id, time_start, time_end, date, dog_number, location, appointment_cost):
    
    if(current_user.user_type == True):
            return {'booking_status': "Non hai i privilegi per effettuare una prenotazione"}, 401
    else:
        user_id = current_user.id
        booked_appointment_return = requests.post('http://localhost:5000/api/book_appointment',
            json={
                'appointment_id': appointment_id,
                'user_id': user_id,
                'time_start': time_start,
                'time_end': time_end,
                'date': date,
                'dog_number': dog_number,
                'location': location,
                'appointment_cost': appointment_cost
            },
            cookies=request.cookies)


        if booked_appointment_return.ok:
            return redirect(url_for('appointment_list'))
        else:
            return redirect(url_for('dashboard'))

# permette all' utente di tipo dogsitter di aggiungere la disponibilità per un appuntamento
@app.route('/appointment_form', methods=['GET', 'POST'])
@login_required
def appointment_form():

    appointment_form = AppointmentForm()

    if(current_user.user_type == True):

        if appointment_form.validate_on_submit():

            appointment_return = requests.post('http://localhost:5000/api/add_appointment',
                json={
                    'dogsitter_id': current_user.id,
                    'dog_number': appointment_form.dog_number.data,
                    'location': appointment_form.location.data,
                    'date': appointment_form.date.data.isoformat(),
                    'time_start': appointment_form.time_start.data.isoformat(),
                    'time_end': appointment_form.time_end.data.isoformat(),
                    'cost_per_hour': appointment_form.cost_per_hour.data
                }
            )

            if appointment_return.ok:
                return redirect(url_for('dogsitter_dashboard'))
            else:
                appointment_return = appointment_return.json()
                if 'date' in appointment_return:
                    appointment_form.date.errors = [appointment_return['date']]
                if 'time_start' in appointment_return:
                    appointment_form.time_start.errors = [appointment_return['time_start']]
                if 'time_end' in appointment_return:
                    appointment_form.time_end.errors = [appointment_return['time_end']]

        return render_template('appointment_form.html', form=appointment_form)

    else:

        return redirect(url_for('dashboard'))


# pagina condivisa sia da Dogsitter che da utenti normali che permette di modificare le informazioni aggiuntive relativa al profilo
@app.route('/profile/<user_id>', methods=['POST','GET'])
@login_required
def profile(user_id):

    # variabile che serve per capire se è la prima volta che viene pigiato il tasto modifica così da poter essere
    # in grado di modificare i vari campi del form e poter caricare un immagine di profilo
    global first_click

    user_id = int(user_id)

    profile_form = UserForm()

    profile_info = requests.get('http://localhost:5000/api/user_profile',
        json={
            'user_id': user_id
        },
        cookies=request.cookies
    )

    profilepicture_form = ProfilePictureForm()


    # nuova immagine di profilo?
    if profilepicture_form.image.data:
        if profilepicture_form.validate():
            # prova a rimuovere quella vecchia se è diversa da quella di default
            if current_user.picture != '/static/img/users/default.png':
                try:
                    remove( current_dir + current_user.picture )
                except OSError:
                    pass
            # salva la nuova immagine con il nome 'current_use.id'.estensione immagine
            f = profilepicture_form.image.data

            filename = secure_filename(
                "%s%s" % ( str(current_user.id), path.splitext(f.filename)[-1] )
            )
            path_img = path.join(current_dir, 'static', 'img', 'users', filename)
            f.save(path_img)
            # Aggiorna il db in base alla nuova immagine
            current_user.picture = '/static/img/users/' + filename

            db.session.commit()

    if profile_info.ok:

        profile_info = profile_info.json()
        
        if profile_form.submit.data:

            if first_click:
                # cambia la variabile first_click cosìcchè dopo il return la variablie non_modificabile venga impostata a False
                first_click = False
                return render_template('user_profile.html', id=current_user.id, form=profile_form, nome=profile_info['user_data']['name'], sesso=profile_info['user_data']['sex'], cognome=profile_info['user_data']['surname'], numero_telefono=profile_info['user_data']['tel_number'], data_nascita=profile_info['user_data']['birth_date'], descrizione=profile_info['user_data']['description'], non_modificabile=False, valore_bottone="Conferma", profilepicture_form=profilepicture_form, immagine=current_user.picture)

            else:
                # se non è il First click allora permette la modifica e effettua una richiesta pu all'Api per poter aggiornare i campi del db
                profile_info = requests.put('http://localhost:5000/api/update_user_profile',
                    json={
                        'user_id': user_id,
                        'name': profile_form.name.data,
                        'surname': profile_form.surname.data,
                        'sex': profile_form.sex.data,
                        'birth_date': profile_form.birth_date.data.isoformat(),
                        'tel_number': profile_form.tel_number.data,
                        'description': profile_form.description.data
                    },
                    cookies=request.cookies
                )

                if profile_info.ok:
                    # l'Api ritorna ok allora first_click viene messa a True così da riportare i campi del form in uno stato di non modificabilità
                    first_click = True
                    return redirect(url_for('profile', user_id=current_user.id))

                else:
                    profile_info = profile_info.json()
                    return {'error': profile_info['error']}, 401

        return render_template('user_profile.html', id=current_user.id, form=profile_form, nome=profile_info['user_data']['name'], sesso=profile_info['user_data']['sex'], cognome=profile_info['user_data']['surname'], numero_telefono=profile_info['user_data']['tel_number'], data_nascita=profile_info['user_data']['birth_date'], descrizione=profile_info['user_data']['description'], non_modificabile=True, valore_bottone="Modifica", profilepicture_form=profilepicture_form, immagine=current_user.picture)
        #return render_template('user_profile.html', id=current_user.id, form=profile_form, nome=profile_return['name'], sesso=profile_return['sex'], cognome=profile_return['surname'], numero_telefono=profile_return['tel_number'], data_nascita=profile_return['birth_date'], descrizione=profile_return['description'], non_modificabile=True)
    else:
        profile_info = profile_info.json()
        return {'error': profile_info['error']}, 401


# pagina principale dell'Utente
@app.route('/dashboard')
@login_required
def dashboard():

    if(current_user.user_type == True):
        return redirect(url_for('dogsitter_dashboard'))
    else:

        user_return = requests.get('http://localhost:5000/api/user_booked_appointment',
        json={
            'id': current_user.id
        },
        cookies=request.cookies
        )
        
        if user_return.ok:
            user_return = user_return.json()
            return render_template('dashboard.html', name=current_user.username, user_id = current_user.id, user_booked_appointments=user_return['return_list'])
        else:
            return abort(404)


# pagina principale del Dogsitter
@app.route('/dogsitter_dashboard')
@login_required
def dogsitter_dashboard():

    if current_user.user_type != True:
        return redirect(url_for('dashboard'))

    return_request = requests.get('http://localhost:5000/api/dogsitter_appointment_list_api',
        json={
            'user_id': current_user.id
        },
        cookies=request.cookies
    )

    if return_request.ok:
        return_request = return_request.json()
        return render_template('dogsitter_dashboard.html', dogsitter_available_appointment=return_request['return_list'], dogsitter_prenotations=return_request['prenotation_list'], name=current_user.username, id=current_user.id)
    else:
        return_request = return_request.json()
        return {'error': return_request['error']}, 401



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
