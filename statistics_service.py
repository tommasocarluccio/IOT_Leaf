# non so dove mettere questo file
# ma sicuramente non deve stare qui

import json
import requests
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta 

def retrieveData(channelID, date_start, date_end):
	
	# format dates
	date_now = date_start.strftime("%Y-%m-%d %H:%M:%S").split()
	date_last = date_end.strftime("%Y-%m-%d %H:%M:%S").split()
	end_date = '%20'.join(date_now)
	start_date = '%20'.join(date_last)

	# format thingspeak request
	request_url = f'https://api.thingspeak.com/channels/{channelID}/feeds.json?start={start_date}&end={end_date}'
	res = requests.get(request_url)

	return res.json()

def calculateStats(json_response):

	# get element into list
	AQI = []
	temp = []
	hum = []
	for feed in json_response['feeds']:
		AQI.append(feed['field1'])
		temp.append(feed['field3'])
		hum.append(feed['field5'])
	AQI = np.array(AQI).astype(float)
	temp = np.array(temp).astype(float)
	hum = np.array(hum).astype(float)
	
	# remove nan
	AQI = AQI[~(np.isnan(AQI))]
	temp = temp[~(np.isnan(temp))]
	hum = hum[~(np.isnan(hum))]

	resp = {}
	resp['AQI'] = {}
	resp['temp'] = {}
	resp['hum'] = {}
	if AQI.size > 0:
		resp['AQI']['avg'] = AQI.mean()
		resp['AQI']['max'] = AQI.max()
		resp['AQI']['min'] = AQI.min()
	else:
		resp['AQI']['avg'] = 'no_data'
		resp['AQI']['max'] = 'no_data'
		resp['AQI']['min'] = 'no_data'
	if temp.size > 0:
		resp['temp']['avg'] = temp.mean()
		resp['temp']['max'] = temp.max()
		resp['temp']['min'] = temp.min()
	else:
		resp['temp']['avg'] = 'no_data'
		resp['temp']['max'] = 'no_data'
		resp['temp']['min'] = 'no_data'
	if hum.size > 0:
		resp['hum']['avg'] = hum.mean()
		resp['hum']['max'] = hum.max()
		resp['hum']['min'] = hum.min()
	else:
		resp['hum']['avg'] = 'no_data'
		resp['hum']['max'] = 'no_data'
		resp['hum']['min'] = 'no_data'

	return resp

