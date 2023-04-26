import requests
from models import GeneralSettings
from app import app, engine
from sqlalchemy.orm import Session
from flask import render_template, flash, redirect, url_for, request


@app.route('/routing-settings', methods=['PUT'])
def update_general_settings():
    if request.method == 'PUT':
        data = request.get_json()

        if data['agent_backlog_limit'] == '':
            agent_backlog_limit = None
        else:
            agent_backlog_limit = data['agent_backlog_limit']

        if data['daily_assignment_limit'] == '':
            daily_assignment_limit = None
        else:
            daily_assignment_limit = data['daily_assignment_limit']

        if data['hourly_assignment_limit'] == '':
            hourly_assignment_limit = None
        else:
            hourly_assignment_limit = data['hourly_assignment_limit']

        with Session(engine) as session:
            GeneralSettings.update_settings(
                session,
                data['use_routes'],
                data['routing_model'],
                agent_backlog_limit,
                daily_assignment_limit,
                hourly_assignment_limit,
            )
            session.commit()

    return 'Data processed successfully'



