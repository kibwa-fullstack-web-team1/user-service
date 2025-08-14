import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

from app import create_app
import uvicorn

# 환경변수 설정
config_name = os.getenv('PHASE') or 'development'
app = create_app(config_name)

if __name__ == '__main__':
    uvicorn.run(
        app,
        host='0.0.0.0',
        port=8000,
    )