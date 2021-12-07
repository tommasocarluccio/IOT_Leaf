# non so dove mettere questo file
# ma sicuramente non deve stare qui

import json
import requests
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta 

def retrieveData(channelID, period='month'):

	# check dates
	now = datetime.now()
	if period == 'day':
		last_period_date = now + relativedelta(days=-1)
	elif period == 'week':
		last_period_date = now + relativedelta(weeks=-1)
	elif period == 'month':
		last_period_date = now + relativedelta(months=-1)
	
	# format dates
	date_now = now.strftime("%Y-%m-%d %H:%M:%S").split()
	date_last = last_period_date.strftime("%Y-%m-%d %H:%M:%S").split()
	end_date = '%20'.join(date_now)
	start_date = '%20'.join(date_last)

	# format thingspeak request
	request_url = f'https://api.thingspeak.com/channels/{channelID}/feeds.json?start={start_date}&end={end_date}'
	res = requests.get(request_url)

	return res.json()

def calculateAvgs(json_response):

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

	return AQI.mean(), temp.mean(), hum.mean()

if __name__ == '__main__':

	# request data to thingspeak
	channelID = '1021300'
	period = 'month' # day OR week OR month
	res = retrieveData(channelID, period)

	# calculate avgs
	AQI_avg, temp_avg, hum_avg = calculateAvgs(res)
	print(AQI_avg, temp_avg, hum_avg)

