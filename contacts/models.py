"""
Models
"""
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey

Base = declarative_base()



class Person(Base):
    """Total information about Person"""

    __tablename__ = "person"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(50))
    phones = relationship("Phones", cascade="all, delete", backref="person")
    address = relationship("Address", cascade="all, delete", backref="person")
    data = relationship("Files", cascade="all, delete", backref="person")
    birthday = Column(DateTime, nullable=True)
    

class Phones(Base):
    """Information about Person phones"""

    __tablename__ = "phones"
    id = Column(Integer, primary_key=True)
    phone = Column(Integer)
    person_id = Column(Integer, ForeignKey("person.id", ondelete="CASCADE"))


class Address(Base):
    """Information about Person address"""

    __tablename__ = "address"
    id = Column(Integer, primary_key=True)
    country = Column(String(50))
    city = Column(String(50))
    street = Column(String(50))
    building_number = Column(String(50))
    flat_number = Column(String(50))
    person_id = Column(Integer, ForeignKey("person.id", ondelete="CASCADE"))


class Files(Base):
    """Information about Person files"""

    __tablename__ = "files"
    id = Column(Integer, primary_key=True)
    file_name = Column(String(50))
    file_extension = Column(String(50))    
    file_storage_path = Column(String(100))
    person_id = Column(Integer, ForeignKey("person.id", ondelete="CASCADE"))

#engine = create_engine('sqlite:///contacts.db', connect_args={'check_same_thread': False})
#Base.metadata.create_all(engine) 