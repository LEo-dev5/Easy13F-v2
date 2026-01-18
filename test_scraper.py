# test_scraper.py
import asyncio
import os
from dotenv import load_dotenv
from app.services.sec_client import SECClient
from app.services.parser import parse_13f_xml

# 윈도우에서 asyncio 오류 방지용
if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def main():
    load_dotenv()
    email = os.getenv("SEC_USER_EMAIL")
    if not email:
        print("❌ .env에 SEC_USER_EMAIL을 설정해주세요!")
        return

    client = SECClient(email)
    
    # 워렌 버핏(Berkshire) CIK
    target_cik = "0001067983" 
    print(f"🔍 워렌 버핏({target_cik}) 데이터 조회 중...")

    # 1. 목록 가져오기 (Atom)
    atom_content = await client.get_latest_filings_list(target_cik)
    if not atom_content:
        print("❌ 목록을 가져오지 못했습니다.")
        await client.close()
        return

    # 여기서 Accession Number 하나를 강제로 추출 (테스트용 파싱)
    from lxml import etree
    tree = etree.fromstring(atom_content)
    # 네임스페이스 처리
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    entries = tree.findall('atom:entry', ns)
    
    if not entries:
        print("❌ 공시가 없습니다.")
        await client.close()
        return

    # 가장 최신 공시 하나만 테스트
    latest_entry = entries[0]
    acc_no = latest_entry.findtext('atom:content/atom:accession-number', default=None, namespaces=ns)
    title = latest_entry.findtext('atom:title', namespaces=ns)
    
    print(f"📄 최신 공시 발견: {title} (Accession: {acc_no})")

    # 2. 실제 XML 다운로드 (Information Table 찾기)
    xml_content = await client.get_information_table_xml(acc_no, target_cik)
    
    if xml_content:
        print("✅ XML 다운로드 성공! 데이터 파싱 시작...")
        # 3. 파싱 테스트
        holdings = parse_13f_xml(xml_content)
        print(f"📊 총 {len(holdings)}개의 종목을 찾았습니다!")
        if holdings:
            print("--- 상위 3개 종목 예시 ---")
            for h in holdings[:3]:
                print(h)
    else:
        print("❌ XML을 찾지 못했습니다.")

    await client.close()

if __name__ == "__main__":
    asyncio.run(main())