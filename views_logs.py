from models import GeneralSettings, AssignedTicketsLog
from app import app, engine
from sqlalchemy.orm import Session
from flask import request
import ast


@app.route('/search-logs', methods=['POST'])
def search_logs():
    if request.method == 'POST':
        data = request.get_json()

        with Session(engine) as db_session:
            logs = AssignedTicketsLog.get_logs(db_session, data=data)

        list_of_logs = []

        for log in logs:
            list_of_logs.append({
                'log_id': log[0],
                'ticket_id': log[1],
                'user_name': log[2],
                'short_message': ast.literal_eval(log[3])['message'],  # converting str to dict
                'full_message': str(ast.literal_eval(log[3])).replace("'", '"'),  # converting str to dict
            })

        return str(list_of_logs)
