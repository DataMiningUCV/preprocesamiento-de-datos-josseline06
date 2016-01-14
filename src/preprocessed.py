from sklearn import preprocessing as scikit
import pandas
import os
import re


input_data = pandas.read_csv('/dat/data.csv', header=None, skiprows=1)

period_messy = input_data[1].str.replace('[ \\\\-]','')
output_data = period_messy.str.extract('^(?P<period_year>(?:20)?[0-9]{2})(?P<period_nro>pri(?:mero)?|seg(?:undo)?|ii?|0?[12]s?)$', re.IGNORECASE)
period_p2 = period_messy.str.extract('^(?P<period_nro>pri(?:mero)?|seg(?:undo)?|ii?|0?[12]s?)(?P<period_year>(?:20)?[0-9]{2})$', re.IGNORECASE)

output_data.update(period_p2)

output_data.nro = period.nro.str.replace('pri(mero)?|i|0?1s?', '1', flags=re.IGNORECASE).str.replace('seg(undo)?|ii|0?2s?', '2', flags=re.IGNORECASE)
output_data.year = period.year.str.replace('[0-9]{2}', '20[0-9]{2}', flags=re.IGNORECASE)
