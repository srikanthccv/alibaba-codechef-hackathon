from flask import Blueprint, render_template, abort, session, request, jsonify, url_for, redirect
from jinja2 import TemplateNotFound
from flaskConfiguration import monDB, codechefDateFormat
from datetime import datetime, date, timedelta
import application.codechefAPI as codechefAPI
import application.user as user
import requests
from bson.objectid import ObjectId
import simplejson as json
import time
from datetime import datetime, date, timedelta
from bson.objectid import ObjectId
codechefDateFormat = '%Y-%m-%d %H:%M:%S'



api = Blueprint('api', __name__, template_folder='templates')
@api.before_request
def tokenExpireCheck():
	if session['expires_in'] <= datetime.now():
		status = helper.refreshAccessToken()
		if status is not True:
			abort(redirect(url_for('authenticate.logout')))

@api.route('/api/search')
def searchUser():
	q_username = request.args.get('q_username')
	q_offset = request.args.get('q_offset')
	if(session['access_token'] != None):
		headers = {'Authorization': 'Bearer ' + session['access_token']}
		rqs = requests.get('https://api.codechef.com/users?fields&limit=20&offset={0}&search={1}'.format(q_offset, q_username),headers=headers)
		resp = json.loads(rqs.text)
		if(resp['status'] == 'OK' and resp['result']['data']['code'] == 9001):
			retdata = resp['result']['data']['content']
			return jsonify(users=retdata)
		else:
			return jsonify(data={'message': resp['result']['data']['message']})
	else:
		return jsonify(data={'message': 'Unauthorized request', 'status': 'error'})

@api.route('/api/logusersearch', methods = ['POST', 'GET'])
def logUser():
	try:
		payload = request.get_json(force=True)
		post_data = {
			'username': session['username'],
			'friend_username': payload['searched_user'],
			'friend_fullname': payload['searched_fullname'],
			'timestamp' : datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		}
		existed_user = monDB.friends.find_one({'friend_username': payload['searched_user'], 'username': session['username']})
		if(existed_user == None):
			result = monDB.friends.insert_one(post_data)
			return jsonify(data = {'message' : 'Saved Successfully', 'success' : True})
		else:
			return jsonify(data = {'message' : 'This user already exists', 'success': True})
	except Exception as e: 
		print(e)
		return jsonify(data = {'message' : e, 'success': False})

@api.route('/api/friends', methods = ['GET'])
def findFriends():
	try:
		# adding the friends from log search and sets to list
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
		return jsonify(data = friends)
	except Exception as e:
		print (e)
		return jsonify(data = {'message' : e})

@api.route('/api/friend/<friend_id>', methods = ['DELETE'])
def deleteFriend(friend_id):
	friendOBJ = monDB.friends.delete_one({'_id': ObjectId(friend_id)})
	if friendOBJ != None:
		return jsonify(data = {'message' : 'Deleted Successfully', 'success' : True})
	else:
		return jsonify(data = {'message' : 'User is not your friend', 'success' : False})

@api.route('/api/history/<friend_name>')
def getUserHistory(friend_name):
	return jsonify(data=friend_name)

