from flask import Blueprint, render_template, abort, session, request, jsonify, url_for, redirect
from jinja2 import TemplateNotFound
from flaskConfiguration import monDB
from datetime import datetime, date, timedelta
import application.user as user
import application.codechefAPI as helper

dashboard_page = Blueprint('dashboard_page', __name__, template_folder='templates')

@dashboard_page.before_request
def tokeExpiryCheck():
	try:
		if session['expires_in'] <= datetime.now():
			status = helper.refreshAccessToken()
			if status is not True:
				abort(redirect(url_for('authenticate.logout')))
	except:
		abort(redirect(url_for('authenticate.logout')))

@dashboard_page.route('/')
def index():
	if(session.get('access_token') != None):
		return redirect(url_for('dashboard_page.dashboard'))
	return render_template('home.html')

@dashboard_page.route('/dashboard')
def dashboard():
	if(session.get('access_token') == None):
		return redirect('/login')
	user.setUserDetails(session['access_token'])
	notifications_count = monDB.suggestions.find({'status': '1', 'username': session['username']}).count()
	session['notifications_count'] = notifications_count
	return render_template('dashboard.html')