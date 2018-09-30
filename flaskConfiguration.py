from pymongo import MongoClient

client_id = 'XXXXXXXXXXXXXXXXXXX'
client_secret = 'XXXXXXXXXXXXXXXXXXX'
callback_uri = 'http://incredibles2.ddns.net/codechef_authorized'

codechefDateFormat = '%Y-%m-%d %H:%M:%S'

monClient = MongoClient('mongodb://root:XXXXXXXXXXXXXXXXXXX@incredibles2.mongodb.ap-south-1.rds.aliyuncs.com:3717/admin')
monDB = monClient.admin