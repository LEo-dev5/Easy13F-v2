import httpx
import asyncio
from lxml import html  # HTML 파싱용 (pip install lxml 필요)
import logging

class SECClient:
    BASE_URL = "https://www.sec.gov/cgi-bin/browse-edgar"
    ARCHIVE_URL = "https://www.sec.gov/Archives"

    def __init__(self, user_email: str):
        self.headers = {
            "User-Agent": f"Easy13F-v2/1.0 ({user_email})",
            "Accept-Encoding": "gzip, deflate",
            "Host": "www.sec.gov"
        }
        self.client = httpx.AsyncClient(headers=self.headers, timeout=30.0, follow_redirects=True)

    async def close(self):
        await self.client.aclose()

    async def get_latest_filings_list(self, cik: str):
        """
        1. 해당 기관의 최신 13F-HR 공시 목록(Atom Feed)을 가져옵니다.
        """
        params = {
            "action": "getcompany",
            "CIK": cik,
            "type": "13F-HR", 
            "dateb": "",
            "owner": "exclude",
            "count": 5, # 최신 5개만 확인
            "output": "atom"
        }
        try:
            response = await self.client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            return response.content # bytes로 반환 (lxml 파싱을 위해)
        except Exception as e:
            print(f"❌ [List Error] {cik}: {e}")
            return None

    async def get_information_table_xml(self, accession_number: str, cik: str):
            """
            [최종 수정 버전] 테이블 구조에 의존하지 않고, 페이지 내의 모든 XML 링크를 전수 조사합니다.
            """
            acc_no_dash = accession_number.replace("-", "")
            cik_int = int(cik) # 0 제거
            index_url = f"{self.ARCHIVE_URL}/edgar/data/{cik_int}/{acc_no_dash}/{accession_number}-index.html"
            
            print(f"   👉 Index Page 접속 시도: {index_url}")

            try:
                resp = await self.client.get(index_url)
                tree = html.fromstring(resp.content)
                
                xml_href = None
                candidates = []

                # 전략: 페이지에 있는 모든 <a> 태그 중 .xml로 끝나는 것을 다 긁어모은다.
                all_links = tree.xpath('//a/@href')
                
                for href in all_links:
                    if not href.endswith(".xml"):
                        continue
                    
                    # 대소문자 통일
                    href_upper = href.upper()
                    
                    # [제외 조건] 
                    # 1. 표지(primary) 제외
                    if "PRIMARY" in href_upper:
                        continue
                    # 2. 스타일시트(xsl) 제외 (혹시 xml로 끝날까봐)
                    if "XSL" in href_upper:
                        continue
                    
                    candidates.append(href)

                # 후보군 중에서 'infotable'이나 'information'이 들어간 걸 최우선으로 찾음
                for cand in candidates:
                    if "INFOTABLE" in cand.upper() or "INFORMATION" in cand.upper():
                        xml_href = cand
                        break
                
                # 만약 명시적인 이름이 없다면, 남은 후보 중 첫 번째 XML을 선택 (가장 큰 파일일 확률 높음)
                if not xml_href and candidates:
                    xml_href = candidates[0]
                    print(f"   ⚠️ 명시적인 InfoTable 이름을 못 찾아서, 추정되는 파일을 선택함: {xml_href}")

                if not xml_href:
                    print(f"   ❌ XML 링크를 찾지 못했습니다. 발견된 후보: {candidates}")
                    return None

                print(f"   ✅ Target XML Found: {xml_href}")
                full_xml_url = f"https://www.sec.gov{xml_href}"
                xml_resp = await self.client.get(full_xml_url)
                return xml_resp.content

            except Exception as e:
                print(f"   ❌ [Download Error] {accession_number}: {e}")
                return None