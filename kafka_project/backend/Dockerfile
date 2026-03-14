# 베이스 이미지 설정
FROM python:3.10

# 기본 작업 디렉토리 지정 (호스트 디렉토리와 무관함)
WORKDIR /app


RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y --no-install-recommends \
	libsystemd-dev build-essential python3-dev \
	&& rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade \
	pip setuptools wheel

# requirements.txot 복사
COPY requirements.txt .
 
# 빌드 격리 해제하고 파이썬 패키지 설치
RUN pip install --no-cache-dir --no-build-isolation -r requirements.txt

# 소스코드 복사
COPY . .

# static 파일 수집
RUN python manage.py collectstatic --noinput

# 포트 노출
EXPOSE 8000

# 컨테이너 시작 커맨드
CMD ["gunicorn", "config.wsgi:application", "--workers", "3", "--bind", "0.0.0.0:8000"]
