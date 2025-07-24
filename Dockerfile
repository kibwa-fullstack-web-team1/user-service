# Python 3.12 기반 이미지 사용
FROM python:3.12-slim

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 시스템 의존성 설치
# libpq-dev: PostgreSQL 클라이언트 라이브러리 (psycopg2 필요)
# gcc: C 컴파일러 (일부 Python 패키지 빌드 시 필요)
RUN apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# 의존성 파일 복사 및 설치
COPY user-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY user-service/app ./app
COPY user-service/user-service_manage.py .

# 서비스 포트 노출
EXPOSE 8000

# 애플리케이션 실행 명령어
CMD ["python", "user-service_manage.py"]