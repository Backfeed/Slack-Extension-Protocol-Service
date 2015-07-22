from protocol_function import BidInfo,FIn,ProtocolFunctionV1
import classes as cls
import math
from operator import attrgetter

state = {}

def bf_Log(logger,messsage,level = 'info'):
	if(logger):
		logger.info(messsage)
	return 0


def getHighestEval(bids):
	maxValue = max(bids, key=attrgetter('contribution_value_after_bid')).contribution_value_after_bid
	return maxValue
	
	
def isBidderFirstBid(bids, current_bid):
	logger = state['logger']	
	bf_Log(logger,'\n\n *** isBidderFirstBid: ***:\n')
	for bid in bids:
		if bid.owner == current_bid.owner:
			bf_Log(logger,'is not  bidders first bid.')
			return False
	
	bf_Log(logger,'is  bidders first bid.')
	return True


def validateBid(bids, current_bid):
	logger = state['logger']	
	bf_Log(logger,'\n\n *** validateBid: ***:\n')
	
	Wi = 0;
	users = state['usersDict']
	current_bidder = users[current_bid.owner]
	rep = math.ceil(float(current_bid.reputation))

	#check how much reputation has been engaged by current_bidder,
	for bid in bids:
		if bid.owner == current_bidder.user_id:  
			Wi += int(bid.reputation)
	bf_Log(logger,'amount of reputation which  has been engaged by the current_bidder:'+str(Wi))
	
	#check if something has to be trimmed
	if int(current_bidder.org_reputation) - Wi < rep:
		if int(current_bidder.org_reputation) > Wi:
			current_bid.reputation = int(current_bidder.org_reputation) - Wi
			bf_Log(logger,"trimmed reputation to : "+str(current_bid.reputation))
			
		else:
			bf_Log(logger,"bidder has no more reputation to spare for current bid. exit.")
			return None;
	elif(not int(current_bidder.org_reputation)):
		bf_Log(logger,"bidder has no more reputation to spare for current bid. exit.")
		return None;		
		
	bf_Log(logger,"current_bid.stake = " + str(current_bid.stake) + " and current_bid.rep = " + str(current_bid.reputation))

	if float(current_bid.stake) > int(current_bid.reputation):
		bf_Log(logger,"bidder has put more stake than he has reputation - reducing stake to bidder's reputation.")
		current_bid.stake = current_bid.reputation

	bf_Log(logger, "bidder reputation: "+ str(current_bidder.org_reputation) + ", bidder total weight = " + str(Wi) + "Appending current bid reputation:" + str(current_bid.reputation))
	bf_Log(logger,'\n\n')

	return current_bid;

def debug_state(state):
	logger = state['logger']
	bf_Log(logger,'\n\n *** current state ***:\n')
	bf_Log(logger,'previous highest eval:'+str(state['highest_eval']))
	bf_Log(logger,'total system reputation:'+str(state['total_system_reputation']))	


def getCurrentState(contributionObject,session):
	usersDict = {}
	total_system_reputation = 0

	# get users:
	user_org = contributionObject.userOrganization
	userOrgObjects = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == user_org.organization_id).all()

	for userOrg in userOrgObjects:
		usersDict[userOrg.user_id] = userOrg
		total_system_reputation = total_system_reputation + userOrg.org_reputation

	state['highest_eval'] = 0 
	if(contributionObject.bids and len(contributionObject.bids)):
		state['highest_eval'] = getHighestEval(contributionObject.bids)

	state['total_system_reputation'] = total_system_reputation
	state['usersDict'] = usersDict
	debug_state(state)


def debug_bid(current_bid):
	logger = state['logger']
	bf_Log(logger,'\n\n *** processing bid - info: ***\n')
	bf_Log(logger,'stake (risk):'+str(current_bid.stake))
	bf_Log(logger,'reputation (weight):'+str(current_bid.reputation))	
	bf_Log(logger,'tokens (eval):'+str(current_bid.tokens))
	
def issueTokens(tokes_to_distribute,contributers,session):
	logger = state['logger']	
	# get collaborators:
	for contributer in contributers:
		user = state['usersDict'][contributer.contributer_id]		
		tokens_to_add = math.ceil( ( tokes_to_distribute * contributer.contributer_percentage ) / 100 ) 
		user.org_tokens += tokens_to_add
		user.org_reputation += tokens_to_add
		session.add(user)


def distribute_rep(bids_distribution, current_bid,session):
	logger = state['logger']
	users = state['usersDict']
	current_bidder = users[current_bid.owner]

	if(not current_bid.stake):
		bf_Log(logger,'stake is null --> stake is set to entire bid reputation:'+str(current_bid.reputation))
		current_bid.stake = current_bid.reputation

	#kill the stake of the current_bidder
	current_bidder.org_reputation -= math.ceil(float(current_bid.stake))
	session.add(current_bidder)	

	#reallocate reputation
	for ownerId in bids_distribution:
		user = users[int(ownerId)]
		bf_Log(logger,"\n\nrealocating reputation for bidder Id:" + str(ownerId))
		bf_Log(logger,"OLD REP === " + str(user.org_reputation))		
		user.org_reputation += bids_distribution[ownerId] 
		bf_Log(logger,"NEW REP === " + str(user.org_reputation))
		session.add(user)
				
def process_bid(current_bid,session,logger = None):
	state['logger'] = logger
	debug_bid(current_bid)
	
	# get contribution :
	contributionObject = session.query(cls.Contribution).filter(cls.Contribution.id == current_bid.contribution_id).first()
	
	# update current state:
	getCurrentState(contributionObject,session)
	
	# validate is First Bid:
	if(not isBidderFirstBid(contributionObject.bids, current_bid)):
		bf_Log(logger,'is Not bidders first bid - exiting (we currently dont allow several bids per contribution.)')
		return None
	
	# validate Bid:
	current_bid = validateBid(contributionObject.bids, current_bid)
	if(not current_bid):
		return None

	# add current bid to bids:
	bids = contributionObject.bids
	bids.append(current_bid);
	
	# prepare input Info for calc:
	bidsInfo = []
	for bid in bids:
		bidsInfo.append( BidInfo(bid.tokens,bid.reputation,bid.stake,bid.owner) )

	current_bid_info = bidsInfo[-1]

	fin = FIn(bidsInfo,current_bid_info,state['total_system_reputation'])
	f = ProtocolFunctionV1(logger)
	result = f.execute(fin)
	
	distribute_rep(result.rep_distributions, current_bid,session)
	current_eval = result.evaluation

	# process current eval:
	current_bid.contribution_value_after_bid = current_eval
	eval_delta = int(current_eval) - int(state['highest_eval'])
	if (eval_delta > 0):
		issueTokens(eval_delta, contributionObject.contributionContributers,session)

	# success: add current bid and commit DB session:
	session.add(current_bid)
	session.commit()
	return current_bid

