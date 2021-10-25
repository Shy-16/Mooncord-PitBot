# -*- coding: utf-8 -*-

## Sayo Logging Module ##
# Helper for logging for all commands, events and everything Discord-related. #

import json
import datetime, time, pytz
import logging
from logging.handlers import WatchedFileHandler
import traceback
import pprint

class MyJsonEncoder(json.JSONEncoder): 
    """
    a json encoder that encodes datetime as an ISO date, (default json encoder doesn't handle datetimes)
    """
    
    def default(self, obj):         # pylint: disable=arguments-differ
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()

        return json.JSONEncoder.default(self, obj)

def init_log():
    """
    Init logging. The must be called only once upon instantiation.
    """

    logger = logging.getLogger("sayo_log")

    logger.setLevel(logging.INFO)    # this sets the min level of logging that this logger will handle.

    hand_fh_info  = WatchedFileHandler("discord.log")
    hand_fh_info.setLevel(logging.INFO)
    hand_fh_info.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(hand_fh_info)

async def do_log(place="guild", data_dict="", message=None, member=None, level=logging.INFO, exception=False):
    """
    place		- where is logging: "dm", "guild", "ping"...
    data_dict	- contains a dict of the data to log. Can also be a plain string.
    message		- message context of the query
    level		- is one of logging.ERROR, etc.
    exception	- will dump a stack trace if True

    if message is given member will be ignored.
    """

    try:
        # make data_dict a dict if it is not already

        if not isinstance(data_dict, dict):
            data_dict = {"msg": data_dict}

        if isinstance(data_dict.get('data'), bytes):
            data_dict['data'] = str(data_dict['data'], 'utf-8')

        # add some log-related info 
        data_dict['unix_timestamp'] = time.time()
        data_dict['level'] = logging.getLevelName(level)
        data_dict['type'] = place
        data_dict['date'] = datetime.datetime.now().isoformat()
        data_dict['date_pt'] = datetime.datetime.now(pytz.timezone('US/Pacific')).isoformat()

        # add info related to message
        if message is not None:
        	data_dict['content'] = message.content
        	data_dict['author_id'] = message.author.id
        	data_dict['author_handle'] = message.author.name + "#" + message.author.discriminator

        	if message.guild is not None:
        		data_dict['guild_id'] = message.guild.id

        	if len(message.mentions) > 0:
        		if len(message.mentions) == 1:
        			data_dict['user_id'] = message.mentions[0].id
        			data_dict['user_handle'] = f'{message.mentions[0].name}#{message.mentions[0].discriminator}'

        		else:
	        		for i in range(len(message.mentions)):
	        			data_dict[f'mention_{i}'] = message.mentions[i].id
	        			data_dict[f'mention_{i}_handle'] = f'{message.mentions[i].name}#{message.mentions[i].discriminator}'

        elif member is not None:
        	data_dict['guild_id'] = member.guild.id
        	data_dict['user_id'] = member.id
        	data_dict['user_handle'] = f'{member.name}#{member.discriminator}'


        # if it is an exception, get some traceback info
        if exception:
            level = logging.CRITICAL
            data_dict['level'] = logging.getLevelName(level)
            exc_err = traceback.format_exc()
            exc_tb  = "".join(traceback.format_stack())
            exc_tb = exc_tb.replace("\\n", "\n")

            data_dict['exception'] = exc_err + exc_tb
            print(exc_err + exc_tb)

        rlogger = logging.getLogger("sayo_log")
        rlogger.log(level, json.dumps(data_dict, cls=MyJsonEncoder))

    except Exception as ex:
        print("utils.do_log() FAILED: %s" % ex)
        pprint.pprint(data_dict)


if __name__ == '__main__':
	init_log()
	do_log()