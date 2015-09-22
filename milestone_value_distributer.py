from protocol_function import BidInfo,FIn,ProtocolFunctionV1
import classes as cls
from operator import attrgetter

class MileStoneValueDistributerBase(object):
	
	def process_bid(self,current_bid,session,logger = None):
		pass


class MileStoneValueDistributer(MileStoneValueDistributerBase):
	
	def __init__(self,logger = None):
		self.logger = logger
		self.error_occured = False
		self.error_code = None
		

	def log(self,messsage,level = 'info'):
		if(self.logger):
			self.logger.info(messsage)
		return True

	def getHighestEval(self,mileStoneBids):
		maxValue = max(mileStoneBids, key=attrgetter('milestone_value_after_bid')).milestone_value_after_bid
		return maxValue


	def isBidderFirstBid(self,mileStoneBids, current_bid):
		self.log('\n\n *** isBidderFirstBid: ***:\n')
		for bid in mileStoneBids:
			if bid.owner == current_bid.owner:
				self.log('is not  bidders first bid.')
				return False

		self.log('is  bidders first bid.')
		return True


	def validateBid(self,mileStoneBids, current_bid):
		self.log('\n\n *** validateBid: ***:\n')

		Wi = 0.0
		users = self.usersDict
		current_bidder = users[current_bid.owner]
		rep = current_bid.reputation
		print 'rep is'+str(rep)
		#check how much reputation has been engaged by current_bidder,
		for bid in mileStoneBids:
			print 'comes here in bids'
			if bid.owner == current_bidder.user_id:  
				Wi += bid.reputation
		self.log('amount of reputation which  has been engaged by the current_bidder:'+str(Wi))
		print 'Wi is'+str(Wi)
		print 'current_bidder.org_reputation is'+str(current_bidder.org_reputation)
		print 'diffrence is'+str(float(current_bidder.org_reputation) - float(Wi))
		print 'check is'+str(float(current_bidder.org_reputation) - float(Wi) < float(rep))
		#check if something has to be trimmed
		if float(current_bidder.org_reputation) - float(Wi) < float(rep):
			print 'comes here in check1'
			if float(current_bidder.org_reputation) > float(Wi):
				current_bid.reputation = float(current_bidder.org_reputation) - float(Wi)
				self.log("trimmed reputation to : "+str(current_bid.reputation))

			else:
				print 'comes here in check2'
				self.log("bidder has no more reputation to spare for current bid. exit.")
				return None;
		elif(not current_bidder.org_reputation):
			print 'comes here in check3'
			self.log("bidder has no more reputation to spare for current bid. exit.")
			return None;		

		self.log("current_bid.stake = " + str(current_bid.stake) + " and current_bid.rep = " + str(current_bid.reputation))				
		if float(current_bid.stake) > float(current_bid.reputation):
			self.log("bidder has put more stake than he has reputation - reducing stake to bidder's reputation.")
			current_bid.stake = current_bid.reputation

		self.log( "bidder reputation: "+ str(current_bidder.org_reputation) + ", bidder total weight = " + str(Wi) + "Appending current bid reputation:" + str(current_bid.reputation))
		self.log('\n\n')

		return current_bid;

	def debug_state(self):
		self.log('\n\n *** current state ***:\n')
		self.log('previous highest eval:'+str(self.highest_eval))
		self.log('total system reputation:'+str(self.total_system_reputation))	

	# get state : users Dict which is a dict of (key : value) userId:userOrgenization object  ,also calc total_system_reputation and highest_eval:
	def getCurrentState(self,milestoneObject,session):
		usersDict = {}
		total_system_reputation = 0

		# get users:
		user_org = milestoneObject.userOrganization
		org = user_org.organization
		userOrgObjects = session.query(cls.UserOrganization).filter(cls.UserOrganization.organization_id == user_org.organization_id).all()

		for userOrg in userOrgObjects:
			usersDict[userOrg.user_id] = userOrg
			total_system_reputation = total_system_reputation + userOrg.org_reputation

		self.highest_eval =  0 
		if(milestoneObject.milestoneBids and len(milestoneObject.milestoneBids)):
			self.highest_eval = self.getHighestEval(milestoneObject.milestoneBids)

		self.total_system_reputation = total_system_reputation
		self.a = org.a
		self.usersDict = usersDict
		self.debug_state()


	def debug_bid(self,current_bid):
		self.log('\n\n *** processing bid - info: ***\n')
		self.log('stake (risk):'+str(current_bid.stake))
		self.log('reputation (weight):'+str(current_bid.reputation))	
		self.log('tokens (eval):'+str(current_bid.tokens))

	def process_current_evaluation(self,current_eval,contributers,session,slackTeamId,organization):
		eval_delta = current_eval - self.highest_eval
		#hardcoding for Lazzoz for right now making it 90% T03K9TS1Q
		#if (slackTeamId == 'T02UHLXM9') :
		print 'before eval_delta is'+str(eval_delta)
		print 'slack team id'+str(slackTeamId)
		if (slackTeamId == 'T02UHLXM9') :
		#if (slackTeamId == 'T03K9TS1Q') :
			restData = float(eval_delta * 90/100)
			organization.reserveTokens = organization.reserveTokens + (float(eval_delta) - restData)
			session.add(organization)
			eval_delta = restData
			print 'after eval_delta is' + str(eval_delta)
		if (eval_delta > 0):
			# Issue tokens and reputation to collaborators:
			for contributer in contributers:
				user = self.usersDict[contributer.contributer_id]		
				tokens_to_add =  ( eval_delta * contributer.contributer_percentage ) / 100 	
				user.org_tokens += tokens_to_add
				user.org_reputation += tokens_to_add
				session.add(user)

	def distribute_rep(self,bids_distribution, current_bid,session):
		users = self.usersDict
		current_bidder = users[current_bid.owner]

		if(not current_bid.stake):
			self.log('stake is null --> stake is set to entire bid reputation:'+str(current_bid.reputation))
			current_bid.stake = current_bid.reputation

		#kill the stake of the current_bidder
		current_bidder.org_reputation = current_bidder.org_reputation - float(current_bid.stake)
		session.add(current_bidder)	

		#reallocate reputation
		for ownerId in bids_distribution:
			user = users[int(ownerId)]
			self.log("\n\nrealocating reputation for bidder Id:" + str(ownerId))
			self.log("OLD REP === " + str(user.org_reputation))		
			user.org_reputation += bids_distribution[ownerId] 
			self.log("NEW REP === " + str(user.org_reputation))
			session.add(user)


	def set_error(self,message):
		self.log('Error:'+message)
		self.error_occured = True
		self.error_code = message	

	def process_bid(self,current_bid,session,logger = None):
		print 'comes here 1'
		self.debug_bid(current_bid)
		
		# get current state data:
		mileStoneObject = session.query(cls.MileStone).filter(cls.MileStone.id == current_bid.milestone_id).first()
		#orgObject = session.query(cls.Organization).filter(cls.Organization.id == cls.UserOrganization.organization_id).filter(cls.UserOrganization.id == cls.Contribution.users_organizations_id).first()
		self.getCurrentState(mileStoneObject,session)

		# validate is First Bid:
		if(not self.isBidderFirstBid(mileStoneObject.milestoneBids, current_bid)):
			self.set_error('is Not bidders first bid, (we currently do not allow several bids per milestone.)')
			return None

		# validate Bid:
		current_bid = self.validateBid(mileStoneObject.milestoneBids, current_bid)
		current_bid.weight = (float(current_bid.reputation)/float(self.total_system_reputation))*100
		if(not current_bid):
			self.set_error('bid not valid.')
			return None

		# add current bid to bids:
		bids = mileStoneObject.milestoneBids
		bids.append(current_bid);

		# prepare protocol function Input:
		bidsInfo = []
		for bid in bids:
			bidsInfo.append( BidInfo(bid.tokens,bid.reputation,bid.stake,bid.owner) )

		current_bid_info = bidsInfo[-1]
		fin = FIn(bidsInfo,current_bid_info,self.total_system_reputation,self.a)

		# protocol function calc:
		f = ProtocolFunctionV1(logger)
		result = f.execute(fin)
		if(result.error_occured):
			self.set_error(result.error_code)
			return None
		
		# success: handle result:	
		self.distribute_rep(result.rep_distributions, current_bid,session)
		self.process_current_evaluation(result.evaluation, mileStoneObject.milestoneContributers,session,mileStoneObject.userOrganization.organization.slack_teamid,mileStoneObject.userOrganization.organization)

		# add current bid and commit DB session:
		current_bid.milestone_value_after_bid = result.evaluation
		session.add(current_bid)
		session.commit()
		return current_bid

