from app import app, engine, bcrypt
from models import ZendeskUsers, Users, ZendeskSchedules, PasswordResetRequests
from sqlalchemy.orm import Session
from flask import request, redirect, url_for, send_from_directory, flash
from helpers import internal_render_template
import os
from flask_wtf import FlaskForm
from wtforms import validators, StringField, SubmitField, PasswordField
import time
from email_sender import send_password_reset_email
from flask_login import login_required


class ProfileForm(FlaskForm):
    name = StringField('Nome', [validators.DataRequired(), validators.Length(min=1, max=100)])
    email = StringField('E-mail', [validators.DataRequired(), validators.Length(min=1, max=100)])
    current_password = PasswordField('Senha atual', [validators.Length(min=0, max=100)])
    new_password = PasswordField('Nova senha', [validators.Length(min=0, max=100)])
    new_password_confirmation = PasswordField('Confirme a nova senha', [validators.Length(min=0, max=100)])
    save = SubmitField('Salvar')


class ForgotPasswordForm(FlaskForm):
    email = StringField('E-mail', [validators.DataRequired(), validators.Length(min=1, max=100)])
    save = SubmitField('Enviar')


class ResetPasswordForm(FlaskForm):
    new_password = PasswordField('Nova senha', [validators.DataRequired(), validators.Length(min=0, max=100)])
    new_password_confirmation = PasswordField('Confirme a nova senha', [validators.DataRequired(), validators.Length(min=0, max=100)])
    save = SubmitField('Salvar')


@app.route('/users/new/', methods=['GET', 'POST', ])
def new_user():
    if request.method == 'GET':
        with Session(engine) as session:
            zendesk_users = ZendeskUsers.get_zendesk_users(session)
            zendesk_schedules = ZendeskSchedules.get_schedules(session)

        return internal_render_template(
            'user-new.html', zendesk_users=zendesk_users, zendesk_schedules=zendesk_schedules,
        )

    if request.method == 'POST':
        data = request.get_json()

        if data['backlog_limit'] == '':
            backlog_limit = None
        else:
            backlog_limit = data['backlog_limit']

        if data['hourly_ticket_assignment_limit'] == '':
            hourly_ticket_assignment_limit = None
        else:
            hourly_ticket_assignment_limit = data['hourly_ticket_assignment_limit']

        if data['daily_ticket_assignment_limit'] == '':
            daily_ticket_assignment_limit = None
        else:
            daily_ticket_assignment_limit = data['daily_ticket_assignment_limit']

        with Session(engine) as session:
            Users.insert_new_user(
                session,
                data['user_name'],
                data['user_email'],
                data['user_status'],
                data['zendesk_users_id'],
                data['zendesk_schedules_id'],
                backlog_limit,
                hourly_ticket_assignment_limit,
                daily_ticket_assignment_limit,
            )
            session.commit()

        return 'Success'


@app.route('/users/delete/<int:user_id>', methods=['DELETE', ])
def delete_user(user_id):

    with Session(engine) as session:
        Users.delete_user(session, user_id)
        session.commit()

    return 'Data processed successfully'


