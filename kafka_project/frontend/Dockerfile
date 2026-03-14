# Step 1 - 빌드 담당
# React app 빌드

FROM node:18 AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install

# 소스 코드 복사
COPY . .
RUN npm run build

# Step 2 -  결과물만 가져옴. 
# frontend 컨테이너에 /app 디렉토리는 존재하지 않게 됨. 
# Nginx로 빌드 파일 서빙하기
From nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx","-g","daemon off;"]
