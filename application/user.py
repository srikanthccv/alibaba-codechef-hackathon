from flask import Blueprint, render_template, abort, session, request, jsonify, url_for, redirect
from jinja2 import TemplateNotFound
from flaskConfiguration import monDB
import requests
import simplejson as json
from datetime import datetime, date, timedelta

def setUserDetails(access_token):
	headers = {'Authorization': 'Bearer ' + access_token}
	apiResponse = requests.get('https://api.codechef.com/users/me',headers=headers)
	apiResponse = json.loads(apiResponse.text)
	try:
		if apiResponse['status'] == 'OK':
			session['username'] = apiResponse['result']['data']['content']['username']
			session['fullname'] = apiResponse['result']['data']['content']['fullname'].title()
			session['expires_in'] = datetime.now() + timedelta(0, 1500)
	except Exception as e: 
		print(e)
		pass

def addPeopleFromSetsToFriendsList(access_token):
	headers = {'Authorization': 'Bearer ' + access_token}
	# fetch all set of user
	rqs = requests.get('https://api.codechef.com/sets',headers=headers)
	resp = json.loads(rqs.text)
	setNames = []
	if(resp['status'] == 'OK' and resp['result']['data']['code'] == 9001):
		setNames = [each_set['setName'] for each_set in resp['result']['data']['content']]
	all_members = []
	# iterate over each set and prepare all set members list
	for setName in setNames:
		memb_rqs = requests.get('https://api.codechef.com/sets/members/get?setName={0}'.format(setName),headers=headers)
		memb_resp = json.loads(memb_rqs.text)
		if(memb_resp['status'] == 'OK' and memb_resp['result']['data']['code'] == 9001):
			members = [member['memberName'] for member in memb_resp['result']['data']['content']]
			all_members.extend(members)
	# add people from sets to db
	print(all_members)
	add_cnt = 0
	for member in all_members:
		in_collection = monDB.friends.find_one({'friend_username': member, 'username': session['username']})
		# add if member is not persent in friends
		if(in_collection == None):
			memb_rqs = requests.get('https://api.codechef.com/users/{0}'.format(member),headers=headers)
			memb_resp = json.loads(memb_rqs.text)
			member_fullname = member
			if memb_resp['status'] == 'OK' and memb_resp['result']['data']['code'] == 9001:
				member_fullname = memb_resp['result']['data']['content']['fullname']
			data = {
				'username': session['username'],
				'friend_username': member,
				'friend_fullname': member_fullname,
				'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			}
			result = monDB.friends.insert_one(data)
			add_cnt = add_cnt + 1
	print ('Added {0} to friends list'.format(add_cnt))