from api import *


@app.route('/')
def index():
    return render_template('index.html')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/dogsitter_appointment_list/<user_id>', methods=['POST', 'GET'])
@login_required
def dogsitter_appointment_list(user_id):

    user_id = int(user_id)

    return_request = requests.post('http://localhost:5000/api/dogsitter_appointment_list_api',
        json={
            'user_id': user_id
        },
        cookies=request.cookies
    )

    if return_request.ok:
        return_request = return_request.json()
        return render_template('dogsitter_appointment_list.html', dogsitter_available_appointment=return_request['return_list'])
    else:
        return_request = return_request.json()
        return {'error': return_request['error']}, 404


@app.route('/delete_dogsitter_appointment/<appointment_id>', methods=['GET','POST'])
@login_required
def delet_dogsitter_appointment(appointment_id):
    
    appointment_id = int(appointment_id)
    return_request = requests.delete('http://localhost:5000/api/delete_dogsitter_appointment_api',
        json={
            'appointment_id': appointment_id
        },
        cookies=request.cookies
        )
    if return_request.ok:
        return redirect(url_for('dogsitter_appointment_list', user_id=current_user.id))
    else:
        return{'errore':'non è stato possibile eliminare la voce selezionata'}


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



@app.route('/delete_booked_prenotation/<requested_prenotation_id>', methods=['GET','POST'])
@login_required
def delete_booked_prenotation(requested_prenotation_id):

    requested_prenotation_id = int(requested_prenotation_id)

    request_return = requests.delete('http://localhost:5000/api/delete_booked_prenotation_by_id',
        json={
            'prenotation_id': requested_prenotation_id
        },
        cookies=request.cookies
    )

    if request_return.ok:
        return redirect(url_for('user_booked_appointment', requested_user_id=current_user.id))
    else:
        return abort(404)


@app.route('/user_booked_appointment/<requested_user_id>', methods=['GET','POST'])
@login_required
def user_booked_appointment(requested_user_id):
    
    requested_user_id = int(requested_user_id)

    if(current_user.id == requested_user_id):

        if(current_user.user_type == True):
                return redirect(url_for('dogsitter_dashboard'))
        else:

            user_return = requests.post('http://localhost:5000/api/user_booked_appointment',
            json={
                'id': current_user.id
            },
            cookies=request.cookies)
            if user_return.ok:
                user_return = user_return.json()
                return render_template('user_booked_appointments.html', user_booked_appointments=user_return['return_list'])
            else:
                return redirect(url_for('dashboard'))
    else:
        return abort(404)


@app.route('/appointment_list', methods=['GET','POST'])
def appointment_list():
    search_form = SearchForm()

    if search_form.validate_on_submit():

        search_return = requests.post('http://localhost:5000/api/appointment_list',
            json={
                'location': search_form.location.data,
                'date': search_form.date.data.isoformat(),
                'dog_number': search_form.dog_number.data,
                'time_start': search_form.time_start.data.isoformat(),
                'time_end': search_form.time_end.data.isoformat()
            }
        )

        if search_return.ok:
            search_return = search_return.json()
            return render_template('appointment_list.html', appointments_list=search_return['return_list'], form=search_form)
        else:
            search_return = search_return.json()
            if 'no_results' in search_return:
                search_form.location.errors = [search_return['no_results']]

    return render_template('appointment_list.html', appointments_list=[], form=search_form)



@app.route('/book_appointment/<int:appointment_id>/<time_start>/<time_end>/<date>/<int:dog_number>/<location>', methods=['GET','POST'])
@login_required
def book_appointment(appointment_id, time_start, time_end, date, dog_number, location):
    
    if(current_user.user_type == True):
            return {'booking_status': "Non hai i privilegi per effettuare una prenotazione"}, 400
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
                'location': location
            },
            cookies=request.cookies)


        if booked_appointment_return.ok:
            return redirect(url_for('appointment_list'))
        else:
            return redirect(url_for('dashboard'))


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
                    'time_end': appointment_form.time_end.data.isoformat()
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()

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


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    profile_form = UserForm()

    if profile_form.submit.data:
        return redirect(url_for('update_user_profile'))
    return render_template('user_profile.html', id=current_user.id, form=profile_form, nome=current_user.name, sesso=current_user.sex ,cognome=current_user.surname, numero_telefono=current_user.tel_number, data_nascita=current_user.birth_date, descrizione=current_user.description)


@app.route('/update_user_profile', methods=['GET','POST'])
@login_required
def update_user_profile():
    update_profile_form = UserForm()

    if update_profile_form.submit.data and update_profile_form.validate():
        user = User.query.filter_by(id=current_user.id).first()
        user.name = update_profile_form.name.data
        user.surname = update_profile_form.surname.data
        user.sex = update_profile_form.sex.data
        user.birth_date = update_profile_form.birth_date.data
        user.tel_number = update_profile_form.tel_number.data
        user.description = update_profile_form.description.data
        db.session.commit()
        return redirect(url_for('profile'))

    return render_template('update_user_profile.html', id=current_user.id, form=update_profile_form, nome=current_user.name, sesso=current_user.sex ,cognome=current_user.surname, numero_telefono=current_user.tel_number, data_nascita=current_user.birth_date, descrizione=current_user.description)


@app.route('/signup', methods=['GET','POST'])
def signup():
    signup_form = RegisterForm()


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
                signup_form.email.errors = [signup_return['email']]
            if 'username' in signup_return:
                signup_form.username.errors = [signup_return['username']]

    return render_template('signup.html', form=signup_form)




@app.route('/dogsitter_profile')
@login_required
def dogsitter_profile_render():
        return render_template('dogsitter_profile.html', id=current_user.id)


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username, user_id = current_user.id)


@app.route('/dogsitter_dashboard')
@login_required
def dogsitter_dashboard():
    return render_template('dogsitter_dashboard.html', name=current_user.username, id=current_user.id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
