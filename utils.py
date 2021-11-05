# -*- coding: utf-8 -*-

## Utils ##
# Any utlity functions required to get prepare the bot #

import argparse

def parse_args():
    """
    Parse command-line arguments for the bot.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--token", "-t", default="", help="Add the secret token to login to Discord."
    )

    return parser.parse_args()

if __name__ == '__main__':

    print("Arguments are: ")
    args = parse_args()
    print(args)