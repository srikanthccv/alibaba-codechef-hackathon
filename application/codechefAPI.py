from flask import session
from pprint import pprint
import requests
import simplejson as json
from datetime import datetime, date, timedelta

from flaskConfiguration import client_id, client_secret

def refreshAccessToken():
	try:
		rqs = refreshToken(session['refresh_token'])
		if(rqs['statuscode'] == 200):
			session['access_token'] = rqs['response']['result']['data']['access_token']
			session['refresh_token'] = rqs['response']['result']['data']['refresh_token']
			session['expires_in'] = datetime.now() + timedelta(0, 1500)
			return True
		return False
	except Exception as e:
		return False

def refreshToken(refresh_token):
	headers = {
		'content-Type': 'application/json'
	}
	postdata = {
		'grant_type': 'refresh_token',
		'refresh_token' : refresh_token,
		'client_id' : client_id,
		'client_secret' : client_secret
	}
	rqs = requests.post('https://api.codechef.com/oauth/token', data=json.dumps(postdata), headers=headers)
	try:
		with open("api_log.txt", "a+") as file:
			file.write(str(datetime.now()) + "\n" + "=" * 50 + '\n')
			file.write('REFRESH TOKEN - ' + refresh_token + '\n')
			file.write("-" * 50 + "\n")
			file.write('RESPONSE DATA\n')
			file.write(rqs.text)
			file.write("\n" + "=" * 50 + '\n\n')
	except Exception as e:
		print(e)
		pass
	return ({"statuscode" : rqs.status_code, "response" : json.loads(rqs.text)})

def get(url, access_token, parameters):
	headers = {'Authorization': 'Bearer ' + access_token}
	rqs = requests.get(url, headers = headers, params = parameters)
	try:
		with open("api_log.txt", "a+") as file:
			file.write(str(datetime.now()) + '\n' + url + '\n' + ("-" * 5) + 'GET' + ("-" * 5) + "\n" + "=" * 50 + '\n')
			file.write('GET PARAMETERS\n')
			json.dump(parameters, file)
			file.write("-" * 50 + "\n")
			file.write('RESPONSE DATA\n')
			file.write(rqs.text)
			file.write("\n" + "*" * 50 + '\n')
	except Exception as e:
		print(e)
		pass
	return ({"statuscode" : rqs.status_code, "response" : json.loads(rqs.text)})

def post(url, access_token, payload):
	headers = {'Authorization': 'Bearer ' + access_token}
	rqs = requests.post(url, headers = headers, data = payload)
	try:
		with open("api_log.txt", "a+") as file:
			file.write(str(datetime.now())+ ' ' + url + ' ' + ("-" * 5) + 'POST' + ("-" * 5) + "\n" + "=" * 50 + '\n')
			file.write('POST PAYLOAD\n')
			json.dump(payload, file)
			file.write("-" * 50 + "\n")
			file.write('RESPONSE DATA\n')
			file.write(rqs.text)
			file.write("\n" + "*" * 50 + '\n')
	except Exception as e:
		print(e)
	return ({"statuscode" : rqs.status_code, "response" : json.loads(rqs.text)})