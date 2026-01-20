from pydantic import BaseModel
from datetime import date
from typing import List, Optional

# 1. 종목 정보 (Holding) 스키마
class HoldingResponse(BaseModel):
    name: str
    cusip: str
    ticker: Optional[str] = None
    shares: float
    value: float
    pct_portfolio: float
    option_type: Optional[str] = None

    class Config:
        from_attributes = True # ORM 객체(SQLAlchemy)를 Pydantic으로 자동 변환

# 2. 공시 정보 (Filing) 스키마
class FilingResponse(BaseModel):
    id: int
    quarter: str
    filing_date: date
    accession_number: str
    # holdings: List[HoldingResponse] = [] # 목록엔 너무 많으니 상세 조회 때만 포함

    class Config:
        from_attributes = True

# 3. 기관 정보 (Institution) 스키마
class InstitutionResponse(BaseModel):
    id: int
    name: str
    cik: str
    
    class Config:
        from_attributes = True