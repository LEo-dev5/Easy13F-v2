from sqlalchemy.orm import Session
from app.models import Institution, Filing, Holding
from datetime import datetime

def save_filing_data(db: Session, cik: str, name: str, filing_date: str, accession_number: str, holdings_list: list):
    """
    [트랜잭션 버전] 공시와 종목을 한 묶음으로 저장합니다. 실패하면 싹 취소(Rollback)합니다.
    """
    # 1. 기관 확인 및 생성
    institution = db.query(Institution).filter(Institution.cik == cik).first()
    if not institution:
        print(f"   🆕 새로운 기관 등록: {name} ({cik})")
        institution = Institution(name=name, cik=cik)
        db.add(institution)
        db.commit()
        db.refresh(institution)

    # 2. 중복 확인
    exists = db.query(Filing).filter(Filing.accession_number == accession_number).first()
    if exists:
        # 혹시 껍데기만 있는 좀비 데이터인지 확인
        count = db.query(Holding).filter(Holding.filing_id == exists.id).count()
        if count == 0:
            print(f"   🧟 좀비 데이터 발견! 삭제 후 다시 저장합니다.")
            db.delete(exists)
            db.commit()
        else:
            print(f"   ⏭️ 이미 저장된 공시입니다. ({accession_number})")
            return

    # --- 트랜잭션 시작 ---
    try:
        # 날짜 변환
        try:
            f_date = datetime.strptime(filing_date, "%Y-%m-%d").date()
        except:
            f_date = datetime.now().date()

        # 분기 계산
        month = f_date.month
        year = f_date.year
        if 1 <= month <= 3: q = f"{year-1}Q4"
        elif 4 <= month <= 6: q = f"{year}Q1"
        elif 7 <= month <= 9: q = f"{year}Q2"
        else: q = f"{year}Q3"

        # 3. 공시 객체 생성 (Commit 안 함)
        new_filing = Filing(
            institution_id=institution.id,
            quarter=q,
            filing_date=f_date,
            accession_number=accession_number
        )
        db.add(new_filing)
        db.flush() # ID 발급용 임시 저장

        # 4. 종목 데이터 병합
        merged_holdings = {}
        for h in holdings_list:
            key = (h['cusip'], h['option_type'])
            if key not in merged_holdings:
                merged_holdings[key] = h
            else:
                merged_holdings[key]['shares'] += h['shares']
                merged_holdings[key]['value'] += h['value']

        holdings_to_save = []
        for h in merged_holdings.values():
            db_holding = Holding(
                filing_id=new_filing.id,
                name=h['name'],
                ticker=h['ticker'],
                cusip=h['cusip'],
                shares=h['shares'],
                value=h['value'],
                pct_portfolio=0.0,
                option_type=h['option_type']
            )
            holdings_to_save.append(db_holding)

        if holdings_to_save:
            db.bulk_save_objects(holdings_to_save)
            db.commit() # [최종 저장] 여기서 한 번에 저장됨!
            print(f"   💾 저장 완료! {len(holdings_to_save)}개 종목 저장됨.")
        else:
            db.rollback()
            print("   ⚠️ 파싱된 종목이 없습니다. (저장 취소)")

    except Exception as e:
        print(f"   ❌ 저장 중 치명적 오류: {e}")
        db.rollback()
        raise e