@app.route('/user/edit/<int:user_id>', methods=['GET', 'PUT', ])
def get_user(user_id):

    if request.method == 'GET':
        with Session(engine) as session:
            user = Users.get_user(session, user_id)
            zendesk_users = ZendeskUsers.get_zendesk_users(session)
            zendesk_user_email = ZendeskUsers.get_zendesk_user_email_by_user_id(session, user.zendesk_users_id)
            zendesk_schedules = ZendeskSchedules.get_schedules(session)
            zendesk_schedule_name = ZendeskSchedules.get_zendesk_schedule_name_by_id(session, user.zendesk_schedules_id)

        return internal_render_template(
            'user-edit.html',
            user=user,
            zendesk_users=zendesk_users,
            zendesk_user_email=zendesk_user_email,
            zendesk_schedules=zendesk_schedules,
            zendesk_schedule_name=zendesk_schedule_name,
        )

    if request.method == 'PUT':
        data = request.get_json()

        if data['backlog_limit'] == '':
            backlog_limit = None
        else:
            backlog_limit = data['backlog_limit']

        if data['hourly_ticket_assignment_limit'] == '':
            hourly_ticket_assignment_limit = None
        else:
            hourly_ticket_assignment_limit = data['hourly_ticket_assignment_limit']

        if data['daily_ticket_assignment_limit'] == '':
            daily_ticket_assignment_limit = None
        else:
            daily_ticket_assignment_limit = data['daily_ticket_assignment_limit']

        with Session(engine) as session:
            Users.update_user(
                session,
                data['user_id'],
                data['user_name'],
                data['user_email'],
                data['user_status'],
                data['zendesk_users_id'],
                data['zendesk_schedules_id'],
                backlog_limit,
                hourly_ticket_assignment_limit,
                daily_ticket_assignment_limit,
            )
            session.commit()

        return 'Success'


@app.route('/users/change-user-status/<int:user_id>', methods=['PATCH', ])
@login_required
def change_another_user_status(user_id):

    with Session(engine) as db_session:
        Users.change_user_status(db_session, user_id)
        db_session.commit()

    return 'Data processed successfully'


@app.route('/profile/<int:user_id>', methods=['GET', 'POST', ])
@login_required
def user_profile(user_id):
    if request.method == 'GET':
        with Session(engine) as db_session:
            user = Users.get_user_profile(db_session, user_id)

        class Password:
            def __init__(self, current_password, new_password, new_password_confirmation):
                self.current_password = current_password
                self.new_password = new_password
                self.new_password_confirmation = new_password_confirmation

        password = Password('', '', '')

        form = ProfileForm()
        form.name.data = user.name
        form.email.data = user.email
        form.current_password.data = password.current_password
        form.new_password.data = password.new_password
        form.new_password_confirmation.data = password.new_password_confirmation

        return internal_render_template(
            'profile.html',
            user=user,
            form=form,
        )

    if request.method == 'POST':
        form = ProfileForm(request.form)

        if form.validate_on_submit():
            with Session(engine) as db_session:
                user = Users.get_user_profile(db_session, user_id)

                current_password = form.current_password.data
                new_password = form.new_password.data
                new_name = form.name.data

                if new_password != '' and bcrypt.check_password_hash(user.password, current_password):
                    Users.update_user_password(
                        db_session,
                        user_id,
                        bcrypt.generate_password_hash(new_password).decode('utf-8'),
                    )
                    flash('Senha alterada com sucesso!')
                    db_session.commit()
                elif new_password != '' and not bcrypt.check_password_hash(user.password, current_password):
                    flash('Senha atual incorreta')
                    return redirect(url_for(f'user_profile', user_id=user_id))

                if new_name != user.name:
                    Users.update_user_name_from_profile(
                        db_session,
                        user_id,
                        new_name,
                    )
                    flash('Cadastro alterado com sucesso!')
                    db_session.commit()

                if request.files['profile-picture']:
                    profile_picture = request.files['profile-picture']
                    upload_path = app.config['USER_PROFILE_PICTURE_UPLOAD_PATH']
                    timestamp = time.time()
                    delete_profile_picture(user.id)
                    profile_picture.save(f'{upload_path}/{user.id}-{timestamp}.jpg')
                    flash('Foto alterada com sucesso!')

        return redirect(url_for(f'user_profile', user_id=user_id))


def get_profile_picture_to_be_replaced(user_id):
    for file_name in os.listdir(app.config['USER_PROFILE_PICTURE_UPLOAD_PATH']):
        if f'{user_id}' in file_name:
            return file_name

    return 'placeholder.png'


def delete_profile_picture(user_id):
    file_name = get_profile_picture_to_be_replaced(user_id)
    if file_name != 'placeholder.png':
        os.remove(os.path.join(app.config['USER_PROFILE_PICTURE_UPLOAD_PATH'], file_name))


