# -*- coding: utf-8 -*-
#pylint: disable=unused-variable,unused-argument,too-many-lines

from flask import request, Blueprint, session, redirect, url_for, flash

import datetime

from web_app.utils import rend_folder_template, verify_session
from web_app.database import Database

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard', methods=['GET'], endpoint="index")
@verify_session
def dashboard():
    db = Database()

    now = datetime.datetime.now() 
    filter_date = now - datetime.timedelta(days=7)

    timeouts = db.count_documents('users_bans', {})
    timeouts_filter = db.get_all_timeouts(status='both', from_date=filter_date.strftime("%Y-%m-%d"))
    strikes = db.count_documents('users_strikes', {})
    strikes_filter = db.get_all_strikes(status='active', from_date=filter_date.strftime("%Y-%m-%d"))
    strikes_all = db.get_all_strikes(status='active')

    dates = [now - datetime.timedelta(days=x) for x in range(7)]
    dates.reverse()

    timeout_data = {
        'active': list(),
        'expired': list(),
        'total': timeouts,
        'chart_data': {
            'labels': [date.strftime("%m/%d") for date in dates],
            'datasets': [{
                'label': 'Timeouts',
                'data': [0, 0, 0, 0, 0, 0, 0],
                'backgroundColor': [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)',
                    'rgba(255, 20, 147, 0.2)'
                ],
                'borderColor': [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)',
                    'rgba(255, 20, 147, 1)'
                ],
                'borderWidth': 1
            }]
        }
    }

    for timeout in timeouts_filter:
        timeout_data[timeout['status']].append(timeout)
        created_date = datetime.datetime.fromisoformat(timeout['created_date'])
        try:
            timeout_data['chart_data']['datasets'][0]['data'][6 - (now.day - created_date.day)] += 1
            timeout['_id'] = str(timeout['_id'])
        except:
            pass
        timeout.pop("user_db_id")

    strikes_data = {
        'active': list(),
        'expired': list(),
        'total': strikes,
        'users': dict(),
        'chart_data': {
            'labels': [date.strftime("%m/%d") for date in dates],
            'datasets': [{
                'label': 'Strikes',
                'data': [0, 0, 0, 0, 0, 0, 0],
                'backgroundColor': [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)',
                    'rgba(255, 20, 147, 0.2)'
                ],
                'borderColor': [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)',
                    'rgba(255, 20, 147, 1)'
                ],
                'borderWidth': 1
            }]
        }
    }

    for strike in strikes_filter:
        strikes_data[strike['status']].append(strike)
        created_date = datetime.datetime.fromisoformat(strike['created_date'])
        try:
            strikes_data['chart_data']['datasets'][0]['data'][6 - (now.day - created_date.day)] += 1
            strike['_id'] = str(strike['_id'])
        except:
            pass
        strike.pop("user_db_id")

    for strike in strikes_all:
        if strike['user_id'] not in strikes_data['users']:
            strikes_data['users'][strike['user_id']] = strike['user']
            strikes_data['users'][strike['user_id']]['strikes'] = list()

        strikes_data['users'][strike['user_id']]['strikes'].append(strike)

    aggregated_data = {
        'total_active': len(timeout_data['active']) + len(strikes_data['active']),
        'total_expired': len(timeout_data['expired']) + len(strikes_data['expired']),
        'total': timeout_data['total'] + strikes_data['total'],
        'chart_data': {
            'labels': [date.strftime("%m/%d") for date in dates],
            'datasets': [{
                'label': 'Total',
                'data': [timeout_data['chart_data']['datasets'][0]['data'][x] + strikes_data['chart_data']['datasets'][0]['data'][x] for x in range(len(timeout_data['chart_data']['datasets'][0]['data']))],
                'backgroundColor': [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)',
                    'rgba(255, 20, 147, 0.2)'
                ],
                'borderColor': [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)',
                    'rgba(255, 20, 147, 1)'
                ],
                'borderWidth': 1
            }]
        }
    }

    return rend_folder_template('dashboard', 'index', timeout_data=timeout_data, strikes_data=strikes_data, aggregated_data=aggregated_data)
