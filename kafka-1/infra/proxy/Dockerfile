# 1. React 빌드
# 베이스 이미지 지정
FROM node:18 AS build

# 워크디렉토리 생성/지정
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install 

# frontend 디렉토리 소스 코드 복사
COPY frontend ./
# 복사한 코드(React) 빌드
RUN npm run build

# 2. Nginx로 정적 파일 서빙
# 베이스 이미지 지정
FROM nginx:alpine

# React 빌드한 결과를 /app/build 디렉토리로 복사해오기
COPY --from=build /app/build /usr/share/nginx/html

# nginx.conf로 로컬 호스트의 /etc/nginx/conf.d/default.conf의 내용 복사해오기
COPY infra/proxy/nginx.conf /etc/nginx/conf.d/default.conf
# 80번 포트 개방

EXPOSE 80
CMD ["nginx","-g","daemon off;"]
