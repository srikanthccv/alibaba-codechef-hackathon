from flask import Blueprint, render_template, abort, session, request, jsonify, url_for, redirect
from jinja2 import TemplateNotFound
from flaskConfiguration import monDB
from datetime import datetime, date, timedelta
import application.codechefAPI as helper
from flaskConfiguration import monDB

notifications_page = Blueprint('notifications_page', __name__, template_folder='templates')

@notifications_page.before_request
def tokenExpireCheck():
	try:
		if session['expires_in'] <= datetime.now():
			status = helper.refreshAccessToken()
			if status is not True:
				abort(redirect(url_for('authenticate.logout')))
	except:
		abort(redirect(url_for('authenticate.logout')))

@notifications_page.route('/notifications')
def userNotifications():
	if session.get('username') == None:
		return redirect(url_for('login'))
	notifications = monDB.suggestions.find({'username': session['username'], 'status' : "1"})
	try:
		return render_template('notifications.html', notifications=notifications)
	except TemplateNotFound:
		abort(404)

@notifications_page.route('/notifications/markasread', methods=['POST'])
def markAsRead():
	if session.get('username') == None:
		return jsonify({'status': 'failure', 'message': 'Something went wrong. Please try again later'})
	if request.method == "POST":
		problemCode = request.form.get('problemCode')
		contestCode = request.form.get('contestCode')
		if problemCode == None or contestCode == None:
			return jsonify({'status': 'failure', 'message': 'Something went wrong. Please try again later'})
		# update criteria
		criteria = {
			'username': session['username'],
			'problemCode': problemCode,
			'contestCode': contestCode,
			'status': '1'
		}
		# change status to '0'
		monDB.suggestions.update_one(criteria,
			{
				'$set': {
					'status': '0'
				}
			}
		)
		notifications_count = monDB.suggestions.find({'status': '1', 'username': session['username']}).count()
		session['notifications_count'] = notifications_count		
		return jsonify({'status': 'success', 'message': 'Marked as read successfully!'})
	else:
		return jsonify({'status': 'failure', 'message': 'Something went wrong. Please try again later'})