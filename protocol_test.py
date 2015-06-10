import classes as cls
from datetime import datetime

from sqlalchemy import orm
from sqlalchemy import create_engine
from settings import DB_URI
import model as model
import vdp

"""
Session = sessionmaker(autocommit=False,
                       autoflush=False,
                       bind=create_engine(DB_URI))
session = scoped_session(Session)
"""

# Create an engine and create all the tables we need
engine = create_engine(DB_URI,echo=False)
model.metadata.bind = engine
model.metadata.create_all()
sm = orm.sessionmaker(bind=engine, autoflush=False, autocommit=False,expire_on_commit=True)
session = orm.scoped_session(sm)

contributionObject = session.query(cls.Contribution).filter(cls.Contribution.id == 1).first()
"""
print 'contribution bids:\n'
for bid in contributionObject.bids:
	print bid
"""

bid_dict = {"tokens":60,
   "reputation":40,
   "owner":3,
   "contribution_id":1,
	"stake":10,
	"time_created":datetime.now()
    }
curent_bid = cls.Bid(bid_dict,session)

vdp.process_bid(curent_bid)
