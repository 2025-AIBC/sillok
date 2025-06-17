# Integrating WorldLand Private Network with MetaMask and a FastAPI+Gradio DApp
## Truffle 프로젝트로 스마트 컨트랙트를 관리
Local Ganache 환경에서 컨트랙트를 컴파일, 배포, 확인

## 로컬 Ganache에 MetaDataStoreContract(및 Migrations)의 정상 배포 확인 (개발-디버그용) (컨트랙트 로직 정상 동작 검증)
- `contracts/Migrations.sol` 및 `migrations/1_initial_migration.js` 파일 추가 필요
  
#### 1) Ganache 로컬 체인 실행: 로컬 RPC 서버(포트 8545, 체인 ID 1337) 및 테스트용 계정 2개 생성
```bash
npx ganache-cli -a 2 -m "test test test test test test test test test test test junk" --host 0.0.0.0 --port 8545 --networkId 1337
```
#### 2) 기존 빌드 결과 삭제: 재컴파일/재배포를 위해 산출물 폴더 초기화
```bash
rm -rf build
```
#### 3) 스마트 컨트랙트 컴파일: atrifact 생성
```bash
npx truffle compile
```
#### 4) 컨트랙트 배포 (development 네트워크, Ganache)
```bash
npx truffle migrate --network development --reset
```
#### 5) Truffle 콘솔로 배포된 인스턴스 확인
```bash
npx truffle console --network development
```

# Integrating WorldLand Private Network with MetaMask and a FastAPI+Gradio DApp
