import math
from AbstractProtocolFunction import AbstractProtocolFunction
from FOut import FOut

class ProtocolFunctionV1(AbstractProtocolFunction):
	
	def __init__(self,logger = None):
		self.logger = logger

	def log(self,messsage,level = 'info'):
		if(self.logger):
			self.logger.info(messsage)
		return True

	def decay(self,vi, vn,similarEvaluationRate):
		
		#decay = math.atan(1 / abs(vi - vn+0.1))
		decay = math.atan(1/(pow(10,(int(similarEvaluationRate)/50))*abs(vi-vn)/(min(vi,vn)+0.00001)+0.0001))/1.57
		return decay
	
	def distribute_current_evaluation_rep(self,fIn,fout):
		current_evaluation = fIn.current_evaluation
		evaluations = fIn.evaluations
		summ = 0;	

		#calculate total sum of Weight * Decay
		for evaluation in evaluations:
			summ += evaluation.reputation * self.decay(evaluation.tokens, current_evaluation.tokens,fIn.similarEvaluationRate)
		
		#self.log("sum of Weight * Decay = " + str(summ))

		#reallocate reputation
		self.log("\n")
		self.log(" ---- total rep to be distributed  (current_evaluation.stake) === " + str(current_evaluation.stake))
		
		for evaluation in evaluations:
			current_decay = self.decay(evaluation.tokens, current_evaluation.tokens,fIn.similarEvaluationRate)
			new_rep_weight = ( evaluation.reputation * current_decay  ) / summ
			# bug fix: we round up and thus create reputation from thin air
			#evaluators_rep_distribution =  math.ceil(float(current_evaluation.stake) * new_rep_weight ) 
			evaluators_rep_distribution =  current_evaluation.stake * new_rep_weight 
			
			fout.rep_distributions[str(evaluation.agentId)] = evaluators_rep_distribution
			
			# debug:
			self.log("\n")
			self.log("calculating reputation distribution for evaluator :" + str(evaluation.agentId))
			self.log("evaluators evaluation: = " + str(evaluation.tokens) + ", current evaluation  = " + str(current_evaluation.tokens))
			self.log("calculated decay = " + str(current_decay))
			self.log('new reputation percentage :'+str(new_rep_weight))
			self.log("---- current evaluators reputation distribution === " + str(evaluators_rep_distribution))
		
		return True

	def calcCurrentEvaluation(self,fIn,fout):
		self.log("calculating current evaluation:")
		
		evaluations = fIn.evaluations
		
		# get reputation on zero (un-invested reputation)
		total_invested_rep = 0
		for evaluation in evaluations:
			total_invested_rep = total_invested_rep + evaluation.reputation

		uninvested_rep =  fIn.total_system_reputation - total_invested_rep

		# Sort by tokens : (To sort the list in place...)
		evaluations.sort(key=lambda x: x.tokens, reverse=False)
		#evaluations_sorted_by_tokens = sorted(evaluations, key=lambda evaluation: evaluation.tokens, reverse=False)

		# check if we passed 50% of total rep in system if so we hit the median:
		if( uninvested_rep > fIn.total_system_reputation/2 ):

			# we hit the median so update current evaluation with current evaluation:
			self.log("uninvested_rep is greater than median - evaluation is 0.")
			fout.evaluation = 0
			return True

		acumulated_rep = uninvested_rep	
		for evaluation in evaluations:
			acumulated_rep = acumulated_rep + evaluation.reputation

			# check if we passed 50% of total rep in system if so we hit the median:
			if( acumulated_rep > fIn.total_system_reputation/2 ):				
				# we hit the median so update current evaluation with current evaluation:
				current_evaluation = evaluation.tokens
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
		self.distribute_current_evaluation_rep(fin,fout)
		self.calcCurrentEvaluation(fin,fout)
		fout.debug(self.logger)				
		
		return fout

