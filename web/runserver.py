# -*- coding: utf-8 -*-

# Start server through python.
# Only used during development.

from web_app import app, socketio
socketio.run(app, host='0.0.0.0', port=11000)
