# -*- coding: utf-8 -*-

## Main Module ##
# Creates and runs the main script and loads all modules #

import logging
import signal
import sys
import yaml

from bot.sayo import Sayo
from bot.utils import parse_args

if __name__ == '__main__':

    args = parse_args()
    try:
        config_file = open('config.yaml', 'r')
        config = yaml.load(config_file, Loader=yaml.FullLoader)

    except FileNotFoundError:
        print("\"config.yaml\" has to exist on root directory.")
        sys.exit(0)

    except IOError:
        print("Sayo doesn't have the proper permissions to read \"config.yaml\".")
        sys.exit(0)

    def on_break(signal, frame):
        print("Sayo is now exiting.")

    # This logger is used only for Bot information, not discord information.
    logging.basicConfig(filename='bot.log', level=logging.INFO)

    sayo = Sayo(config, args)
    sayo.run()
