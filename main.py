# -*- coding: utf-8 -*-

## Main Module ##
# Creates and runs the main script and loads all modules #

import sys
import yaml

from bot import Bot
from utils import parse_args

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
        print("PitBot doesn't have the proper permissions to read \"config.yaml\".")
        sys.exit(0)

    bot = Bot(config)
    bot.run(token=args.token)
