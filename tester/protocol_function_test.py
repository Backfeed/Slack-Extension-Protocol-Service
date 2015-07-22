from protocol_function import BidInfo,FIn,ProtocolFunctionV1

import logging
import logging.config

logging.config.fileConfig("p_function_logging.conf")
logger = logging.getLogger("loading")


bids = [{
			'owner':1,
			'reputation':4,
			'tokens':10,
			'stake':4
		},
		{
			'owner':2,
			'reputation':16,
			'tokens':13,
			'stake':16
		}
		]

# establish bids:
bidsInfo = []
for bid in bids:
	bifInfo = BidInfo(bid['tokens'],bid['reputation'],bid['stake'],bid['owner'])
	bidsInfo.append(bifInfo)

# establish current bid (to be last bid):
current_bid_info = bidsInfo[-1]

# establish total system reputation:
total_sys_rep = 30

fin = FIn(bidsInfo,current_bid_info,total_sys_rep)
f = ProtocolFunctionV1(logger)
f.execute(fin)


