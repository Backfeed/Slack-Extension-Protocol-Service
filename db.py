
#from sqlalchemy import create_engine
#from sqlalchemy.orm import scoped_session
#from sqlalchemy.orm import sessionmaker

from sqlalchemy import orm
from sqlalchemy import create_engine
from settings import DB_URI
import model as model
#import model
"""
Session = sessionmaker(autocommit=False,
                       autoflush=False,
                       bind=create_engine(DB_URI))
session = scoped_session(Session)
"""

# Create an engine and create all the tables we need
engine = create_engine(DB_URI,echo=True)
model.metadata.bind = engine
#model.metadata.create_all()
sm = orm.sessionmaker(bind=engine, autoflush=False, autocommit=False,expire_on_commit=True)
session = orm.scoped_session(sm)

