# -*- coding: utf-8 -*-

## Main Module ##
# Creates and runs the main script and loads all modules #

import logging
import signal
import sys
import yaml

from bot import Bot
from .utils import parse_args

if __name__ == '__main__':

    args = parse_args()
    if(not args.token):
        print("You need to provide a secret token with \"--token\" or \"-t\" ")
        sys.exit(0)

    try:
        config_file = open('config.yaml', 'r')
        config = yaml.load(config_file, Loader=yaml.FullLoader)

    except FileNotFoundError:
        print("\"config.yaml\" has to exist on root directory.")
        sys.exit(0)

    except IOError:
        print("Pit Bot doesn't have the proper permissions to read \"config.yaml\".")
        sys.exit(0)

    # This logger is used only for Bot information, not discord information.
    logging.basicConfig(filename='bot.log', level=logging.INFO)

    sayo = Bot(config)
    sayo.run(token=args.token)
