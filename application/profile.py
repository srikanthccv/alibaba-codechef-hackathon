from flask import Blueprint, render_template, abort, session, request, jsonify, url_for, redirect
from jinja2 import TemplateNotFound
from flaskConfiguration import monDB, codechefDateFormat
import application.user as user
from datetime import datetime, date, timedelta
import application.codechefAPI as helper

profile_page = Blueprint('profile_page', __name__, template_folder='templates')

@profile_page.before_request
def tokeExpiryCheck():
	try:
		if session['expires_in'] <= datetime.now():
			status = helper.refreshAccessToken()
			if status is not True:
				abort(redirect(url_for('authenticate.logout')))
	except:
		abort(redirect(url_for('authenticate.logout')))

@profile_page.route('/profile/<friend_username>')
def getProfile(friend_username):
	friendOBJ = monDB.friends.find_one( { 'friend_username' : friend_username , 'username' : session['username']  } )
	if friendOBJ != None:
		lastVisitedString = ''
		try:
			visitedDate = (datetime.strptime(friendOBJ['timestamp'], codechefDateFormat))
			lastVisitedString = pretty_time_delta((visitedDate - datetime(1970, 1, 1)).total_seconds())
		except:
			print('date parse failed')
			pass
		viewdata = {
			'friend_username' : friend_username,
			'timestamp' : lastVisitedString,
			'success' : True
		}
		return render_template('profile.html', data = viewdata)
	else:
		viewdata = {'success' : False, 'message' : 'User is not your friend list'}
		return render_template('profile.html', data = viewdata)

def pretty_time_delta(seconds):
	seconds = int(seconds)
	currentSeconds = (datetime.now() - datetime(1970, 1, 1)).total_seconds()
	currentDif = (currentSeconds - seconds)
	months, seconds = divmod(int(currentDif), 2628000)
	days, seconds = divmod(seconds, 86400)
	hours, seconds = divmod(seconds, 3600)
	minutes, seconds = divmod(seconds, 60)
	if months > 0:
		return ('{0}m {1}d {2}h {3}m {4}s'.format(months, days, hours, minutes, seconds))
	elif days > 0:
		return ('{0}d {1}h {2}m {3}s'.format(days, hours, minutes, seconds))
	elif hours > 0:
		return ('{0}h {1}m {2}s'.format(hours, minutes, seconds))
	elif minutes > 0:
		return ('{0}m {1}s'.format(minutes, seconds))
	else:
		return ('{0}s'.format(seconds))