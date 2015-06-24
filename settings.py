import os
envType = os.getenv('ENV_TYPE', 'Local')
DB_URI = ''
print 'envType is'+envType
if(envType == 'Local'):
    DB_URI = 'sqlite:///./main.db'
if(envType == 'Prod'):
    DB_URI = 'mysql+pymysql://backfeed:backfeed@aajwc79xamypg4.cb6pht5ogo4h.us-east-1.rds.amazonaws.com/'
if(envType == 'Stage'):
    DB_URI = 'mysql+pymysql://backfeed:backfeed@aa1g5dhpz9ey233.cb6pht5ogo4h.us-east-1.rds.amazonaws.com/'   

#DB_URI = 'sqlite:///modules/SparkWorldEng/Tester/spark_tester.db'
print 'DB_URI is:'+DB_URI
#DB_URI = 'sqlite:///' + path