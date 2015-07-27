import classes as cls
from datetime import datetime

from sqlalchemy import orm
from sqlalchemy import create_engine
import model as model
from value_distributer import ValueDistributer 

DB_TEST_URI = 'sqlite:///./tester.db'
import json 

"""
Session = sessionmaker(autocommit=False,
                       autoflush=False,
                       bind=create_engine(DB_URI))
session = scoped_session(Session)
"""
import logging
import logging.config
from testData.data import contributers
from testData.data import bids

# Create an engine and create all the tables we need
engine = create_engine(DB_TEST_URI,echo=True)
model.metadata.bind = engine
model.metadata.create_all()
sm = orm.sessionmaker(bind=engine, autoflush=False, autocommit=False,expire_on_commit=True)
session = orm.scoped_session(sm)

params = {"loggingConfigFilename":"logging.conf","DB":"tester.db","schemaPKG":"testData/pkgSchema.json"}
logging.config.fileConfig(params["loggingConfigFilename"])

def loadData(params):
	log = logging.getLogger("loading")
	
	# load world pkg :
	log.info('loading Data Pkg:' )	
	schemaPath = params["schemaPKG"]
	loadPkgIntoDB(schemaPath)
	
	# load contribution:
	loadContributionIntoDB()
	
	

def getUser(id):
    user = session.query(cls.User).filter(cls.User.id == id).first()    
    return user	
	

def loadContributionIntoDB():
		
	contribution = cls.Contribution()
	
	# owner is currently hard coded to first user in DB	-
	contribution.owner = 1
	contribution.users_organizations_id = 1

	userObj = getUser(contribution.owner)        
	if not userObj:
		return False       
	for contributer in contributers:             
		contributionContributer = cls.ContributionContributer()
		contributionContributer.contributer_id = contributer['contributer_id']
		if contributionContributer.contributer_id == '':
			continue
		userObj = getUser(contributionContributer.contributer_id)        
		if not userObj:
			return False
		contributionContributer.contribution_id=contribution.id
		contributionContributer.contributer_percentage=contributer['contributer_percentage']
		contribution.contributionContributers.append(contributionContributer) 
	session.add(contribution)
	
	
	
	# now add dummy contribution just so the above is not contribution-0:
	contribution2 = cls.Contribution()
	
	# owner is currently hard coded to first user in DB	-
	contribution2.owner = 1
	contribution2.users_organizations_id = 1
	session.add(contribution2)
	
	session.commit()


def loadPkgIntoDB(schemaPath):
	log = logging.getLogger("loading")
	#session = database.getSession()
	
	
	pkgSchemaFile =   openFile(schemaPath) 
	schemaJson = json.load(pkgSchemaFile)
	# parse json for objClass and jsonObjects:
	for objConfigFilname in schemaJson['files']:
	
		log.info('loading file :'+objConfigFilname)

		# get Json:	
		objConfigPath = schemaPath.replace('pkgSchema.json',objConfigFilname)  # switch pkgSchema.json with objConfigFilname
	
		(className,jsonObjects) = parseClassJsonObjs(objConfigPath)
		
		log.info('loading Objects of class :'+className)
		
		classObj = eval('cls.'+className)
		itemsToAdd = []
		for jsonObj in jsonObjects:
			itemObj = classObj(jsonObj,session)
			itemsToAdd.append(itemObj)

		# write to db:
		for obj in itemsToAdd:
			session.add(obj)
		session.flush()
		session.commit()


def parseClassJsonObjs(objConfigPath):
	# get Json file:	
	objFile =   openFile(objConfigPath) 
	objJson = json.load(objFile)
	
	className = objJson['class']
	jsonObjects = objJson['objects']
	
	return (className,jsonObjects)


def openFile(filename):
	log = logging.getLogger("loading")

	try:
		file = open(filename)
	except Exception, msg:
		log.error('Error while opening file:' +str(msg))
		file = None

	return file




def simulateBids():
	logger = logging.getLogger("protocols")
	
	logger.info('\n\n****************** Tester: running bids: ******************\n\n')
	
	for bidData in bids:
		curent_bid = cls.Bid(bidData,session)
		vd = ValueDistributer(logger)
		vd.process_bid(curent_bid,session,logger)
		if(vd.error_occured):
			print vd.error_code


loadData(params)
simulateBids()


"""
contributionObject = session.query(cls.Contribution).filter(cls.Contribution.id == 1).first()

bid_dict = {"tokens":60,
   "reputation":40,
   "owner":3,
   "contribution_id":1,
	"stake":10,
	"time_created":datetime.now()
    }
curent_bid = cls.Bid(bid_dict,session)

logger = logging.getLogger("protocols")
vdp.initialize(session,logger)
vdp.process_bid(curent_bid)
"""