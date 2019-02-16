from flask import Blueprint, render_template, abort, session, request, jsonify, url_for, redirect
from jinja2 import TemplateNotFound
from pymongo import MongoClient
from datetime import datetime, date, timedelta
import application.codechefAPI as helper
import application.api as api

from flaskConfiguration import monDB, codechefDateFormat


activetime = Blueprint('activetime', __name__, template_folder='templates')

@activetime.before_request
def tokenExpireCheck():
	try:
		if session['expires_in'] <= datetime.now():
			status = helper.refreshAccessToken()
			if status is not True:
				abort(redirect(url_for('authenticate.logout')))
	except:
		abort(redirect(url_for('authenticate.logout')))


@activetime.route('/activetime/<friend_username>/')
def useractiveTime(friend_username):
	subs = monDB.submissions.find({ 'username' : friend_username})
	if subs.count() == 0:
		api.populateTable(friend_username)
		subs = monDB.submissions.find({ 'username' : friend_username})
	subinterval = dict()
	submissionsList = list()
	for submission in subs:
		minStamp = submission['date'][11:13] + ":" + '{0:02d}'.format(int(int(submission['date'][14:16]) / 15) * 15)
		minStamp += "-" + submission['date'][11:13] + ":" + '{0:02d}'.format((int(int(submission['date'][14:16]) / 15) * 15) + 14)
		submissionsList.append(minStamp)
		try:
			subinterval[minStamp] += 1
		except:
			subinterval[minStamp] = 1
			pass
	submissionsList = list(set(submissionsList))
	submissionsList.sort()
	try:
		return render_template('activetime.html', friend_username = friend_username, intervals = submissionsList, values = list(subinterval.values()))
	except TemplateNotFound:
		abort(404)