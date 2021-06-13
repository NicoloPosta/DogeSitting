from api import *


@app.route('/')
def index():
    return render_template('index.html')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



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

'''
@app.route('/add_appointment')
@login_required
def add_appointment():

    if(current_user.user_type == True):
            return redirect(url_for('appointment_form'))
    else:
        return redirect(url_for('dashboard'))
'''

@app.route('/appointment_form', methods=['GET', 'POST'])
@login_required
def appointment_form():

    appointment_form = AppointmentForm()

    if(current_user.user_type == True):

        if appointment_form.validate_on_submit():
            '''
            new_appointment = AvailableDogsitter(dogsitter_id=current_user.id , max_dog_number=form.dog_number.data, location=form.location.data, appointment_day=form.date.data, appointment_start=form.time_start.data, appointment_end=form.time_end.data)
            db.session.add(new_appointment)
            db.session.commit()
            '''
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
