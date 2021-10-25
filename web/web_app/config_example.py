# -*- coding: utf-8 -*-
# pylint: disable=fixme

# URI Configuration
WEB_URI = "https:/localhost:11000/"

# Server information
SERVER_ID = 'server_id'	# What server the bot needs to check they are part of. Needs to be string ... because discord.
ALLOWED_IDS = [] # List of allowed users into dashboard regardless of access in server. Same as above: strings
BOT_API_KEY = '958c3c3bedcc4ed534295g09c27f412eBdc3ac6e7e503735981e4ebd85390f53'
API_SESSION_IDENTIFIER = 'd-api-key'

# Database Configuration
DB_PATH = 'mongodb://username:password@localhost:27017/?authSource=admin&readPreference=primar&ssl=false'
DB_NAME = 'moon2web'

# Discord configuration
DISCORD_CLIENT_ID = 'client_id'
DISCORD_CLIENT_SECRET = 'client_secret'
DISCORD_BOT_TOKEN = 'bot_token'
DISCORD_API_URI = 'https://discord.com/api' # do not leavea / at the end
DISCORD_IMAGE_CDN = 'https://cdn.discordapp.com/' # important to leave the / at the end
DISCORD_REDIRECT_URL = 'http://localhost:11000/oauth2/authorize'
