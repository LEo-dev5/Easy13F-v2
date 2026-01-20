from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models import Institution, Filing, Holding
from app.schemas.filing import InstitutionResponse, FilingResponse, HoldingResponse

router = APIRouter()

# 1. 모든 기관 목록 조회
@router.get("/institutions", response_model=List[InstitutionResponse])
def read_institutions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    institutions = db.query(Institution).offset(skip).limit(limit).all()
    return institutions

# 2. 특정 기관의 공시(보고서) 목록 조회
@router.get("/institutions/{institution_id}/filings", response_model=List[FilingResponse])
def read_institution_filings(institution_id: int, db: Session = Depends(get_db)):
    filings = db.query(Filing).filter(Filing.institution_id == institution_id).order_by(Filing.filing_date.desc()).all()
    if not filings:
        raise HTTPException(status_code=404, detail="Filings not found")
    return filings

# 3. 특정 공시의 보유 종목 상세 조회 (핵심!)
@router.get("/filings/{filing_id}/holdings", response_model=List[HoldingResponse])
def read_filing_holdings(filing_id: int, db: Session = Depends(get_db)):
    # 가치(value)가 큰 순서대로 정렬해서 가져오기
    holdings = db.query(Holding).filter(Holding.filing_id == filing_id).order_by(Holding.value.desc()).all()
    return holdings