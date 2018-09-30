from flask import Blueprint, render_template, abort, session, request, jsonify, url_for, redirect
from jinja2 import TemplateNotFound
import requests
import pprint
import simplejson as json
from collections import OrderedDict
from datetime import datetime, date, timedelta
import application.codechefAPI as helper
from flaskConfiguration import monDB
import random
statistics_page = Blueprint('statistics_page', __name__, template_folder='templates')

@statistics_page.before_request
def tokenExpireCheck():
	try:
		if session['expires_in'] <= datetime.now():
			status = helper.refreshAccessToken()
			if status is not True:
				abort(redirect(url_for('authenticate.logout')))
	except:
		abort(redirect(url_for('authenticate.logout')))


@statistics_page.route('/stats/tags/<friend_username>')
def tags(friend_username):
	fullname = friend_username
	headers = {'Authorization': 'Bearer ' + session['access_token']}
	# gets the user problem statistics
	userProfileResponse = requests.get("https://api.codechef.com/users/{0}?fields=problemStats".format(friend_username), headers=headers)
	userProfileResponse = json.loads(userProfileResponse.text)
	print (userProfileResponse)
	problemStats = {}
	if(userProfileResponse['status'] == 'OK' and userProfileResponse['result']['data']['code'] == 9001):
		problemStats = userProfileResponse['result']['data']['content']['problemStats']['solved']
		fullname = userProfileResponse['result']['data']['content']['fullname']
	tags = {}
	# iterate over all the solved problems and aggregate tags
	for contestCode, solvedProblems in problemStats.items():
		for problemCode in solvedProblems:
			# fetch the tags for given problem -- incomplete db, may not be accurate results
			res = monDB.tags.find_one({'contestCode': contestCode, 'problemCode': problemCode})
			if(res != None):
				for tag in res['tags']:
					if str(tag) == contestCode.lower():
						continue
					if tag not in tags:
						tags[tag] = 0
					tags[tag] = tags[tag] + 1
	print (tags)
	tags = OrderedDict(sorted(tags.items(), key=lambda x: x[1]))
	orderedTags = []
	# prepare data pie chart 
	for key, val in tags.items():
		orderedTags.append({'name': str(key), 'y':val})
	orderedTags = orderedTags[::-1]
	# shows only top 20 tags data
	orderedTags = orderedTags[:min(20, len(orderedTags))]
	orderedTags = json.dumps(orderedTags)
	# for footer of tags page
	randomList = getFiveRandomFriends()
	try:
		return render_template('tags.html', tags=orderedTags, username=friend_username, fullname=fullname, randomList = randomList)
	except TemplateNotFound:
		abort(404)

def getFiveRandomFriends():
	friends = monDB.friends.find()
	friendsList = {}
	randomList = {}
	for x in friends:
		friendsList[x['friend_username']] = x['friend_fullname']
	keys = list(friendsList.keys())
	random.shuffle(keys)
	maxRand = min(5, len(keys))
	for key in keys:
		if maxRand > 0:
			maxRand = maxRand-1
			randomList[key] = friendsList[key]
	return randomList

@statistics_page.route('/stats/problems/<friend_username>')
def tagProblems(friend_username):
	tag = request.args.get('tag')
	headers = {'Authorization': 'Bearer ' + session['access_token']}
	# initialize the empty problem list
	tagProblemsUser = []
	# api request for user profile
	userProfileResponse = requests.get("https://api.codechef.com/users/{0}?fields=problemStats".format(friend_username), headers=headers)
	userProfileResponse = json.loads(userProfileResponse.text)
	# 
	if(userProfileResponse['status'] == 'OK' and userProfileResponse['result']['data']['code'] == 9001):
		problemStats = userProfileResponse['result']['data']['content']['problemStats']['solved']
	else:
		problemStats = {}
	for contestCode, solvedProblems in problemStats.items():
		for problemCode in solvedProblems:
			problemTags = monDB.tags.find_one({'contestCode': contestCode, 'problemCode': problemCode})
			if(problemTags != None and tag in problemTags['tags']):
				tagProblemsUser.append({'problemCode': problemCode, 'contestCode': contestCode})
	try:
		userFriends = findFriends()
		return render_template('tag_problems_user.html',userFriends = userFriends, tagProblemsUser=tagProblemsUser, friend_username=friend_username)
	except TemplateNotFound:
		abort(404)

def findFriends():
	friends = []
	dbUsers = monDB.friends.find({
		'username': session['username']
	})
	for friend in dbUsers:
		obh = {
			'friend_username': friend['friend_username'], 
			'friend_fullname': friend['friend_fullname'].title(),
			'timestamp': friend['timestamp'],
			'friend_id': str(friend['_id'])
		}
		friends.append(obh)
	return friends