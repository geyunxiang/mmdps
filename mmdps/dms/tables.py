"""Database sql-alchemy tables.

Define the database by sql-alchemy tables.
Can ease the selection of RMDBS, and much more if use ORM properly.
"""

import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class BaseModel(Base):
    """Base model."""
    __abstract__ = True

# table for many to many relationship
association_table_group_person = Table(
    'association_group_person', Base.metadata,
    Column('group_id', Integer, ForeignKey('groups.id')),
    Column('person_id', Integer, ForeignKey('people.id'))
)

class Person(BaseModel):
    """Person."""
    __tablename__ = 'people'
    # columns
    id = Column(Integer, primary_key=True)
    patientid = Column(String)
    name = Column(String)
    gender = Column(String)
    birth = Column(DateTime)
    weight = Column(Integer)
    # relationships
    mriscans = relationship('MRIScan', back_populates='person')
    motionscores = relationship('MotionScore', back_populates='person')
    strokescores = relationship('StrokeScore', back_populates='person')
    groups = relationship('Group', secondary=association_table_group_person, back_populates='people')
    def __repr__(self):
        return "<Person(name='{}', gender='{}', birth='{}', weight='{}'>".format(self.name, self.gender, self.birth, self.weight)

class MRIMachine(BaseModel):
    """MRIMachine."""
    __tablename__ = 'mrimachines'
    # columns
    id = Column(Integer, primary_key=True)
    institution = Column(String)
    manufacturer = Column(String)
    modelname = Column(String)
    # relationships
    mriscans = relationship('MRIScan', back_populates='mrimachine')
    def __repr__(self):
        return "<MRIMachine(institution='{}', manufacturer='{}', modelname='{}'>".format(self.institution, self.manufacturer, self.modelname)
    
class MRIScan(BaseModel):
    """MRIScan."""
    __tablename__ = 'mriscans'
    # columns
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('people.id'))
    mrimachine_id = Column(Integer, ForeignKey('mrimachines.id'))
    date = Column(DateTime)
    hasT1 = Column(Boolean)
    hasT2 = Column(Boolean)
    hasBOLD = Column(Boolean)
    hasDWI = Column(Boolean)
    # relationships
    person = relationship('Person', back_populates='mriscans')
    mrimachine = relationship('MRIMachine', back_populates='mriscans')
    motionscores = relationship('MotionScore', back_populates='mriscan')
    strokescores = relationship('StrokeScore', back_populates='mriscan')
    def __repr__(self):
        return "<MRIScan(person_id='{}', date='{}', hasT1='{}', hasT2='{}', hasBOLD='{}', hasDWI='{}'>".format(self.person_id, self.date, self.hasT1, self.hasT2, self.hasBOLD, self.hasDWI)
    def get_folder(self):
        return "{}_{}".format(self.person.name, datetime.datetime.strftime(self.date, '%Y%m%d'))
    
class MotionScore(BaseModel):
    """MotionScore."""
    __tablename__ = 'motionscores'
    # columns
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('people.id'))
    mriscan_id = Column(Integer, ForeignKey('mriscans.id'))
    date = Column(DateTime)
    scTSI = Column(Float)
    scMotor = Column(Float)
    scSensory = Column(Float)
    scVAS = Column(Float)
    scMAS = Column(Float)
    scWISCI2 = Column(Float)
    scSCIM = Column(Float)
    # relationships
    person = relationship('Person', back_populates='motionscores')
    mriscan = relationship('MRIScan', back_populates='motionscores')
    def __repr__(self):
        return "<MotionScore(person_id='{}', mriscan_id='{}', date='{}', scTSI='{}', scMotor='{}', scSensory='{}', scVAS='{}', scMAS='{}', scWISCI2='{}', scSCIM='{}'>".format(self.person_id, self.mriscan_id, self.date, self.scTSI, self.scMotor, self.scSensory, self.scVAS, self.scMAS, self.scWISCI2, self.scSCIM)
    
class StrokeScore(BaseModel):
    """StrokeScore."""
    __tablename__ = 'strokescores'
    # columns
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('people.id'))
    mriscan_id = Column(Integer, ForeignKey('mriscans.id'))
    date = Column(DateTime)
    scFMA = Column(Float)
    scARAT = Column(Float)
    scWOLF = Column(Float)
    # relationships
    person = relationship('Person', back_populates='strokescores')
    mriscan = relationship('MRIScan', back_populates='strokescores')
    def __repr__(self):
        return "<StrokeScore(person_id='{}', mriscan_id='{}', date='{}', scFMA='{}', scARAT='{}', scWOLF='{}'>".format(self.person_id, self.mriscan_id, self.date, self.scFMA, self.scARAT, self.scWOLF)
    
class Group(BaseModel):
    """Group."""
    __tablename__ = 'groups'
    # columns
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    # relationships
    people = relationship('Person', secondary=association_table_group_person, back_populates='groups')
    def __repr__(self):
        return "<Group(name='{}', description='{}'>".format(self.name, self.description)
    