if __name__ == '__main__':

	# request data to thingspeak
	channelID = '1021300'
	period = 'week' # day OR week OR month

	# check dates
	now = datetime.now()
	if period == 'day':
		last_period_date = now + relativedelta(days=-1)
		res = retrieveData(channelID, now, last_period_date)
		respDEF = calculateStats(res)

		NUM_DAYS = 7
		avg_lastAQI = 0
		avg_lastTemp = 0
		avg_lastHum = 0

		try:
			# query for avgs of last 7 days
			for d in range(NUM_DAYS):
				now = last_period_date
				last_period_date = now + relativedelta(days=-1)
				res = retrieveData(channelID, now, last_period_date)
				resp = calculateStats(res)
				avg_lastAQI += resp['AQI']['avg']
				avg_lastTemp += resp['temp']['avg']
				avg_lastHum += resp['hum']['avg']
			avg_lastAQI /= NUM_DAYS
			avg_lastTemp /= NUM_DAYS
			avg_lastHum /= NUM_DAYS

			# print advice msg
			if respDEF['AQI']['avg'] > avg_lastAQI:
				AQI_avice = f'The average AQI today is higher than the previous {NUM_DAYS} days! (avg: {avg_lastAQI})'
			else:
				AQI_avice = f'The average AQI today is lower than the previous {NUM_DAYS} days! (avg: {avg_lastAQI})'
			if respDEF['temp']['avg'] > avg_lastTemp:
				temp_avice = f'The average temperature today is higher than the previous {NUM_DAYS} days! (avg: {avg_lastTemp})'
			else:
				temp_avice = f'The average temperature today is lower than the previous {NUM_DAYS} days! (avg: {avg_lastTemp})'
			if respDEF['hum']['avg'] > avg_lastHum:
				hum_avice = f'The average humidity today is higher than the previous {NUM_DAYS} days! (avg: {avg_lastHum})'
			else:
				hum_avice = f'The average humidity today is lower than the previous {NUM_DAYS} days! (avg: {avg_lastHum})'
		except: 
			'Could not find enough data'
			AQI_avice = 'not enough data'
			temp_avice = 'not enough data'
			hum_avice = 'not enough data'

	elif period == 'week':
		last_period_date = now + relativedelta(weeks=-1)
		res = retrieveData(channelID, now, last_period_date)
		respDEF = calculateStats(res)

		NUM_WEEKS = 4
		avg_lastAQI = 0
		avg_lastTemp = 0
		avg_lastHum = 0

		try: 
			for d in range(NUM_WEEKS):
				now = last_period_date
				last_period_date = now + relativedelta(weeks=-1)
				res = retrieveData(channelID, now, last_period_date)
				resp = calculateStats(res)
				avg_lastAQI += resp['AQI']['avg']
				avg_lastTemp += resp['temp']['avg']
				avg_lastHum += resp['hum']['avg']
			avg_lastAQI /= NUM_WEEKS
			avg_lastTemp /= NUM_WEEKS
			avg_lastHum /= NUM_WEEKS

			if respDEF['AQI']['avg'] > avg_lastAQI:
				AQI_avice = f'The average AQI today is higher than the previous {NUM_WEEKS} weeks! (avg: {avg_lastAQI})'
			else:
				AQI_avice = f'The average AQI today is lower than the previous {NUM_WEEKS} weeks! (avg: {avg_lastAQI})'
			if respDEF['temp']['avg'] > avg_lastTemp:
				temp_avice = f'The average temperature today is higher than the previous {NUM_WEEKS} weeks! (avg: {avg_lastTemp})'
			else:
				temp_avice = f'The average temperature today is lower than the previous {NUM_WEEKS} weeks! (avg: {avg_lastTemp})'
			if respDEF['hum']['avg'] > avg_lastHum:
				hum_avice = f'The average humidity today is higher than the previous {NUM_WEEKS} weeks! (avg: {avg_lastHum})'
			else:
				hum_avice = f'The average humidity today is lower than the previous {NUM_WEEKS} weeks! (avg: {avg_lastHum})'
		except:
			'Could not find enough data'
			AQI_avice = 'not enough data'
			temp_avice = 'not enough data'
			hum_avice = 'not enough data'


	elif period == 'month':
		last_period_date = now + relativedelta(months=-1)
		res = retrieveData(channelID, now, last_period_date)
		respDEF = calculateStats(res)

		NUM_MONTHS = 2
		avg_lastAQI = 0
		avg_lastTemp = 0
		avg_lastHum = 0

		try:
			for d in range(NUM_MONTHS):
				now = last_period_date
				last_period_date = now + relativedelta(months=-1)
				res = retrieveData(channelID, now, last_period_date)
				resp = calculateStats(res)
				avg_lastAQI += resp['AQI']['avg']
				avg_lastTemp += resp['temp']['avg']
				avg_lastHum += resp['hum']['avg']
			avg_lastAQI /= NUM_MONTHS
			avg_lastTemp /= NUM_MONTHS
			avg_lastHum /= NUM_MONTHS

			if respDEF['AQI']['avg'] > avg_lastAQI:
				AQI_avice = f'The average AQI today is higher than the previous {NUM_MONTHS} months! (avg: {avg_lastAQI})'
			else:
				AQI_avice = f'The average AQI today is lower than the previous {NUM_MONTHS} months! (avg: {avg_lastAQI})'
			if respDEF['temp']['avg'] > avg_lastTemp:
				temp_avice = f'The average temperature today is higher than the previous {NUM_MONTHS} months! (avg: {avg_lastTemp})'
			else:
				temp_avice = f'The average temperature today is lower than the previous {NUM_MONTHS} months! (avg: {avg_lastTemp})'
			if respDEF['hum']['avg'] > avg_lastHum:
				hum_avice = f'The average humidity today is higher than the previous {NUM_MONTHS} months! (avg: {avg_lastHum})'
			else:
				hum_avice = f'The average humidity today is lower than the previous {NUM_MONTHS} months! (avg: {avg_lastHum})'
		except:
			'Could not find enough data'
			AQI_avice = 'not enough data'
			temp_avice = 'not enough data'
			hum_avice = 'not enough data'

	respDEF['AQI']['Advice'] = AQI_avice
	respDEF['temp']['Advice'] = temp_avice
	respDEF['hum']['Advice'] = hum_avice

	print(respDEF)

