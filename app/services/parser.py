from lxml import etree

def parse_13f_xml(xml_content):
    """
    [강화 버전] 태그 대소문자(infoTable, infotable) 무시 및 네임스페이스 자동 처리
    """
    if not xml_content:
        return []

    try:
        # 파서 설정 (Recover=True: XML 문법이 약간 틀려도 살려냄)
        parser = etree.XMLParser(recover=True)
        tree = etree.fromstring(xml_content, parser=parser)
    except Exception as e:
        print(f"   ❌ XML Parsing Error: {e}")
        return []

    holdings = []

    # XPath로 대소문자 상관없이 infoTable 태그 찾기 (가장 강력한 방법)
    # local-name()을 사용하여 네임스페이스와 상관없이 태그 이름만 비교
    nodes = tree.xpath("//*[translate(local-name(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='infotable']")

    for info in nodes:
        try:
            # 태그 찾기 함수 (대소문자 무시)
            def find_text(node, tag_name):
                # 자식 노드 중에서 해당 태그 이름을 가진 것 찾기
                res = node.xpath(f".//*[translate(local-name(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='{tag_name.lower()}']")
                return res[0].text if res else None

            # 필수 데이터 추출
            name = find_text(info, 'nameOfIssuer')
            cusip = find_text(info, 'cusip')
            
            # 주식 수 / 가치
            val_text = find_text(info, 'value')
            value = float(val_text) * 1000 if val_text else 0.0
            
            shrs_text = find_text(info, 'sshPrnamt')
            shares = float(shrs_text) if shrs_text else 0.0
            
            # 옵션 구분
            put_call = find_text(info, 'putCall')
            
            if not name: continue # 이름 없으면 스킵

            holding_data = {
                "name": name,
                "ticker": None,
                "cusip": cusip,
                "shares": shares,
                "value": value,
                "pct_portfolio": 0.0,
                "option_type": put_call if put_call else None
            }
            holdings.append(holding_data)
            
        except Exception as e:
            continue
            
    return holdings