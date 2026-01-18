from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .core.database import Base

# 1. 기관 테이블

class Institution(Base):
    __tablename__ = "institutions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String,index=True, nullable=False)
    cik = Column(String, unique=True, index=True, nullable=False)
    
    # [관계 설정]
    # 이 기관이 낸 공시들을 리스트로 가져옴
    # cascade="all, delete-orphan": 기관을 DB에서 지우면, 소속된 공시들도 같이 삭제됨 (데이터 무결성)
    filings = relationship("Filing", back_populates="institution", cascade="all, delete-orphan")


# 2. 공시 테이블
class Filing(Base):
    __tablename__ = "filings"

    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(Integer, ForeignKey("institutions.id"), nullable=False)

    quarter = Column(String, nullable=False)    #공시 분기 예: 2023Q1
    filing_date = Column(Date, nullable=False)  #공시 날짜  
    accession_number = Column(String, unique=True, index=True, nullable=False) #고유 공시 번호 

    created_at = Column(DateTime(timezone=True), server_default=func.now()) # 데이터 수정 생성 시간

    #[관계 설정]
    institution = relationship("Institution", back_populates="filings")  # 소속 기관
    holdings = relationship("Holding", back_populates="filing", cascade="all, delete-orphan")  # 이 공시의 보유 종목들

    # 3. 보유 종목 테이블
class Holding(Base):
    __tablename__ = "holdings"
    id = Column(Integer, primary_key=True, index=True)
    filing_id = Column(Integer, ForeignKey("filings.id"), nullable=False)

    name = Column(String, nullable=False)           #종목명
    ticker = Column(String, nullable=True)         #종목 티커
    cusip = Column(String, index=True, nullable=False)   #CUSIP 식별자

    shares = Column(Float, nullable=False)        #보유 주식 수 소수점 일수도 있어서 Float
    value = Column(Float, nullable=False)         #보유 주식 가치 (달러 단위)
    pct_portfolio = Column(Float, nullable=False)  #포트폴리오 내 비중 (%)

    #put call 구분
    option_type = Column(String, nullable=True)

    filing = relationship("Filing", back_populates="holdings")



