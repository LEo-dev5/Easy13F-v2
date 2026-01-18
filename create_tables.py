from app.core.database import engine, Base
# 우리가 정의한 모델들을 가져와야 Base가 인식을 합니다.
from app.models import Institution, Filing, Holding

print("테이블 생성 시작...")
Base.metadata.create_all(bind=engine)
print("✅ 테이블 생성 완료! pgAdmin에서 확인해보세요.")