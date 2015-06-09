#import logging.config
#logging.config.fileConfig(params["loggingConfigFilename"])
from db import session
import classes as cls

def process_bid(current_bid):
    print 'processing bid:'+str(current_bid)
    contributionObject = session.query(cls.Contribution).filter(cls.Contribution.id == current_bid.contribution_id).first()
    
    # prepare (E,R)
    E_R_tuple = [ (bid.tokens,bid.reputation) for bid in contributionObject.bids]
    E_R_tuple.append((current_bid.tokens,current_bid.reputation))
    (V,Vr) = functionX(E_R_tuple)

    # update 'current_rep_to_return' on bids:
    i = 0
    for prev_bid in contributionObject.bids:    
        prev_bid.current_rep_to_return = Vr[i]
        session.add(prev_bid)
        i = i+1

    # update 'contribution_value_after_bid' on current bid:
    current_bid.current_rep_to_return = Vr[i]
    current_bid.contribution_value_after_bid = V
    return current_bid



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