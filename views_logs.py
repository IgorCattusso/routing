from models import AssignedTicketsLog
from app import app, engine
from sqlalchemy.orm import Session
from flask import request
import ast


def logs_as_list(logs):
    list_of_logs = []

    for log in logs:
        list_of_logs.append({
            'log_id': log[0],
            'ticket_id': log[1],
            'user_name': log[2],
            'short_message': ast.literal_eval(log[3])['message'],  # converting str to dict
            'full_message':
                str(ast.literal_eval(log[3]))
                .replace("'", '"')
                .replace('True', '"True"')
                .replace('False', '"False"')
                .replace('None', '""'),
            'created_at': log[4].strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
        })

    return list_of_logs


@app.route('/search-logs', methods=['POST'])
def search_logs():
    if request.method == 'POST':
        data = request.get_json()

        with Session(engine) as db_session:
            logs = AssignedTicketsLog.get_logs(db_session, data=data)

        return logs_as_list(logs)
