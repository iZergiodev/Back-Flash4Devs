import os
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


sqliteName = 'flash4devs.sqlite'
base_dir = os.path.dirname(os.path.realpath(__file__))
data_base_url = f'sqlite:///{os.path.join(base_dir, sqliteName)}'

engine = create_engine(data_base_url, echo = True)

Session = sessionmaker(bind=engine)


Base = declarative_base()