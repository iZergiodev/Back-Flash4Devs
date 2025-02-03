import os
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from dotenv import load_dotenv

load_dotenv()



sqliteName = 'flash4devs.sqlite'
base_dir = os.path.dirname(os.path.realpath(__file__))
data_base_url = os.getenv("DATABASE_URL")
print(data_base_url)

engine = create_engine(data_base_url, echo = True)

Session = sessionmaker(bind=engine)


Base = declarative_base()
