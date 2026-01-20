from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as api_router

app = FastAPI(
    title="EASY13F-V2 API",
    description="미국 기관 투자자 포트폴리오 데이터 API",
    version="2.0.0"
)

# CORS 설정 (프론트엔드에서 접속 허용)
# 라즈베리파이 호스팅 시 origins에 도메인 추가 필요
origins = [
    "http://localhost",
    "http://localhost:3000", # React/Next.js 개발 서버
    "*" # 개발 중에는 모든 접속 허용 (배포 시 보안 주의)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to EASY13F V2 API! 🚀"}