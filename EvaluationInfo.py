class EvaluationInfo(object):
    def __init__(self, tokens,reputation,stake,agentId):
        self.tokens = float(tokens)
        self.reputation = float(reputation)
        self.stake = float(stake)    
        self.agentId = agentId    

    def debug(self,logger):
        if(logger):
            logger.info('tokens: '+str(self.tokens))
            logger.info('reputation: '+str(self.reputation))
            logger.info('stake: '+str(self.stake))
            logger.info('agentId: '+str(self.agentId))