from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Client(Base):
    __tablename__ = 'Client'
    ClientID = Column(Integer, primary_key=True)
    Email = Column(String, nullable=False, unique=True)
    Name = Column(String, nullable=False)
    Password = Column(String, nullable=False)
    bills = relationship("Bill", back_populates="client")
    sessions = relationship("Session", back_populates="client")
    transactions = relationship("Transaction", back_populates="client")

class Bill(Base):
    __tablename__  = 'Bill'
    BillID = Column(Integer, primary_key=True)
    ClientID = Column(Integer, ForeignKey('Client.ClientID'))
    Coins = Column(Integer, nullable=False)
    client = relationship("Client", back_populates="bills")

class Session(Base):
    __tablename__  = 'Session'
    SessionID = Column(Integer, primary_key=True)
    ClientID = Column(Integer, ForeignKey('Client.ClientID'))
    HashID = Column(String, nullable=False)
    Time = Column(String, nullable=False)
    client = relationship("Client", back_populates="sessions")

class Model(Base):
    __tablename__  = 'Model'
    ModelID = Column(Integer, primary_key=True)
    ModelName = Column(String, nullable=False)
    Cost = Column(Integer, nullable=False)
    ModelPath = Column(String, nullable=False)
    transactions = relationship("Transaction", back_populates="model")

class Transaction(Base):
    __tablename__  = 'Transaction'
    TransactionID = Column(Integer, primary_key=True)
    ClientID = Column(Integer, ForeignKey('Client.ClientID'))
    ModelID = Column(Integer, ForeignKey('Model.ModelID'))
    Time = Column(String, nullable=False)
    client = relationship("Client", back_populates="transactions")
    model = relationship("Model", back_populates="transactions")
