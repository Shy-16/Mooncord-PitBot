# -*- coding: utf-8 -*-
#pylint: disable=unused-variable,unused-argument,too-many-lines

from flask import request, Blueprint, session, redirect, url_for, flash

import datetime

from web_app.utils import rend_folder_template, verify_session
from web_app.database import Database

users_bp = Blueprint('users', __name__)

@users_bp.route('/users', methods=['GET'], endpoint="index")
@verify_session
def users():
    db = Database()

    users = db.get_users()

    now = datetime.datetime.now() 
    filter_date = now - datetime.timedelta(days=7)

    strikes_all = db.get_all_strikes(status='active')
    strikes_filter = db.get_all_strikes(status='active', from_date=filter_date.strftime("%Y-%m-%d"))

    dates = [now - datetime.timedelta(days=x) for x in range(7)]
    dates.reverse()

    strikes_data = dict()

    for strike in strikes_filter:
        if strike['user_id'] not in strikes_data:
            strikes_data[strike['user_id']] = {
                **strike['user'],
                'all_strikes': list(),
                'recent_strikes': list(),
                'avg_time': 0,
                'chart_data': {
                  'labels': [date.strftime("%m/%d") for date in dates],
                  'datasets': [
                    {
                      'label': 'Strikes',
                      'data': [0, 0, 0, 0, 0, 0, 0],
                      'borderColor': 'rgba(75, 192, 192, 1)',
                      'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                      'fill': 'start'
                    }
                  ]
                }
            }

        created_date = datetime.datetime.fromisoformat(strike['created_date'])
        try:
            strikes_data[strike['user_id']]['chart_data']['datasets'][0]['data'][6 - (now.day - created_date.day)] += 1
        except:
            pass
        strikes_data[strike['user_id']]['recent_strikes'].append(strike)

    for strike in strikes_all:
        if strike['user_id'] not in strikes_data:
            strikes_data[strike['user_id']] = {
                **strike['user'],
                'all_strikes': list(),
                'recent_strikes': list(),
                'avg_time': 0,
                'chart_data': {
                  'labels': [date.strftime("%m/%d") for date in dates],
                  'datasets': [
                    {
                      'label': 'Strikes',
                      'data': [0, 0, 0, 0, 0, 0, 0],
                      'borderColor': 'rgba(75, 192, 192, 1)',
                      'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                      'fill': 'start'
                    }
                  ]
                }
            }

        created_date = datetime.datetime.fromisoformat(strike['created_date'])
        try:
            strikes_data[strike['user_id']]['chart_data']['datasets'][0]['data'][6 - (now.day - created_date.day)] += 1
        except:
            pass
        strikes_data[strike['user_id']]['all_strikes'].append(strike)

    for user_id in strikes_data:
        days_passed = list()

        i = 0
        while i < len(strikes_data[user_id]['all_strikes']) -1:

            created_date_current = datetime.datetime.fromisoformat(strikes_data[user_id]['all_strikes'][i]['created_date'])
            created_date_next = datetime.datetime.fromisoformat(strikes_data[user_id]['all_strikes'][i+1]['created_date'])
            days_passed.append((created_date_next - created_date_current).days)

            i += 1

        if len(days_passed) != 0:
            strikes_data[user_id]['avg_time'] = sum(days_passed) / len(days_passed)
        else:
            strikes_data[user_id]['avg_time'] = 0


    return rend_folder_template('users', 'index', strikes_data=strikes_data)