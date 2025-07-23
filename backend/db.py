from sqlalchemy import Column, Integer, String, Float, Date, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class ReceiptORM(Base):
    __tablename__ = "receipts"
    id       = Column(Integer, primary_key=True)
    vendor   = Column(String, index=True)
    date     = Column(Date, index=True)
    amount   = Column(Float)
    category = Column(String, nullable=True)

engine = create_engine("sqlite:///receipts.db", echo=False, future=True)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)
