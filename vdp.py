#import logging.config
#logging.config.fileConfig(params["loggingConfigFilename"])
from db import session
import classes as cls

import math
from operator import attrgetter

state = {}


def init():
	usersDict = {}
	total_system_reputation = 0
	
	# get users:
	userObjects = session.query(cls.User).all()
	for user in userObjects:
		usersDict[user.id] = user
		total_system_reputation = total_system_reputation + user.reputation
	
	state['total_system_reputation'] = total_system_reputation
	state['usersDict'] = usersDict
	

def getHighestEval(bids):
	maxValue = max(bids, key=attrgetter('contribution_value_after_bid')).contribution_value_after_bid
	return maxValue
	
def issueTokens(tokes_to_distribute,contributers):
	
	# get collaborators:
	for contributer in contributers:
		user = state['usersDict'][contributer.contributer_id]		
		tokens_to_add = math.ceil( ( tokes_to_distribute * contributer.contributer_percentage ) / 100 ) 
		user.tokens += tokens_to_add
		user.reputation += tokens_to_add
		session.add(user)
		
def calcValue(bids):
	
	# get reputation on zero (un-invested reputation)
	total_invested_rep = 0
	for bid in bids:
		total_invested_rep = total_invested_rep + bid.reputation
	
	uninvested_rep =  state['total_system_reputation'] - total_invested_rep
	
	# Sort by tokens : (To sort the list in place...)
	bids.sort(key=lambda x: x.tokens, reverse=False)
	#bids_sorted_by_tokens = sorted(bids, key=lambda bid: bid.tokens, reverse=False)
		
	# check if we passed 50% of total rep in system if so we hit the median:
	if( uninvested_rep > math.ceil(state['total_system_reputation']/2) ):
		
		# we hit the median so update current bid with current evaluation:
		return 0
	
	acumulated_rep = uninvested_rep	
	for bid in bids:
		acumulated_rep = acumulated_rep + bid.reputation
		
		# check if we passed 50% of total rep in system if so we hit the median:
		if( acumulated_rep > math.ceil(state['total_system_reputation']/2) ):
			
			# we hit the median so update current bid with current evaluation:
			current_evaluation = bid.tokens
			return current_evaluation

	return 0

	
def add_to_bids(bids, current_bid):
	Wi = 0;
	users = state['usersDict']
	current_bidder = users[current_bid.owner]
	rep = current_bid.reputation;

	#check how much reputation has been engaged by current_bidder,
	for bid in bids:
		if bid.owner == current_bidder.id:  
			Wi += bid.reputation
	#check if something has to be trimmed
	print "*******" + str(Wi);
	if current_bidder.reputation - Wi < rep:
		if current_bidder.reputation > Wi:
			current_bid.reputation = current_bidder.reputation - Wi
		else:
			return None;

	print "current_bid.stake = " + str(current_bid.stake) + "and current_bid.rep = " + str(current_bid.reputation)

	if current_bid.stake > current_bid.reputation:
		print "!@#!@#!@#!@#!@#!@#!@#!@#!#!@#!@#!@#"
		current_bid.stake = current_bid.reputation

	print "User reputation: "+ str(current_bidder.reputation) + "& Wi = " + str(Wi) + "Appending:" + str(current_bid.reputation)
	bids.append(current_bid);
	
	return bids;



def distribute_rep(bids, current_bid):

	users = state['usersDict']
	current_bidder = users[current_bid.owner]

	stake = current_bid.stake
	if(not stake):
		stake = current_bid.reputation

	#kill the stake of the current_bidder
	current_bidder.reputation -= stake
	session.add(current_bidder)

	# and redistribute it around to the others
	update_rep(bids, current_bid)



def update_rep(bids, current_bid):
	summ = 0;	
	users = state['usersDict']	

	#calculate total sum of Weight * Decay
	for bid in bids:
		summ += bid.reputation * decay(bid.tokens, current_bid.tokens)
	print "summmm = " + str(summ)

	#reallocate reputation
	for bid in bids:
		user = users[bid.owner]
		print "OLD REP === " + str(user.reputation)
		print " ----  current_bid.stake = " + str(current_bid.stake)
		user.reputation += math.ceil(current_bid.stake * ( bid.reputation * decay(bid.tokens, current_bid.tokens)  ) / summ) 
		print "NEW REP === " + str(user.reputation)
		session.add(user)


def decay(vi, vn):
	print "v1 = " + str(vi) + "vn = " + str(vn)
	decay = math.atan(1 / abs(int(vi) - int(vn)+0.1))
	print "decay................." + str(decay)
	return decay


def process_bid(current_bid):
	
	print 'processing bid:'+str(current_bid)
	
	init()

	contributionObject = session.query(cls.Contribution).filter(cls.Contribution.id == current_bid.contribution_id).first()
	highest_eval = 0 
	if(contributionObject.bids and len(contributionObject.bids)):
		highest_eval = getHighestEval(contributionObject.bids)
	
	#contributionObject.bids.append(current_bid)
	#bids = contributionObject.bids
	bids = add_to_bids(contributionObject.bids, current_bid)
	if(not bids):
		return False

	distribute_rep(bids, current_bid)

	current_eval = calcValue(bids)

	# process current eval:
	eval_delta = int(current_eval) - int(highest_eval)
	if (eval_delta > 0):
		issueTokens(eval_delta, contributionObject.contributionContributers)

	current_bid.contribution_value_after_bid = current_eval
	session.add(current_bid)

	# success: commit DB session:
	session.commit()
	return current_bid

