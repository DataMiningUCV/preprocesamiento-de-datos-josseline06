import pandas
import re

input_data = pandas.read_csv('/dat/data.csv', header=None, skiprows=1)

period_messy = input_data[1].str.replace('[ \\\\-]','')
period = period_messy.str.extract('^(?P<year>(?:20)?[0-9]{2})(?P<nro>pri(?:mero)?|seg(?:undo)?|ii?|0?[12]s?)$', re.IGNORECASE)
period_p2 = period_messy.str.extract('^(?P<nro>pri(?:mero)?|seg(?:undo)?|ii?|0?[12]s?)(?P<year>(?:20)?[0-9]{2})$', re.IGNORECASE)

period.update(period_p2)

period.nro = period.nro.str.replace('pri(mero)?|i|0?1s?', '1', flags=re.IGNORECASE).str.replace('seg(undo)?|ii|0?2s?', '2', flags=re.IGNORECASE)
period.year = period.year.str.replace('^[0-9]{2}$', lambda str: '20'+str)