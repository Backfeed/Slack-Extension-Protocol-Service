#import logging.config
#logging.config.fileConfig(params["loggingConfigFilename"])
from db import session
import classes as cls





def functionX(E_R_tuple):
	V = E_R_tuple[0][0]
	vector_R = None
	vector_R = [ str(int(r)+1) for (e,r) in E_R_tuple]
    
	return (V,vector_R)







class Action(object):
	
	def __init__(self,logger):
		#self._logger = logger;
		pass

	def execute(self,state):			
		pass # TBD: raise exception, inorder for this class to be pure abstract
		
	

class ProcessContribution(Action):

	def __init__(self,logger):
		Action.__init__(self,logger)

	def execute(self,state):
		#log = logging.getLogger(self._logger)
		contribution = state['contribution']
		print 'ProcessContribution: bids:'+str(len(contribution.bids))
		
		#self.getData(state)
		
		

		return state
		
	def getData(self,state):
		
		# get bids:
		bids = session.query(cls.Bid).filter(cls.Bid.contribution_id == state['contribution_id']).all()
		
		for bid in bids:
			print bid	