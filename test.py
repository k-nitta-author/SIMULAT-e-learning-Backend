from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('mysql://root:koolele@127.0.0.1:3306/simulatdb')
Base = declarative_base()

Session = sessionmaker(bind=engine)
session = Session()



class Student(Base):
    __tablename__ = 'students'

    dob = Column(Date)
    gender= Column(String(20))
    enrollment_date = Column(Date)
    id = Column(Integer, primary_key=True)
    name=Column(String(23))




Base.metadata.create_all(engine)

new_student = Student(
    name='Jane',
    dob='1990-05-01',
    enrollment_date="1990-05-01",
    gender="female" 
    )

session.add(new_student)
session.commit()

