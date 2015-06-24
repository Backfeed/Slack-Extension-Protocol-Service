#DB_URI = 'sqlite:///./main.db'
DB_URI = 'mysql+pymysql://backfeed:backfeed@aajwc79xamypg4.cb6pht5ogo4h.us-east-1.rds.amazonaws.com/'
import os
basePath  = os.path.dirname(os.path.abspath(__file__))
testPath = '/../SparkWorldEng/Tester/spark_tester.db'
path = basePath+testPath
#DB_URI = 'sqlite:///modules/SparkWorldEng/Tester/spark_tester.db'
print 'the path:'+path
#DB_URI = 'sqlite:///' + path