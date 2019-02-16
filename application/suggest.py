from flask import Blueprint, render_template, abort, session, request, jsonify, url_for, redirect
from jinja2 import TemplateNotFound
from datetime import datetime, date, timedelta
import application.codechefAPI as helper
from flaskConfiguration import monDB

suggest = Blueprint('suggest', __name__, template_folder='templates')

@suggest.before_request
def tokenExpireCheck():
	try:
		if session['expires_in'] <= datetime.now():
			status = helper.refreshAccessToken()
			if status is not True:
				abort(redirect(url_for('authenticate.logout')))
	except:
		abort(redirect(url_for('authenticate.logout')))

@suggest.route('/suggestToFriend', methods=['POST'])
def suggestToFriend():
	if request.method == "POST":
		username = request.form.get('username')
		problemCode = request.form.get('problemCode')
		contestCode = request.form.get('contestCode')
		if None in [username, problemCode, contestCode]:
			jsonify({'message' : 'Something went wrong. Please try again later', 'status' : 'failure'})
		res = monDB.suggestions.find_one({
			'username' : username,
			'problemCode' : problemCode,
			'contestCode' : contestCode,
			'by': session['username'],
		})
		if(res != None):
			return jsonify({'message' : 'It seems you have already suggested this problem to ' + username, 'status' : 'failure'})
		monDB.suggestions.insert_one({
			'username' : username,
			'problemCode' : problemCode,
			'contestCode' : contestCode,
			'by': session['username'],
			'status' : "1"
		})
		return jsonify({'message' : 'Successfully suggested to ' + username, 'status' : 'success'})
	return jsonify({'message' : 'Something went wrong. Please try again later', 'status' : 'failure'})