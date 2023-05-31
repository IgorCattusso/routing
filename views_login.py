from app import login_manager, app, engine, bcrypt
from models import UsersQueue
from flask import session, render_template, redirect, url_for, flash
from flask_login import login_user, UserMixin, login_required, logout_user
from flask_wtf import FlaskForm
from wtforms import validators, StringField, SubmitField, PasswordField
from sqlalchemy import select
from sqlalchemy.orm import Session
from models import Users


class UserForm(FlaskForm):
    email = StringField(
        'E-mail',
        [validators.DataRequired(),
         validators.Length(min=1, max=150)],
        render_kw={"placeholder": "E-mail"}
    )
    password = PasswordField(
        'Senha',
        [validators.DataRequired(),
         validators.Length(min=1, max=150)],
        render_kw={"placeholder": "Senha"}
    )
    submit = SubmitField('Login')


class User(UserMixin):
    def __init__(self, id, name, email, password, active, deleted, authenticated):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.active = active
        self.deleted = deleted
        self.authenticated = authenticated

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
            select(
                Users.id,
                Users.name,
                Users.email,
                Users.password,
                Users.active,
                Users.deleted,
                Users.authenticated,
            ).where(Users.id == id)
        ).first()

        if db_user:
            return User(
                Users.id,
                Users.name,
                Users.email,
                Users.password,
                Users.active,
                Users.deleted,
                Users.authenticated,
            )
        else:
            return None


def check_user_credentials(email, password):
    with Session(engine) as db_session:
        db_user = db_session.execute(
            select(
                Users.id,
                Users.name,
                Users.email,
                Users.password,
                Users.active,
                Users.deleted,
                Users.authenticated,
            ).where(Users.email == email)
        ).first()

        is_password_correct = bcrypt.check_password_hash(db_user.password, password)

        if db_user and is_password_correct:
            return User(
                db_user.id,
                db_user.name,
                db_user.email,
                db_user.password,
                db_user.active,
                db_user.deleted,
                db_user.authenticated,
            )
        else:
            return None


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))


@login_manager.user_loader
def load_user(id):
    return check_user(id)


@app.route('/login', methods=['GET', 'POST'])
def login():

    form = UserForm()

    if form.validate_on_submit():
        user = check_user_credentials(form.email.data, form.password.data)

        if user:
            if not user.active or user.deleted:
                flash('Usuário não encontrado!')
                return render_template('login.html', form=form)

            login_user(user)

            session.permanent = True

            session['routing_status'] = 2
            session['logged_in'] = True
            user_id = session['_user_id']

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

            return redirect(url_for('home'))

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

    session['_user_id'] = 0

    with Session(engine) as db_session:
        Users.logout_user(db_session, user_id)
        Users.change_routing_status(db_session, user_id, session['routing_status'])
        if UsersQueue.check_if_user_has_to_be_in_queue(db_session, user_id):
            UsersQueue.remove_user_from_queue(db_session, user_id)
        db_session.commit()

    return redirect(url_for('login'))
