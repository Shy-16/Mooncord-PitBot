# -*- coding: utf-8 -*-

## Parse Args ##
# Get OS arguments and make sure Token is in it #

import argparse


def parse_args():
    """Parse command-line arguments for the bot."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--token", "-t", default="", help="Add the secret token to login to Discord."
    )
    return parser.parse_args()
