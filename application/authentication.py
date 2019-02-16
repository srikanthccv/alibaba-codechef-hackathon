from flask import  Flask, render_template, redirect, session, request, jsonify, url_for, Blueprint, abort
from flask_oauth import OAuth
from flaskConfiguration import client_id, client_secret, callback_uri
from jinja2 import TemplateNotFound
import requests
import simplejson as json
from datetime import datetime, date, timedelta


authenticate = Blueprint('authenticate', __name__, template_folder='templates')

oauth = OAuth()
codechef = oauth.remote_app('Codechef',
	base_url='https://api.codechef.com/',
	request_token_url=None,
	access_token_url='/oauth/token',
	authorize_url='/oauth/authorize',
	consumer_key= client_id,
	consumer_secret= client_secret,
	request_token_params={'response_type':'code', 'state':'d#xMsy3V6:c4`F]'}
)

@authenticate.route('/login')
def login():
	# avoid session kill after browser window close
	session.permanent = True
	if(session.get('access_token') != None):
		return redirect('/dashboard')
	return codechef.authorize(callback= callback_uri)

@authenticate.route('/logout')
def logout():
	session.clear()
	try:
		return render_template('home.html')
	except TemplateNotFound:
		abort(404)

@authenticate.route('/codechef_authorized')
def codechefAuthorized():
	session['authorization_code'] = request.args.get('code')
	getAccessTokem(request.args.get('code'))
	try:
		return redirect('/dashboard')
	except TemplateNotFound:
		abort(404)

def getAccessTokem(authorization_code):
	headers = {'content-Type': 'application/json'}
	payload = {
		"grant_type": "authorization_code",
		"code": authorization_code, 
		"client_id": client_id,
		"client_secret": client_secret,
		"redirect_uri": callback_uri
	}
	apiResponse = requests.post('https://api.codechef.com/oauth/token', payload, headers)
	apiResponse = json.loads(apiResponse.text)
	try:
		if apiResponse['status'] == 'OK':
			session['access_token'] = apiResponse['result']['data']['access_token']
			session['refresh_token'] = apiResponse['result']['data']['refresh_token']
			session['expires_in'] = datetime.now() + timedelta(0, 1500)
		print (session['expires_in'])
	except Exception as e: 
		print(e)
