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