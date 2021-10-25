# -*- coding: utf-8 -*-
#pylint: disable=unused-variable,unused-argument,too-many-lines

from flask import Flask
from flask_socketio import SocketIO
import logging
from datetime import timedelta

app = Flask("Moonmoon Dashboard", static_folder="web_app/static", template_folder="web_app/templates")
app.permanent_session_lifetime = timedelta(days=7)
app.config['PROPAGATE_EXCEPTIONS'] = True
app.secret_key = 'sha256stringofapassword' # Used to encrypt cookies
app.env = 'development'
app.debug = True # Set to False if production
socketio = SocketIO(app)

##@app.errorhandler(Exception)
##def catch_all(e):
##    """
##    Error handler that catches all other exceptions
##    """
##    log_utils.logexception()
##    return render_template("500.html", error=e)

@app.before_first_request
def before_first_request():
    """
    Called only once upon instantiation.
    """
    logging.basicConfig(filename='server.log', level=logging.INFO)

##@app.before_request
##def before_request():
##    """
##    Called before every request.
##    """
##    pass

# webserver normal modules

##@app.after_request
##def after_request(response):
##    response.headers.add('Access-Control-Allow-Origin', '*')
##    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
##    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
##    return response

from web_app.index import index_bp
app.register_blueprint(index_bp)

from web_app.session import session_bp
app.register_blueprint(session_bp)

from web_app.oauth2 import oauth_bp
app.register_blueprint(oauth_bp)

from web_app.dashboard import dashboard_bp
app.register_blueprint(dashboard_bp)

from web_app.users import users_bp
app.register_blueprint(users_bp)

from web_app.modules.modmail import modmail_bp
app.register_blueprint(modmail_bp)

from web_app.modules.banwords import banwords_bp
app.register_blueprint(banwords_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=11000)
