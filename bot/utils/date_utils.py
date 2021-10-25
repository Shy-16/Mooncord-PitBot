# -*- coding: utf-8 -*-

## Iso-related conversions ##
# Different decorators for utility #

import datetime
import re
import math

def iso_to_datetime(iso_date):
	"""
	Gets an ISO formatted date

	returns datetime object
	"""

	return datetime.datetime.fromisoformat(iso_date)

def datetime_to_iso(datetime_date):
	"""
	Gets an ISO formatted date

	returns datetime object
	"""

	return datetime_date.toisoformat()


def date_string_to_timedelta(date_string):
	"""Given a string date turn into a proper datetime Object

	@date_string: 30s, 30m, 30h, 30d

	returns: datetime.timedelta
	"""

	regex = '(\d\d?)([smhd])' # Matches (digit, digit?)(letter in [s, m, h, d])

	g = re.search(regex, date_string)
	if g:
		lapse = int(g.group(1)) # can safely convert to int because it only matches digits
		amount = g.group(2)

		delta = None

		if amount == "s":
			delta = datetime.timedelta(seconds=lapse)

		elif amount == "m":
			delta = datetime.timedelta(minutes=lapse)

		elif amount == "h":
			delta = datetime.timedelta(hours=lapse)

		else:
			delta = datetime.timedelta(days=lapse)

		return delta

	try:
		date = datetime.datetime.fromisoformat(date_string)
	except Exception as e:
		return None

	return date - datetime.datetime.now()

def seconds_to_string(seconds):
	"""Given an integer of seconds return a string of time passed

	@seconds: integer

	returns: string
	"""

	if seconds < 60:
		return f"{seconds}s"

	minutes = seconds / 60
	if minutes < 60:
		return "%sm" % math.floor(minutes)

	hours = minutes / 60
	if hours < 24:
		return "%sh" % math.floor(hours)

	days = hours / 24
	return "%sd" % math.floor(days)


if __name__ == '__main__':
	print(date_string_to_timedelta('30s'))
	print(date_string_to_timedelta('30m'))
	print(date_string_to_timedelta('30h'))
	print(date_string_to_timedelta('30d'))

	print(seconds_to_string(15))
	print(seconds_to_string(75))
	print(seconds_to_string(16400))
	print(seconds_to_string(88700))