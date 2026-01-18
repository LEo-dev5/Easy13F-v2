from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# 1. 환경 변수 로드 (.env 파일에서 DB 주소 가져오기)
load_dotenv()
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# 예외처리: .env가 없거나 URL이 없을 경우를 대비
if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("DATABASE_URL이 .env 파일에 설정되지 않았습니다.")

# 2. 엔진 생성 (실제 DB와의 연결 통로)
# echo=True로 설정하면 실행되는 SQL이 터미널에 보여서 공부할 때 좋습니다.
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)

# 3. 세션 로컬 생성 (DB와 대화하는 '전화기' 같은 존재)
# 요청이 들어올 때마다 이 SessionLocal을 통해 DB 작업을 하고 닫습니다.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. 모델들의 조상님 (Base) 생성
# 앞으로 만들 모든 모델(테이블)은 이 Base를 상속받아야 합니다.
Base = declarative_base()

# 5. DB 세션을 가져오는 유틸리티 함수 (FastAPI에서 의존성 주입으로 사용)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() # 다 썼으면 반드시 전화기를 끊어야 함 (연결 해제)