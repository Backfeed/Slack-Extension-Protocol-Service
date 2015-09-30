import math

class BidInfo(object):
	def __init__(self, tokens,reputation,stake,owner,contributionsSize):
		self.tokens = float(tokens)
		self.reputation = float(reputation)
		self.stake = float(stake)	
		self.owner = owner	
		self.contributionsSize = contributionsSize

	def debug(self,logger):
		if(logger):
			logger.info('tokens: '+str(self.tokens))
			logger.info('reputation: '+str(self.reputation))
			logger.info('stake: '+str(self.stake))
			logger.info('owner: '+str(self.owner))
			

class FIn(object):
	def __init__(self, bids,current_bid,total_rep,a,contributionsSize):
		self.bids = bids
		self.current_bid = current_bid
		self.total_system_reputation = total_rep
		self.a = a
		self.contributionsSize = contributionsSize
		
	def isValid(self):
		if (not self.bids or
			not self.total_system_reputation or
			not self) and (self.contributionsSize > 1):
			return False
		return True
		
	def debug(self,logger):
		if(logger):
			logger.info('\n')
			
			logger.info('F input:')
			"""
			logger.info('bids:')
			for bid in self.bids:
				bid.debug(logger)
			"""
			logger.info('current bid: ')
			self.current_bid.debug(logger)
			logger.info('total system reputation: '+str(self.total_system_reputation))
			
		return True

class FOut(object):
	def __init__(self):
		self.evaluation = None
		self.rep_distributions = {}
		self.error_occured = False
		self.error_code = None
		
	def debug(self,logger):
		if(logger):
			logger.info('\n')
			
			logger.info('F output:')
			logger.info('---- reputation distribution between owners:'+str(self.rep_distributions))
			logger.info('---- current evaluation: '+str(self.evaluation))

		return True
		
class AbstractProtocolFunction(object):
	
	def execute(self,fIn):
		pass


class ProtocolFunctionV1(AbstractProtocolFunction):
	
	def __init__(self,logger = None):
		self.logger = logger

	def log(self,messsage,level = 'info'):
		if(self.logger):
			self.logger.info(messsage)
		return True

	def decay(self,vi, vn,a):
		
		#decay = math.atan(1 / abs(vi - vn+0.1))
		decay = math.atan(1/(pow(10,(int(a)/50))*abs(vi-vn)/(min(vi,vn)+0.00001)+0.0001))/1.57
		return decay
	
	def distribute_current_bid_rep(self,fIn,fout):
		current_bid = fIn.current_bid
		bids = fIn.bids
		summ = 0;	

		#calculate total sum of Weight * Decay
		for bid in bids:
			summ += bid.reputation * self.decay(bid.tokens, current_bid.tokens,fIn.a)
		
		#self.log("sum of Weight * Decay = " + str(summ))

		#reallocate reputation
		self.log("\n")
		self.log(" ---- total rep to be distributed  (current_bid.stake) === " + str(current_bid.stake))
		
		for bid in bids:
			current_decay = self.decay(bid.tokens, current_bid.tokens,fIn.a)
			if fIn.contributionsSize > 1 :
				new_rep_weight = ( bid.reputation * current_decay  ) / summ
			else:
				new_rep_weight = 0
			# bug fix: we round up and thus create reputation from thin air
			#bidders_rep_distribution =  math.ceil(float(current_bid.stake) * new_rep_weight ) 
			bidders_rep_distribution =  current_bid.stake * new_rep_weight 
			
			fout.rep_distributions[str(bid.owner)] = bidders_rep_distribution
			
			# debug:
			self.log("\n")
			self.log("calculating reputation distibution for bidder :" + str(bid.owner))
			self.log("bidders evaluation: = " + str(bid.tokens) + ", current bid  = " + str(current_bid.tokens))
			self.log("calculated decay = " + str(current_decay))
			self.log('new reputation percentage :'+str(new_rep_weight))
			self.log("---- current bidders reputation distribution === " + str(bidders_rep_distribution))
		
		return True

	def calcCurrentEvaluation(self,fIn,fout):
		self.log("calculating current evaluation:")
		
		bids = fIn.bids
		
		if fIn.contributionsSize == 1 :
			for bid in bids:
				current_evaluation = bid.tokens
				fout.evaluation = current_evaluation
				return True
		
		
		
		# get reputation on zero (un-invested reputation)
		total_invested_rep = 0
		for bid in bids:
			total_invested_rep = total_invested_rep + bid.reputation

		uninvested_rep =  fIn.total_system_reputation - total_invested_rep

		# Sort by tokens : (To sort the list in place...)
		bids.sort(key=lambda x: x.tokens, reverse=False)
		#bids_sorted_by_tokens = sorted(bids, key=lambda bid: bid.tokens, reverse=False)

		# check if we passed 50% of total rep in system if so we hit the median:
		if( uninvested_rep > fIn.total_system_reputation/2 ):

			# we hit the median so update current bid with current evaluation:
			self.log("uninvested_rep is greater than median - evaluation is 0.")
			fout.evaluation = 0
			return True

		acumulated_rep = uninvested_rep	
		for bid in bids:
			acumulated_rep = acumulated_rep + bid.reputation

			# check if we passed 50% of total rep in system if so we hit the median:
			if( acumulated_rep > fIn.total_system_reputation/2 ):				
				# we hit the median so update current bid with current evaluation:
				current_evaluation = bid.tokens
				fout.evaluation = current_evaluation
				self.log("acumulated_rep is greater than median - evaluation is :"+str(fout.evaluation))
				
				return True

		fout.evaluation = None
		fout.error_occured = True
		fout.error_code = "current evaluation - calculation error."
		return True

	def execute(self,fin):
		
		fout = FOut()
		if (not fin.isValid()):
			fout.error_occured = True
			fout.error_code = "input invalid."
			return fout
		
		fin.debug(self.logger)				
		self.distribute_current_bid_rep(fin,fout)
		self.calcCurrentEvaluation(fin,fout)
		fout.debug(self.logger)				
		
		return fout

