"""Colours for NISV House Style and number formats and separators for CLARIAH"""
import locale

BLUE = "#009fda"
PINK = "#e00034"
GREY = "#c7c2ba"
YELLOW = "#fce300"
PURPLE = "#56197b"
LILAC = "#dcbdab"
GREEN = "#92d400"
ORANGE = "#ff5800"
JADE = "#00b400"
ROYAL_BLUE = "#0028be"

# below is technically speaking not NISV House style but what we have chosen in CLARIAH

def formatNumber(number, decimalPlaces = 0):
	"""Formats the number into a string according to the user's default setting
	Returns the formatted string"""

	locale.setlocale(locale.LC_ALL, '')
	formatString = "%%.%df"%decimalPlaces
	return locale.format_string(formatString, number, grouping = True)


def formatNumberList(numberList, decimalPlaces = 0):
	"""Formats each number in the list into a string according to the user's default setting
	Returns a list of the formatted strings"""

	locale.setlocale(locale.LC_ALL, '')
	formatString = "%%.%df"%decimalPlaces
	return list(map(lambda x: locale.format(formatString, x, grouping = True), numberList))


def getSeparators():
	"""Returns a string with first the decimal separator, then the thousands separator. E.g. in English
	this would be ".," - example number 1,222,333.2345.  Note that the return format is that required
	by Plotly when setting separators in figures"""

	decimalPoint = locale.localeconv()['decimal_point']
	thousandsSep = locale.localeconv()['thousands_sep']
	return decimalPoint + thousandsSep
