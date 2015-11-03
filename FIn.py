class FIn(object):
    def __init__(self, evaluations,current_evaluation,total_rep,similarEvaluationRate):
        self.evaluations = evaluations
        self.current_evaluation = current_evaluation
        self.total_system_reputation = total_rep
        self.similarEvaluationRate = similarEvaluationRate
        
    def isValid(self):
        if (not self.evaluations or
            not self.total_system_reputation or
            not self):
            return False
        return True
        
    def debug(self,logger):
        if(logger):
            logger.info('\n')
            
            logger.info('F input:')
            """
            logger.info('evaluations:')
            for evaluation in self.evaluation:
                evaluation.debug(logger)
            """
            logger.info('current evaluation: ')
            self.current_evaluation.debug(logger)
            logger.info('total system reputation: '+str(self.total_system_reputation))
            
        return True