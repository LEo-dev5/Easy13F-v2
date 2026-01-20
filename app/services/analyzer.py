from sqlalchemy.orm import Session
from app.models import Filing, Holding
from app.core.database import SessionLocal
import json
import httpx
import asyncio

# ==========================================
# 1. 포트폴리오 비중(%) 계산
# ==========================================
def update_portfolio_percentage(db: Session):
    print("📊 포트폴리오 비중 계산 시작...")
    
    # 모든 공시(Filing)를 가져옵니다.
    filings = db.query(Filing).all()
    
    count = 0
    for filing in filings:
        # 해당 공시의 모든 보유 종목을 가져옴
        holdings = db.query(Holding).filter(Holding.filing_id == filing.id).all()
        
        if not holdings:
            continue
            
        # 전체 가치 합산 (총 자산)
        total_value = sum(h.value for h in holdings)
        
        if total_value == 0:
            continue

        # 각 종목별 비중 계산 및 업데이트
        for h in holdings:
            # (종목가치 / 총자산) * 100
            pct = (h.value / total_value) * 100
            h.pct_portfolio = round(pct, 4) # 소수점 4자리까지
        
        count += 1
    
    db.commit()
    print(f"✅ 총 {count}개 공시의 포트폴리오 비중 업데이트 완료!")

# ==========================================
# 2. 티커(Ticker) 매핑 (SEC 공식 데이터 활용)
# ==========================================
async def update_tickers(db: Session):
    print("🔤 티커(Ticker) 매핑 시작 (SEC 데이터 다운로드 중)...")
    
    # SEC에서 제공하는 CIK-Ticker-Name 매핑 JSON 다운로드
    url = "https://www.sec.gov/files/company_tickers.json"
    headers = {"User-Agent": "Easy13F-v2/1.0 (myemail@example.com)"}
    
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
        if resp.status_code != 200:
            print("❌ SEC 티커 데이터 다운로드 실패")
            return
        
        raw_data = resp.json()

    # 데이터 변환: { "APPLE INC": "AAPL", ... } 형태로 만들기
    # SEC 데이터는 CUSIP은 안 주지만, '회사 이름'으로 매칭할 수 있습니다.
    name_to_ticker = {}
    
    # raw_data는 인덱스 키(0, 1, 2...)로 되어 있음
    for item in raw_data.values():
        ticker = item['ticker']
        title = item['title'].upper() # 대문자로 통일
        name_to_ticker[title] = ticker

    # DB에 있는 종목들 업데이트
    holdings = db.query(Holding).filter(Holding.ticker == None).all()
    
    updated_count = 0
    for h in holdings:
        # DB에 있는 이름 정제 (예: "APPLE INC" -> "APPLE INC")
        # 정확히 일치하지 않을 수 있으니, "포함" 여부나 간단한 정제 필요
        db_name = h.name.upper().strip()
        
        # 1. 완전 일치 시도
        if db_name in name_to_ticker:
            h.ticker = name_to_ticker[db_name]
            updated_count += 1
            continue
            
        # 2. 부분 일치 시도 (간단한 로직)
        # 예: "AMAZON COM INC" vs "AMAZON COM INC"
        # 너무 복잡하면 오래 걸리니 여기선 간단히 스킵하거나 나중에 정교화
        
        # 유명 종목 하드코딩 (예시)
        if "APPLE INC" in db_name: h.ticker = "AAPL"
        elif "MICROSOFT" in db_name: h.ticker = "MSFT"
        elif "AMAZON" in db_name: h.ticker = "AMZN"
        elif "TESLA" in db_name: h.ticker = "TSLA"
        elif "NVIDIA" in db_name: h.ticker = "NVDA"
        elif "NETFLIX" in db_name: h.ticker = "NFLX"
        elif "META PLATFORMS" in db_name: h.ticker = "META"
        elif "ALPHABET INC" in db_name: h.ticker = "GOOGL"
        
        if h.ticker:
            updated_count += 1

    db.commit()
    print(f"✅ {updated_count}개 종목의 티커 업데이트 완료!")

# 실행기
if __name__ == "__main__":
    db = SessionLocal()
    
    # 1. 비중 계산
    update_portfolio_percentage(db)
    
    # 2. 티커 매핑 (비동기라 실행 방식 다름)
    asyncio.run(update_tickers(db))
    
    db.close()