import json as JSON

class BaseObject(object):

	def __init__(self,json ,session):
		self.parseJSON(json,session)

	def parseJSON(self,json,session ):
		#session = db.getSession()
		myAttributes = [a for a in dir(self) if not a.startswith('__') and not callable(getattr(self,a)) and not a.startswith('_') and not a == ('id')]
		for key in json :
			value = json[key]	
			#check if value is a dict
			if type(value) is dict:
				# value is a complex object
				valueClass = value['class']
				
				if  value['reference'] == 'False':
					# we create new objects to connect to self.key
					valueClass = value['class']
					valueList = []
				    # value is iterable
					for jsonObj in value['objects']:
						valueList.append(eval(valueClass)(jsonObj,session))
			
					setattr(self, key,valueList)
				
				elif (value['reference'] == 'True'):
					# we query for  existing objects to connect to self.key
					filterStr = value['filter']
					
					#giantBats = session.query(cls.Monster).filter(cls.Monster.race.like("Giant%")).all()
					queryObjects = eval('session.query('+valueClass+').filter('+ filterStr+ ').all()')
					for obj in queryObjects:
						eval('self.'+key).append(obj)
				else :
					pass #TBD: raise error - reference value ...
					
			else:
				# value is a simple field value
				
				# TBD: if needed - raise no attribute error ...
				setattr(self, key,value)

	def __str__(self):
		
		myAttributes = [a for a in dir(self) if not a.startswith('__') and not callable(getattr(self,a)) and not a.startswith('_') and not a == ('id')]		
		string = self.__class__.__name__ + ':'
		for key in myAttributes :
			myAtribute = getattr(self, key)
			string = string + '\n'+ key+':'+str(myAtribute)
		return string

	def __repr__(self):
		return self.__str__()		

	
class User(BaseObject):
	pass

class Bid(BaseObject):
	pass

class Contribution(object):
	pass

class Organization(object):
	pass

class UserOrganization(object):
	pass

class ContributionContributer(object):
	pass

class Contributer(object):
     def __init__(self, contributerId, contributerPercentage):
        self.obj1 = contributerId
        self.obj2 = contributerPercentage
       
class IntialBid(object):
    def __init__(self, tokens, reputation):
        self.obj1 = tokens
        self.obj2 = reputation        
		
# checkout serlizing : http://www.diveintopython3.net/serializing.html