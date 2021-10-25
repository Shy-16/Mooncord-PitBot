
# Bot Module

This module initializes the Bot that connects to discord.

## Usage

### Commands.

Each command is under `commands` folder, which has a help section. Generally to call the help of each command just type the command without any params, with `config` being the only exception.

#### Command Inteface 
All commands implement the following interface:

- Execute

	Execute the command regularly through the command instruction.
	
	`Example: !timeout`

- DM

	Users can't dm the bot a list of words which will be parsed as natural language through a tokenization process and will execute the command through DMs.
	
	`Example: remaining time` - This will show remaining time of a timeout of a user.

- Ping

	When pinging the bot you can execute a command using natural language instead of having to do the strict command structure of Execute.
	
	`Example: @pitbot timeout @yui for 30d for being too cute`

#### Timeout
Timeout command will timeout a user for a certain amount of time, add a strike to their account and when the timeout expires will release them automatically.
If this command is issued a second time while a timeout is still active, it will extend the duration instead.

- Execute

	`!timeout @user <time> <reason:optional>`

	`<time>` takes one of: `s m h d` where `s is second, m is minute, h is hour, d is day`

	`<reason>`takes a string to include as an option during the timeout.


	`Example: !timeout @yui 1d posted elf tits in weebs`

- DM

	One of the following words will trigger the command: `['ban', 'time', 'remaining', 'timeout']`

	This will give the person who DMd information regarding any active timeout they have, including how much remaining time it's left.

- Ping

	`@pitbot timeout|ban @user for <time> for <reason>`

	`<timeout|ban>` means that you can use either of both

	`<time>` takes one of the same parameters as Execute

	`<reason>` takes a string to  include as a reason. This is **not** optional


	``Example: @pitbot timeout @yui for 30d for being too cute``
	
#### Timeoutns
Timeoutns (Timeout no strike) command will timeout a user for a certain amount of time **without** adding strike to their account and when the timeout expires will release them automatically.
If this command is issued a second time while a timeout is still active, it will extend the duration instead.

Usage syntax is the same as `Timeout`

#### Release
Release command will release a user from a timeout, optionally also removing the strike they got added for it.

- Execute

	`!release @user <ammend:optional>`

	`<ammend>` If is provided after `@user`, it will **delete** the last strike issued from a Timeout.

	This means the strike will not be marked as "expired" but will be removed from database as it never existed.


	`Example: !release @yui ammend`

- DM

	*Not implemented*

- Ping

	*Not implemented*

#### Strikes
Strikes command can list the amount of strikes of a user and add or remove a strike from a user.

- Execute Show

	`!strikes @user <verbose|optional>`

	`<verbose>` takes the string `verbose` and will include full information of strikes.


	`Example: !strikes @yui verbose`

- Execute Add

	`!strikes @user add <reason>`

	`<reason>` takes the string and will include as reason for strike.


	`Example: !strikes @yui add baited ot into liking anime`

- Execute Remove

	`!strikes @user rm|remove <strike_id>`

	`rm|remove` either of both is accepted.

	`<strike_id>` is the UniqueID provided on the list of strikes of the user, which uniquely identify each strike.

	The ID of the strike can be seen using `verbose` during `Execute Show` command.


	`Example: !strikes @yui rm 60ede37bde0408b1a92a2b66`

- DM

	One of the following words will trigger the command: `['strikes', 'pithistory', 'history']`

	This will give the person who DMd information regarding all the strikes they have in the server.

- Ping

	*Not implemented*

#### Config
Config command will show current server configuration.
If the parameter is a list, you have to use `add|rm` command.
If its just a paremeter then `set` command.

- Execute Show

	`!config`

	`Example: !config`

- Execute set for single parameter

	`!config <parameter> set <value>`

	`<parameter>` takes a string exactly as it is shown in `Show` command.

	`<value>` takes an acceptable value for the parameter you're setting.


	`Example: !config log_channel set #log_important`

- Execute add|rm value from list

	`!config <parameter> add|rm <value>`

	`add|rm` either of both is accepted. `add` for adding, `rm` for removing

	`<value>` takes an acceptable value for the parameter you're setting.


	`Example: !config admin_roles add @Administrators`

- DM

	*Not implemented*

- Ping

	*Not implemented*

#### Roles
Roles will add or remove a list of roles to a list of users.

- Execute 

	`!roles add|rm @user_1 @user_2 ... @role_1 @role_2 ...`

	`@user_1 @user_2 ...`is a list of users separated by spaces.

	`@role_1 @role_2 ...`is a list of roles separated by spaces.


	`Example: !roles add @yui @shy @nyx @amayasin @GAMEJAM @GAMEDEV @artist`

	Note: It doesn't matter at all the order of roles or users. The bot determines which ones are roles and users so you can just keep adding as you need.

- DM

	*Not implemented*

- Ping

	*Not implemented*

#### Help
Help command.

- Execute Show

	`!help`

	`Example: !help`

- DM

	One of the following words will trigger the command: `['help', 'elp']`

- Ping

	*Not implemented*