@app.route('/get-profile-picture/<user_id>')
@login_required
def get_profile_picture(user_id):
    for file_name in os.listdir(app.config['USER_PROFILE_PICTURE_UPLOAD_PATH']):
        if f'{user_id}-' in file_name:
            return send_from_directory(app.config['USER_PROFILE_PICTURE_UPLOAD_PATH'], str(file_name))

    return send_from_directory(app.config['USER_PROFILE_PICTURE_UPLOAD_PATH'], 'placeholder.png')


@app.route('/forgot-password', methods=['GET', 'POST', ])
def forgot_password():
    if request.method == 'GET':
        form = ForgotPasswordForm()
        form.email.data = ''

        return internal_render_template(
            'forgot-password.html',
            form=form,
        )

    if request.method == 'POST':
        form = ForgotPasswordForm(request.form)

        if form.validate_on_submit():
            with Session(engine) as db_session:
                user = Users.get_user_from_email(db_session, form.email.data)

            if user:
                new_password_request = PasswordResetRequests.create_new_request_returning_uuid(db_session, user.id)
                PasswordResetRequests.invalidate_other_user_requests(db_session, new_password_request, user.id)

                password_reset_email = send_password_reset_email(
                    user.email,
                    user.name,
                    request.base_url.replace('/forgot-password', '') + '/reset-password/' + new_password_request
                )   # TODO think of a better way to create this URL

                if password_reset_email:
                    db_session.commit()
                    flash('E-mail enviado com sucesso!', 'success')
                    return redirect(url_for('login'))

                else:
                    flash('Ocorreu um erro ao enviar o e-mail de recuperação de senha!')
                    return redirect(url_for('login'))

            else:
                flash('E-mail não cadastrado!')
                return redirect(url_for('forgot_password'))

        else:
            flash('Ocorreu um erro!')
            return redirect(url_for('login'))


@app.route('/reset-password/<request_uuid>', methods=['GET', 'POST', ])
def reset_password(request_uuid):
    if request.method == 'GET':
        with Session(engine) as db_session:
            reset_password_request_data = PasswordResetRequests.is_request_valid(db_session, request_uuid)
            if not reset_password_request_data.used and reset_password_request_data.valid:
                form = ResetPasswordForm()

                class Password:
                    def __init__(self, user_new_password, user_new_password_confirmation):
                        self.new_password = user_new_password
                        self.new_password_confirmation = user_new_password_confirmation

                password = Password('', '')

                form.new_password.data = password.new_password
                form.new_password_confirmation.data = password.new_password_confirmation

                return internal_render_template(
                    'reset-password.html',
                    form=form,
                    current_request_uuid=request_uuid,
                )

            else:
                flash('Este link de recuperação de senha é inválido ou já foi utilizado!')
                return redirect(url_for('login'))

    if request.method == 'POST':
        form = ResetPasswordForm(request.form)

        if form.validate_on_submit():
            with Session(engine) as db_session:
                reset_password_request_data = PasswordResetRequests.is_request_valid(db_session, request_uuid)

                if not reset_password_request_data.used:
                    new_password = form.new_password.data
                    new_password_confirmation = form.new_password_confirmation.data
                    if new_password == new_password_confirmation:
                        user_id = reset_password_request_data.users_id

                        Users.update_user_password(
                            db_session,
                            user_id,
                            bcrypt.generate_password_hash(new_password).decode('utf-8'),
                        )

                        PasswordResetRequests.flag_request_as_used(db_session, reset_password_request_data.id)

                        db_session.commit()

                        flash('Senha alterada com sucesso!', 'success')
                        return redirect(url_for('login'))

                    else:
                        flash('As senhas inseridas não coincidem!')
                        return redirect(request.url)

                else:
                    flash('Este link de recuperação de senha já foi utilizado!')
                    return redirect(url_for('login'))
