from models import GeneralSettings
from app import app, engine
from sqlalchemy.orm import Session
from flask import request


@app.route('/routing-settings', methods=['PUT'])
def update_general_settings():
    if request.method == 'PUT':
        data = request.get_json()

        if data['backlog_limit'] == '':
            backlog_limit = None
        else:
            backlog_limit = data['backlog_limit']

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
                backlog_limit,
                daily_assignment_limit,
                hourly_assignment_limit,
                zendesk_schedules_id=data['zendesk_schedules_id'],
            )
            session.commit()

    return 'Data processed successfully'
