#!/bin/bash

# Ganache 시작
ganache-cli -a 2 -m "test test test test test test test test test test test junk" --host 0.0.0.0 --port 8545 --networkId 1337 --debug &

# Ganache가 실행될 때까지 대기
while ! nc -z localhost 8545; do   
  sleep 1
done

# 스마트 컨트랙트 배포
cd /ganache  # ganache 디렉토리로 이동
truffle compile
# truffle migrate --reset # 만약 컨트랜트를 재배포해야 하면 이 커맨드 실행
truffle migrate --network development


# Ganache의 실행을 지속
wait
