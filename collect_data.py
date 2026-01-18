import asyncio
import os
from dotenv import load_dotenv
from app.core.database import SessionLocal
from app.core.seeds import TARGET_CIKS
from app.services.sec_client import SECClient
from app.services.parser import parse_13f_xml
from app.services.store import save_filing_data
from lxml import etree

async def process_institution(client, db, cik_info):
    name = cik_info['name']
    cik = cik_info['cik']
    
    print(f"\n📡 처리 중: {name} (CIK: {cik})")
    
    # 1. 목록 가져오기
    atom_content = await client.get_latest_filings_list(cik)
    if not atom_content: return

    # Atom 파싱해서 최신 공시 1개만 가져오기 (초기 구축용)
    # 나중에는 반복문 돌려서 과거 데이터도 가져올 수 있음
    try:
        # lxml의 etree 사용 (Namespaces 주의)
        root = etree.fromstring(atom_content)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        entries = root.findall('atom:entry', ns)
        
        if not entries:
            print("   ⚠️ 공시가 없습니다.")
            return

        # 가장 최신 것 하나만
        latest = entries[0]
        acc_no = latest.findtext('atom:content/atom:accession-number', default=None, namespaces=ns)
        filing_date = latest.findtext('atom:updated', default=None, namespaces=ns) # 예: 2024-05-15T...
        
        if filing_date:
            filing_date = filing_date.split('T')[0] # 시간 자르고 날짜만

        print(f"   📄 최신 보고서 발견: {acc_no} ({filing_date})")

        # 2. XML 다운로드
        xml_content = await client.get_information_table_xml(acc_no, cik)
        if not xml_content: return

        # 3. 파싱
        holdings = parse_13f_xml(xml_content)
        if not holdings:
            print("   ⚠️ 데이터가 비어있습니다.")
            return

        # 4. DB 저장
        save_filing_data(db, cik, name, filing_date, acc_no, holdings)

    except Exception as e:
        print(f"   ❌ 처리 중 오류 발생: {e}")

async def main():
    load_dotenv()
    email = os.getenv("SEC_USER_EMAIL")
    
    # DB 세션 열기
    db = SessionLocal()
    client = SECClient(email)
    
    try:
        print("🚀 EASY13F-V2 데이터 수집 시작...")
        
        # seeds.py에 있는 모든 기관 순회
        for cik_data in TARGET_CIKS:
            await process_institution(client, db, cik_data)
            # SEC 서버 부하 방지를 위해 1초 휴식 (매너)
            await asyncio.sleep(1) 
            
    finally:
        await client.close()
        db.close()
        print("\n🎉 모든 작업이 완료되었습니다.")

if __name__ == "__main__":
    asyncio.run(main())