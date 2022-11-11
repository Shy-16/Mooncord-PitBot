# Pit-Bot

Moderation bot for Mooncord

## Install Instructions

### Install latest version of Python 3.

Pit-Bot uses latest version of Python3, at the very least higher than 3.10.
Pit-Bot uses poetry as dependency manager.
Install all modules:
- `poetry install`

## Install MongoDB

Pit-Bot uses latest version of MongoDB. 
- Configure access user with admin privileges.

By default mongoDB will create non-existing resources on first read, that means you don't need to configure anything.

## Copy config.yaml and edit it.

Copy `config.yaml` from `config_example` to root folder (where `main.py` is located).
Open it and configure the file.

## Run the bot

The bot requires discord token from a **Bot** user to run, which will be provided within the command parameters. 
To get your token create a new Application in the [Discord developer portal](https://discord.com/developers/applications) and then make sure you activate the `Bot` under `Bot` configuration.

Once you have the token, run the bot:
- `poetry run python main.py -t <token>`

## Invite the bot to your server

To invite the bot to your server you have to copy both the `Applcation ID` and `Permissions` from the bot, and edit them into the invite link.

The `Application ID` can be found on top of the `General Information` of the application.

The bot uses the following permissions:
- Permissions number is: `1643630685398`
- `Send Messages`
- `View Audit Log`
- `Create Public Threads`
- `Create Private Threads`
- `Send Messages in Threads`
- `Manage Roles`
- `Manage Channels`
- `Kick Members`
- `Ban Members`
- `View Channels`
- `Manage Messages`
- `Manage Threads`
- `Embed Links`
- `Attack Files`
- `Read Message History`
- `Manage Webhooks`
- `Use External Emojis`
- `Read Messages / View Channels`
- `Use External Stickers`
- `Mamage Events`
- `Add Reactions`
- `Moderate Members`
- `Use Slash Commands`

Once ready, edit the following link with `application_id`, and open it in a new tab.

[https://discord.com/oauth2/authorize?client_id=<client_id>&permissions=1643630685398&scope=bot%20applications.commands](https://discord.com/oauth2/authorize?client_id=<client_id>&permissions=1643630685398&scope=bot%20applications.commands)