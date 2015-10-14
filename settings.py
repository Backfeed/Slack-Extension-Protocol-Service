import os
envType = os.getenv('ENV_TYPE', 'Local')
SLACK_SECRET = os.environ.get('SLACK_SECRET') or 'ff21d4660b41b7bee9fef7bb4bf19b79'
TOKEN_SECRET = os.environ.get('SECRET_KEY') or 'JWT Token Secret String'
DB_URI = ''
print 'envType is '+envType
# setting database according to different environment 
if envType == 'Local':
    DB_URI = 'sqlite:///./main.db'
if envType == 'Prod' :
    DB_URI = 'mysql+pymysql://backfeed:backfeed@aajwc79xamypg4.cb6pht5ogo4h.us-east-1.rds.amazonaws.com/'
if envType == 'Staging':
    DB_URI = 'mysql+pymysql://backfeed:backfeed@aa1g5dhpz9ey233.cb6pht5ogo4h.us-east-1.rds.amazonaws.com/'
if envType == 'Develop':
    DB_URI = 'mysql+pymysql://backfeed:backfeed@aadz7cmluktrd9.cb6pht5ogo4h.us-east-1.rds.amazonaws.com/'

print 'DB_URI is:'+DB_URI
