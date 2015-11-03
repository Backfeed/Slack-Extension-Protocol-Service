from protocol_function import ProtocolFunctionV1
import classes as cls
from operator import attrgetter
from EvaluationInfo import EvaluationInfo
from FIn import FIn

class ValueDistributerBase(object):
	
	def process_evaluation(self,current_evaluation,session,logger = None):
		pass


class ValueDistributer(ValueDistributerBase):
	
	def __init__(self,protocolName,logger = None):
		self.logger = logger
		self.error_occured = False
		self.error_code = None
		self.protocolName = protocolName
		

	def log(self,messsage,level = 'info'):
		if(self.logger):
			self.logger.info(messsage)
		return True

	def getHighestEval(self,evaluations):
		maxValue = max(evaluations, key=attrgetter('contributionValueAfterEvaluation')).contributionValueAfterEvaluation
		return maxValue


	def isEvaluatarFirstEvaluation(self,evaluations, current_evaluation):
		self.log('\n\n *** isEvaluatarFirstEvaluation: ***:\n')
		for evaluation in evaluations:
			if int(evaluation.agentHandleId) == int(current_evaluation.agentHandleId):
				self.log('is not  evaluators first evaluation.')
				return False

		self.log('is  evaluators first evaluation.')
		return True


	def validateEvaluation(self,evaluations, current_evaluation):
		self.log('\n\n *** validateEvaluation: ***:\n')

		Wi = 0.0
		agents = self.agentsDict
		current_evaluator = agents[int(current_evaluation.agentHandleId)]
		rep = current_evaluation.reputation
		print 'rep is'+str(rep)
		#check how much reputation has been engaged by current_evaluator,
		for evaluation in evaluations:
			print 'comes here in evaluations'
			if evaluation.agentHandleId == current_evaluator.agentHandleId:  
				Wi += evaluation.reputation
		self.log('amount of reputation which  has been engaged by the current_evaluator:'+str(Wi))
		print 'Wi is'+str(Wi)
		print 'current_evaluator.reputation is'+str(current_evaluator.reputation)
		print 'diffrence is'+str(float(current_evaluator.reputation) - float(Wi))
		print 'check is'+str(float(current_evaluator.reputation) - float(Wi) < float(rep))
		#check if something has to be trimmed
		if float(current_evaluator.reputation) - float(Wi) < float(rep):
			print 'comes here in check1'
			if float(current_evaluator.reputation) > float(Wi):
				current_evaluation.reputation = float(current_evaluator.reputation) - float(Wi)
				self.log("trimmed reputation to : "+str(current_evaluation.reputation))

			else:
				print 'comes here in check2'
				self.log("evaluator has no more reputation to spare for current evaluation. exit.")
				return None;
		elif(not current_evaluator.reputation):
			print 'comes here in check3'
			self.log("evaluator has no more reputation to spare for current evaluations. exit.")
			return None;		

		self.log("current_evaluation.stake = " + str(current_evaluation.stake) + " and current_evaluation.rep = " + str(current_evaluation.reputation))				
		if float(current_evaluation.stake) > float(current_evaluation.reputation):
			self.log("evaluator has put more stake than he has reputation - reducing stake to evaluator's reputation.")
			current_evaluation.stake = current_evaluation.reputation

		self.log( "evaluator reputation: "+ str(current_evaluator.reputation) + ", evaluator total weight = " + str(Wi) + "Appending current evaluation reputation:" + str(current_evaluation.reputation))
		self.log('\n\n')

		return current_evaluation;

	def debug_state(self):
		self.log('\n\n *** current state ***:\n')
		self.log('previous highest eval:'+str(self.highest_eval))
		self.log('total system reputation:'+str(self.total_system_reputation))	

	# get state : agents Dict which is a dict of (key : value) agentHandleId:agentOrgenization object  ,also calc total_system_reputation and highest_eval:
	def getCurrentState(self,contribution,session):
		agentsDict = {}
		contributionValuesDict = {}
		total_system_reputation = 0

		# get agents:
		agent_collaboration = contribution.agentCollaboration
		collaboration = agent_collaboration.collaboration
		agentCollaborations = session.query(cls.AgentCollaboration).filter(cls.AgentCollaboration.collaborationId == agent_collaboration.collaborationId).all()
		contributionValues = session.query(cls.ContributionValue).filter(cls.ContributionValue.contributionId == contribution.id).all()
		for agentCollaboration in agentCollaborations:
			agentsDict[agentCollaboration.agentHandleId] = agentCollaboration
		 
		for contributionValue in contributionValues:
			total_system_reputation = total_system_reputation + contributionValue.reputation
			contributionValuesDict[contributionValue.agentCollaborationId] = contributionValue
		
		self.highest_eval =  0 
		if(contribution.evaluations and len(contribution.evaluations)):
			self.highest_eval = self.getHighestEval(contribution.evaluations)

		self.total_system_reputation = total_system_reputation
		self.similarEvaluationRate = collaboration.similarEvaluationRate
		self.passingResponsibilityRate = collaboration.passingResponsibilityRate
		self.agentsDict = agentsDict
		self.contributionValuesDict = contributionValuesDict
		self.debug_state()


	def debug_evaluation(self,current_evaluation):
		self.log('\n\n *** processing evaluation - info: ***\n')
		self.log('stake (risk):'+str(current_evaluation.stake))
		self.log('reputation (weight):'+str(current_evaluation.reputation))	
		self.log('tokens (eval):'+str(current_evaluation.tokens))

	def process_current_evaluation(self,current_eval,contributors,session,organization):
		eval_delta = current_eval - self.highest_eval
		contributionValues = self.contributionValuesDict
		print 'before eval_delta is'+str(eval_delta)
		if (eval_delta > 0):
			# Issue tokens and reputation to collaborators:
			for contributor in contributors:
				agent = self.agentsDict[contributor.contributorId]		
				tokens_to_add =  ( float(eval_delta) * float(contributor.percentage) ) / 100 	
				agent.tokens += tokens_to_add
				agent.reputation += tokens_to_add
				contributionValues[agent.id].reputationGain = contributionValues[agent.id].reputationGain + tokens_to_add
				session.add(agent)
				session.add(contributionValues[agent.id])

	def distribute_rep(self,evaluations_distribution, current_evaluation,session):
		agents = self.agentsDict
		current_evaluator = agents[int(current_evaluation.agentHandleId)]
		contributionValues = self.contributionValuesDict

		if(not current_evaluation.stake):
			self.log('stake is null --> stake is set to entire evaluation reputation:'+str(current_evaluation.reputation))
			current_evaluation.stake = current_evaluation.reputation

		#kill the stake of the current_evaluator
		
		current_evaluator.reputation = current_evaluator.reputation - float(current_evaluation.stake)
		contributionValues[current_evaluator.id].reputationGain= contributionValues[current_evaluator.id].reputationGain  - float(current_evaluation.stake)
		session.add(current_evaluator)	
		session.add(contributionValues[current_evaluator.id])
		#reallocate reputation
		for agentHandleId in evaluations_distribution:
			agent = agents[int(agentHandleId)]
			self.log("\n\nrealocating reputation for evaluator Id:" + str(agentHandleId))
			self.log("OLD REP === " + str(agent.reputation))		
			agent.reputation += evaluations_distribution[agentHandleId] 
			contributionValues[agent.id].reputationGain= contributionValues[agent.id].reputationGain  + evaluations_distribution[agentHandleId]
			self.log("NEW REP === " + str(agent.reputation))
			session.add(agent)
			session.add(contributionValues[agent.id])

	def set_error(self,message):
		self.log('Error:'+message)
		self.error_occured = True
		self.error_code = message	

	def process_evaluation(self,current_evaluation,session,logger = None):
		self.debug_evaluation(current_evaluation)
		
		# get current state data:
		contribution = session.query(cls.Contribution).filter(cls.Contribution.id == current_evaluation.contributionId).first()
		#orgObject = session.query(cls.Organization).filter(cls.Organization.id == cls.AgentOrganization.organization_id).filter(cls.AgentOrganization.id == cls.Contribution.agents_organizations_id).first()
		self.getCurrentState(contribution,session)

		# validate is First Evaluation:
		if(not self.isEvaluatarFirstEvaluation(contribution.evaluations, current_evaluation)):
			self.set_error('is Not evaluators first evaluation, (we currently do not allow several evaluations per contribution.)')
			return None

		# validate Evaluation:
		current_evaluation = self.validateEvaluation(contribution.evaluations, current_evaluation)
		
		if(not current_evaluation):
			self.set_error('evaluation not valid.')
			return None

		# add current_evaluation evaluation to evaluations:
		evaluations = contribution.evaluations
		evaluations.append(current_evaluation);

		# prepare protocol function Input:
		evaluationsInfo = []
		for evaluation in evaluations:
			evaluationsInfo.append( EvaluationInfo(evaluation.tokens,evaluation.reputation,evaluation.stake,evaluation.agentHandleId) )

		current_evaluation_info = evaluationsInfo[-1]
		fin = FIn(evaluationsInfo,current_evaluation_info,self.total_system_reputation,self.similarEvaluationRate)

		# protocol function calc:
		f = ProtocolFunctionV1(logger)
		result = f.execute(fin)
		if(result.error_occured):
			self.set_error(result.error_code)
			return None
		
		# success: handle result:	
		self.distribute_rep(result.rep_distributions, current_evaluation,session)
		self.process_current_evaluation(result.evaluation, contribution.contributors,session,contribution.agentCollaboration.collaboration)

		# add current evaluation and commit DB session:
		current_evaluation.contributionValueAfterEvaluation = result.evaluation
		if result.evaluation > contribution.currentValuation :
			contribution.valueIndic = 1
		elif result.evaluation < contribution.currentValuation :
			contribution.valueIndic = -1
		else :
			contribution.valueIndic = 0
		contribution.currentValuation = result.evaluation
		session.add(current_evaluation)
		session.add(contribution)
		session.commit()
		return current_evaluation

