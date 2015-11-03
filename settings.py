import os
TOKEN_SECRET = os.environ.get('SECRET_KEY') or 'JWT Token Secret String'
envType = os.getenv('ENV_TYPE', 'Local')
DB_URI = ''
print 'envType is '+envType
# setting database according to different environment 
if envType == 'Local':
    DB_URI = 'sqlite:///./main.db'
if envType == 'Staging' :
    DB_URI = 'mysql+pymysql://backfeed:backfeed@aa1g5dhpz9ey233.cb6pht5ogo4h.us-east-1.rds.amazonaws.com/'

print 'DB_URI is:'+DB_URI
