# app/core/seeds.py

# CIK는 문자열로 관리해야 합니다 (앞에 0이 중요함)
TARGET_CIKS = [
    # --- 유명 슈퍼 인베스터 ---
    {"name": "BERKSHIRE HATHAWAY (Warren Buffett)", "cik": "0001067983"},
    {"name": "BRIDGEWATER ASSOCIATES (Ray Dalio)", "cik": "0001350694"},
    {"name": "SCION ASSET MANAGEMENT (Michael Burry)", "cik": "0001649339"},
    {"name": "PERSHING SQUARE (Bill Ackman)", "cik": "0001336528"},
    {"name": "RENAISSANCE TECHNOLOGIES (Jim Simons)", "cik": "0001037389"},
    {"name": "APPALOOSA (David Tepper)", "cik": "0001006438"},
    {"name": "ARK INVESTMENT (Cathie Wood)", "cik": "0001697748"},
    {"name": "DUQUESNE FAMILY OFFICE (Stanley Druckenmiller)", "cik": "0001536411"},
    
    # --- 초대형 기관 (시장 흐름 파악용) ---
    {"name": "VANGUARD GROUP", "cik": "0000102909"},
    {"name": "BLACKROCK", "cik": "0001364742"},
    {"name": "STATE STREET CORP", "cik": "0000093751"},
    {"name": "JPMORGAN CHASE", "cik": "0000019617"},
    {"name": "GOLDMAN SACHS", "cik": "0000886982"},
    {"name": "MORGAN STANLEY", "cik": "0000895421"},
    {"name": "CITADEL ADVISORS", "cik": "0001423053"},
    {"name": "TIGER GLOBAL", "cik": "0001167483"},
    {"name": "THIRD POINT (Daniel Loeb)", "cik": "0001040273"},
    {"name": "SOROS FUND MANAGEMENT", "cik": "0001029160"},
    {"name": "BAILLIE GIFFORD", "cik": "0001088875"},
    {"name": "SUSQUEHANNA", "cik": "0001446194"},
]