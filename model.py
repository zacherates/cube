from sqlalchemy import Column, Integer, String, create_engine, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Person(Base):
	__tablename__ = "person"

	id = Column(Integer, primary_key = True)
	name = Column(String(250))

class Card(Base):
	__tablename__ = "card"

	multiverse_id = Column(String, primary_key = True)
	name = Column(String(250))

class Pick(Base):
	__tablename__ = "pick"

	id = Column(Integer, primary_key = True)
	person_id = Column(Integer, ForeignKey('person.id'))
	better = Column(String(250), ForeignKey('card.multiverse_id'))
	worse = Column(String(250), ForeignKey('card.multiverse_id'))


def connect():
	engine = create_engine("sqlite:///picks.sqlite3")
	session = sessionmaker(bind = engine)
	return engine, session

def init():
	engine, session = connect()
	Base.metadata.create_all(engine)

if __name__ == "__main__":
	init()

