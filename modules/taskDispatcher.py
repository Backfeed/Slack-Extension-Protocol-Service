#import SparkWorldEng.main as worldEng
import urllib2


def dispatch(uTaskid):
	# TBD: dispatch according to environment (DEV - call to world eng on localhost / Prod - add to SQS queue)
	# TBD: dispatch to queue: instead of direct calling and separate SparkWorldEng from app (to be its own application)
	#worldEng.onUserTaskCreation(utask.id)
	urllib2.urlopen("http://localhost:8080/proccessTask/"+str(uTaskid)).read()
	