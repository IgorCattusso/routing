from app import app, login_manager, engine
from models import Users, UsersQueue
from flask import flash, request, redirect, url_for, render_template, session
from flask_login import login_user, UserMixin, login_required, logout_user
from helpers import UserForm
from sqlalchemy.orm import Session
from sqlalchemy import select


class User(UserMixin):
    def __init__(self, id, name, email, password):
        self.id = id
        self.name = name
        self.email = email
        self.password = password

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return self.is_active

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return str(self.id)
        except AttributeError:
            raise NotImplementedError("No `id` attribute - override `get_id`") from None


def check_user(id):
    with Session(engine) as db_session:
        db_user = db_session.execute(
            select(Users).where(Users.id == id)
        ).first()

        if db_user:
            return User(db_user.Users.id, db_user.Users.name, db_user.Users.email, db_user.Users.password)
        else:
            return None


def check_user_credentials(email, password):
    with Session(engine) as db_session:
        db_user = db_session.execute(
            select(Users).where(Users.email == email).where(Users.password == password)
        ).first()

        if db_user:
            return User(db_user.Users.id, db_user.Users.name, db_user.Users.email, db_user.Users.password)
        else:
            return None


def user_is_already_logged_in(users_id):
    with Session(engine) as db_session:
        already_logged_in = db_session.execute(
            select(Users).where(Users.id == users_id).where(Users.authenticated == 1)
        ).first()

        if already_logged_in:
            return True
        else:
            return False


@login_manager.user_loader
def load_user(id):
    return check_user(id)


@app.route('/login', methods=['GET', 'POST'])
def login():

    form = UserForm()

    if form.validate_on_submit():
        user = check_user_credentials(form.email.data, form.password.data)

        if user and not user_is_already_logged_in(user.id):
            login_user(user)

            session['routing_status'] = 2
            session['logged_in'] = True
            user_id = session['_user_id']
            print(user_id)

            with Session(engine) as db_session:
                Users.login_user(db_session, user.id)
                Users.change_routing_status(db_session, user_id, session['routing_status'])
                if UsersQueue.check_if_user_has_to_be_in_queue(db_session, user_id):
                    if UsersQueue.is_user_alread_in_queue(db_session, user_id):
                        UsersQueue.insert_user_at_queue_end(db_session, user_id)
                    else:
                        UsersQueue.insert_new_user_in_queue(db_session, user_id)
                        UsersQueue.insert_user_at_queue_end(db_session, user_id)

                db_session.commit()

            flash('Logged in successfully.')

            return redirect(url_for('home'))

        elif user and user_is_already_logged_in(user.id):
            flash('Este usuário já está logado!')
            return render_template('login.html', form=form)

        else:
            flash('Usuário ou senha incorretos!')
            return render_template('login.html', form=form)

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():

    user_id = session['_user_id']
    session['logged_in'] = 0
    session['routing_status'] = 0

    logout_user()

    with Session(engine) as db_session:
        Users.logout_user(db_session, user_id)
        Users.change_routing_status(db_session, user_id, session['routing_status'])
        if UsersQueue.check_if_user_has_to_be_in_queue(db_session, user_id):
            UsersQueue.remove_user_from_queue(db_session, user_id)
        db_session.commit()

    return redirect(url_for('home'))