@api.route('/api/submissions/<friend_username>/', methods = ['GET'])
def getUserSubmissions(friend_username):
	refetchSubs = 0
	showAll = 0
	try:
		refetchSubs = int(request.args.get('refetchSubs'))
		showAll = int(request.args.get('showAll'))
		print(refetchSubs, showAll)
	except:
		refetchSubs = 0
		showAll = 0
	friendOBJ = monDB.friends.find_one( { 'friend_username' : friend_username , 'username' : session['username']  } )
	if friendOBJ == None:
		friendOBJ = monDB.sets_people.find_one( { 'friend_username' : friend_username , 'username' : session['username']  } )
	lastVistedTime = ""
	if friendOBJ != None:
		lastVistedTime = datetime.strptime(friendOBJ['timestamp'], codechefDateFormat)
	else:
		return jsonify(data = '{0} is not your friend list'.format(friend_username))
	storedSubmissions = monDB.submissions.find({'username' : friend_username})
	friend_submissions = []
	for submission in storedSubmissions:
			obj = {
				'contestCode': submission['contestCode'],
				'date': submission['date'],
				'id': submission['id'],
				'result': submission['result'],
				'language': submission['language'],
				'problemCode' : submission['problemCode'],
				'username' : submission['username'],
			}
			friend_submissions.append(obj)
	if len(friend_submissions) > 0 and (showAll == 0 or showAll == None) and refetchSubs == 0:
		print(friend_submissions[0])
		print(friendOBJ)
		print(friendOBJ['timestamp'] > friend_submissions[0]['date'])
		friend_submissions = [x for x in friend_submissions if friendOBJ['timestamp'] <= x['date']]
		return jsonify(data = friend_submissions)
	if len(friend_submissions) > 0 and (refetchSubs == 0 or refetchSubs == None):
		return jsonify(data = friend_submissions)
	offset = 0
	latestFetch = getSubmissions(friend_username, offset)
	try:
		if(latestFetch['responsecode'] != 200):
			latestFetch = getSubmissions(friend_username, offset)
		elif(latestFetch['response']['result']['data']['code'] == 9003):
			return jsonify(data = latestFetch)
	except:
		pass
	print('Last Visit to Profile: ' + friendOBJ['timestamp'])
	print('last submission: ' + latestFetch[-1]['date'] if len(latestFetch) != 0  else "")
	friend_submissions += latestFetch
	if len(latestFetch) < 1:
		return jsonify(data = friend_submissions)
	while checkTime(latestFetch[-1]['date'], friendOBJ['timestamp']):
		offset += 1
		latestFetch = getSubmissions(friend_username, offset)
		friend_submissions += latestFetch
	json_data = jsonify(data = friend_submissions)
	# submissions = friend_submissions.copy() #ERROR HERE
	if(len(friend_submissions) > 1):
		# CREATE UNIQUE INDEX AND ADD ------------------ 
		# monDB.submissions.ensuer
		dbObj = monDB.submissions.find_one({"username" : friend_username})
		print(len(friend_submissions))
		if dbObj != None:
			friend_submissions = [x for x in friend_submissions if dbObj['date'] < x['date']]
			if len(friend_submissions) < 1:
				return json_data
		try:
			monDB.submissions.insert_many(friend_submissions, ordered= False)
		except Exception as e:
			print(e)
	return json_data

@api.route('/api/mytodolist', methods = ['POST'])
def addTODOList():
	postdata = request.get_json(force=True)
	payload = {
		"problemCode": postdata['problemCode'], 
		"contestCode": postdata['contestCode'],
	}
	try:
		rqs = codechefAPI.post('https://api.codechef.com/todo/add', session['access_token'], payload)
		if rqs["statuscode"] == 200:
			return jsonify(data = rqs['response']['result']['data']['message'])
		return jsonify(data = "Some error occcured")
	except Exception as e:
		print(e)
		return jsonify(data = e)

@api.route('/api/logvisit/<friend_username>/', methods= ['PUT'])
def logUserVisit(friend_username):
	try:
		friendObj = monDB.friends.find_and_modify(query = {'username': session['username'], 'friend_username' : friend_username}, update = {"$set": {'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')} })
		if friendObj != None:
			return jsonify(success = "true")
		else:
			return jsonify(success = "false")
	except Exception as e:
		print(e)
		return jsonify(success = "false")

@api.route('/api/populate/<friend_username>/', methods = ['GET'])
def populateTable(friend_username):
	offset = 0
	friend_submissions = list()
	latestFetch = getSubmissions(friend_username, offset)
	try:
		if(latestFetch['responsecode'] != 200):
			latestFetch = getSubmissions(friend_username, offset)
	except:
		pass
	friend_submissions += latestFetch
	if len(latestFetch) < 1:
		return jsonify(success = False)
	while offset < 10 and len(latestFetch) > 0:
		offset += 1
		latestFetch = getSubmissions(friend_username, offset)
		try:
			if(latestFetch['responsecode'] != 200):
				helper.refreshAccessToken()
		except:
			friend_submissions += latestFetch
	
	dbObj = monDB.submissions.find_one({"username" : friend_username})
	print(len(friend_submissions))
	print(dbObj)
	if dbObj != None:
		friend_submissions = [x for x in friend_submissions if dbObj['date'] < x['date']]
	print(len(friend_submissions))
	if len(friend_submissions) < 1:
		return jsonify(success = True)
	try:
		monDB.submissions.insert_many(friend_submissions, ordered= False)
	except Exception as e: #PREVENTS DUP ADDITION OF SUBMISSIONS
		print(e)
		print('-' * 75)
	return jsonify(success = True)

def getSubmissions(username, field_offset):
	response_data = ''
	try:
		params = {'username' : username, 'limit' : 1500, 'offset' : field_offset * 1500 }
		print(field_offset, '-*' * 50)
		rqs = codechefAPI.get('https://api.codechef.com/submissions/', session['access_token'], params)
		print(rqs)
		print(username, '-*' * 50)
		if rqs["statuscode"] == 200:
			return rqs['response']['result']['data']['content']
		return []
	except Exception as e:
		print(e)
		return []

def checkTime(friendLastSubsion, userLastVisit):
	return datetime.strptime(friendLastSubsion, codechefDateFormat) > datetime.strptime(userLastVisit, codechefDateFormat)
