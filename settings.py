DB_URI = 'sqlite:///./main.db'
import os
basePath  = os.path.dirname(os.path.abspath(__file__))
testPath = '/../SparkWorldEng/Tester/spark_tester.db'
path = basePath+testPath
#DB_URI = 'sqlite:///modules/SparkWorldEng/Tester/spark_tester.db'
print 'the path:'+path
#DB_URI = 'sqlite:///' + path