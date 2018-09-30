from flask import  Flask, render_template, redirect, session, request, jsonify, url_for, Blueprint, abort
from flask_oauth import OAuth
import time
from datetime import datetime, date, timedelta
import requests
import simplejson as json
from bson.objectid import ObjectId
import sys
from application.notifications import notifications_page
from application.statistics import statistics_page
from application.suggest import suggest
from application.activetime import activetime
from application.authentication import authenticate
from application.dashboard import dashboard_page
from application.profile import profile_page
from application.api import api
import application.user as user
from pymongo import MongoClient
from pprint import pprint #to proper proper data

monClient = MongoClient('mongodb://root:Du88qrb1W8U0@incredibles2.mongodb.ap-south-1.rds.aliyuncs.com:3717/admin')
monDB = monClient.admin

app = Flask(__name__, template_folder='./templates')
app.register_blueprint(notifications_page)
app.register_blueprint(statistics_page)
app.register_blueprint(profile_page)
app.register_blueprint(dashboard_page)
app.register_blueprint(suggest)
app.register_blueprint(activetime)
app.register_blueprint(authenticate)
app.register_blueprint(api)

app.secret_key = 'JacKKcaJ'
app.permanent_session_lifetime = timedelta(days=365)

def page_not_found(e):
	return render_template('404.html'), 404

def page_internal_error(e):
	return render_template('500.html'), 500

app.register_error_handler(404, page_not_found)
app.register_error_handler(500, page_internal_error)

if __name__ == '__main__':
	if len(sys.argv) > 1 and sys.argv[1] == 'alibaba':
		app.run(host = '0.0.0.0',port=80)
	else:
		app.run(host = '127.0.0.1', debug=True)