FROM node:18.20.4-slim

# Python, netcat 및 필요한 빌드 도구 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-openbsd python3 python3-pip build-essential \
    && ln -sf /usr/bin/python3 /usr/bin/python \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set Python path for node-gyp
ENV PYTHON=python3

# Ganache CLI 설치
RUN npm install -g ganache-cli

# Truffle 설치 (권한 문제 해결을 위한 설정 포함)
RUN npm install -g --unsafe-perm truffle

# 프로젝트 코드 복사 (ganache 내부의 모든 파일 복사)
WORKDIR /ganache
COPY . .

# CRLF 제거: Windows 개행 문자를 제거하여 스크립트가 올바르게 실행되도록 함
RUN sed -i 's/\r$//' /ganache/entrypoint.sh

# entrypoint.sh 복사 및 실행 권한 부여
RUN chmod +x /ganache/entrypoint.sh

ENTRYPOINT ["/ganache/entrypoint.sh"]