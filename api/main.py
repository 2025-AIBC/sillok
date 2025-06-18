# [추가로 구현해야 할 API 리스트]
# [-] 마크다운 파일 저장(Create): 임베딩 => 크로마DB => (원본 문서, 그에 따른 벡터 임베딩) 2가지를 IPFS에 저장 => CID 및 메타데이터를 블록체인에 저장 => TxHash와 메타데이터를 postgres에 저장.
#   - 마크다운 파일 업데이트(Update): 위 기능 구현 후 가장 첫단계로 기존에 있는지 확인. 있다면 업데이트하는 것으로 구현
# - 마크다운 파일 삭제(Delete): 삭제하고자 하는 데이터(user_id + title + created_date)에 해당하는 파일의 내용에 `is_deleted`값을 업데이트. (완전삭제는 추후 구현 대상)
# - 마크다운 파일 읽어오기(개별파일;Read): 해당하는 user_id 내의 해당 파일이 (1)존재하는지, (2) `is_deleted=False`인지 확인 후 맞다면 해당 파일 읽어서 반환.
# - 사용자에 따른 마크다운 파일 리스트 가져오기(Read): 사용자의 메타데이터를 살펴보고 `is_deleted = False`인 모든 CID에 대해 검색해서 그 목록을 문서 제목과 함께 반환.
# - 사용자의 모든 마크다운으로 구성된 Vector Store(크로마DB)를 이용한 랭체인 기반 RAG 결과 생성: 
# - 사용자 파일에 대한 검증 기능(Read): 일단은 해당 마크다운의 자료가 블록체인 CID => IPFS 로 찾은 문서의 내용과 동일한지 확인하도록 구현
#   - 보다 구체적인 로직은 좀 더 생각해봐야 함.
# - (Additionally) IPFS에 저장할 때 암호화 먹여서 저장. 찾을 때 decryption 지원. (복호화 정보는 user_id에 따라 저장하면 됨.)

import json
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models, schemas, utils

import time, os
from web3 import Web3, HTTPProvider
from eth_account import Account

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db_data():
    db = SessionLocal()
    try:
        file_paths = {
            "Users": "./samples/CreateUserSample.json",
            "Files": "./samples/CreateFileSample.json",
        }
        for model_name, file_path in file_paths.items():
            with open(file_path, encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines:
                    item = json.loads(line)
                    if model_name == "Users":
                        user = schemas.UserCreate(**item)
                        utils.create_user(user, db)
                    # elif model_name == "Files":
                    #     file = schemas.FileCreate(**item)
                    #     utils.create_file(file, db) # 중복 생성 수정 필요
    finally:
        db.close()


# --- Web3 / 스마트 컨트랙트 설정 ---
WORLDLAND_RPC = os.getenv("WORLDLAND_RPC", "http://127.0.0.1:8545") # 6?
CHAIN_ID = int(os.getenv("WORLDLAND_CHAIN_ID", "250407"))
PRIVATE_KEY = "8eb2f0a69ea741dc8e3e3385c5903b25562ef77b0302338642d17b45a7f46921"  # 서비스 계정 개인키

w3 = Web3(HTTPProvider(WORLDLAND_RPC))
service_account = Account.from_key(PRIVATE_KEY) if PRIVATE_KEY else None
print()
print()
print("service_account0:", service_account)
print()
print()
print()
# ABI 로드 및 컨트랙트 인스턴스 생성
# 3) ABI 로드
abi_path = os.getenv("ABI_PATH", "/app/ganache_build/contracts/MetaDataStoreContract.json")
with open(abi_path, "r") as f:
    artifact     = json.load(f)
    contract_abi = artifact["abi"]
contract_address = os.getenv("CONTRACT_ADDRESS", "0x4f28be56BA833340c5A4BA9a5AeE95e2Ce8f3aa8")
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Initialize the database with JSON data
init_db_data()

##############################
############ APIs ############
##############################
@app.get("/api/") #TEST
def test():
    return "OK"

@app.get("/api/eth_accounts")
def eth_accounts():
    return {"accounts": w3.eth.accounts}

@app.get("/api/chain_status/")
def chain_status():
    """현재 체인 ID와 최신 블록 번호를 반환합니다."""
    return {
        "chainId": w3.eth.chain_id,
        "latestBlock": w3.eth.block_number
    }
    
@app.get("/api/tx_receipt/")
def tx_receipt(txHash: str):
    """주어진 트랜잭션 해시의 receipt를 반환합니다."""
    receipt = w3.eth.get_transaction_receipt(txHash)
    return {
        "transactionHash": receipt.transactionHash.hex(),
        "blockNumber": receipt.blockNumber,
        "status": receipt.status
    }
    
@app.get("/api/tx_receipt/")
async def tx_receipt(txHash: str = Query(..., min_length=1)):
    try:
        receipt = w3.eth.get_transaction_receipt(txHash)
        return {
            "blockNumber": receipt.blockNumber,
            "transactionHash": receipt.transactionHash.hex(),
            "status": receipt.status
        }
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Transaction {txHash} not found")    
    
@app.post("/api/auth/")
async def authenticate_user(auth_request: schemas.AuthRequest, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.account == auth_request.user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="계정이 없습니다.")
    if db_user.password != auth_request.user_pw:
        raise HTTPException(status_code=401, detail="잘못된 비밀번호입니다.")
    
    return JSONResponse(content={"user_id": db_user.user_id, "name": db_user.name, "account": db_user.account, "email": db_user.email, "message": "로그인 성공."})

@app.post("/api/create/")
async def create_file(file: schemas.FileCreate, db: Session = Depends(get_db)):
    # 1) 오프체인 저장
    db_file = utils.create_file(file, db)

    # 2) 온체인 메타데이터 기록 (서비스 계정 사용)
    if service_account:
        nonce = w3.eth.get_transaction_count(service_account.address)
        tx = contract.functions.storeFileMetadata(
            db_file.CID,
            db_file.type,
            int(db_file.last_update.timestamp()),
            False,
            db_file.user_id
        ).build_transaction({
            'from': service_account.address,
            'nonce': nonce,
            'gas': 300000,
            'chainId': CHAIN_ID
        })
        print(f"ifif Transaction to be sent: {tx}")

        # 트랜잭션 서명 및 전송
        signed = service_account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        print(f"Sent tx hash: {tx_hash.hex()}")
        
        db_file.TXHash = tx_hash.hex()
        print(f"txhashTransaction to be sent: {tx_hash}")
        db.commit()
    else:
        print("esleesleesleesleesleesleesleesleesle")
        db_file.TXHash = ""
            
    return JSONResponse(content={"UserID": db_file.user_id, "CID": db_file.CID,"TXHash": db_file.TXHash,"fname": db_file.fname,"last_update": db_file.last_update.strftime('%Y-%m-%d %H:%M:%S'),"message": "파일 생성 성공."})

@app.post("/api/update/")
async def update_file(file: schemas.FileUpdate, db: Session = Depends(get_db)):
    db_file = utils.update_file(file, db)
    # 온체인 메타데이터 기록 (서비스 계정 사용)
    if service_account:
        nonce = w3.eth.get_transaction_count(service_account.address)
        tx = contract.functions.storeFileMetadata(
            db_file.CID,
            db_file.type,
            int(db_file.last_update.timestamp()),
            False,
            db_file.user_id
        ).buildTransaction({
            'from': service_account.address,
            'nonce': nonce,
            'gas': 300000,
            'chainId': CHAIN_ID
        })
        signed = service_account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
        db_file.TXHash = tx_hash.hex()
        db.commit()
    else:
        db_file.TXHash = ""    
    return JSONResponse(content={"CID": db_file.CID,"TXHash": db_file.TXHash,"fname": db_file.fname,"last_update": db_file.last_update.strftime('%Y-%m-%d %H:%M:%S'),"message": "파일 생성 성공."})

@app.delete("/api/delete_file/")
@app.post("/api/delete_file/")
async def delete_file(del_request: schemas.fileDelete, db: Session = Depends(get_db)):
    fname = utils.delete_file_by_cid(del_request.cid, db)
    return JSONResponse(content={"message": f"CID {del_request.cid}에 해당하는{fname} 파일이 삭제되었습니다.", "CID":del_request.cid, "fname":fname})

# async def delete_file(del_request: schemas.fileDelete, db: Session = Depends(get_db)):
#     fname = utils.delete_file_by_cid(del_request.cid, db)
#     return {"message": f"CID {del_request.cid}에 해당하는 {fname} 파일이 삭제되었습니다.",
#             "CID": del_request.cid, "fname": fname}
    
    
@app.post("/api/restore/")
async def restore_file(req: schemas.fileDelete, db: Session = Depends(get_db)):
    db_file = utils.restore_file_by_cid(req.cid, db)
    return JSONResponse(content={"CID": db_file.CID, "fname": db_file.fname, "message": "파일 복구 성공."})

@app.post("/api/read_by_user_id/", response_model=list)
async def read_file(read_request:schemas.ReadRequest, db: Session = Depends(get_db)):
    return utils.get_txhash_and_cid_by_user_id(read_request.user_id, db)

@app.post("/api/restore/", response_model=list)
async def restore_files(req: schemas.RestoreRequest, db: Session = Depends(get_db)):
    return utils.restore_user_files(req.user_id, db)

@app.post("/api/chat/")
async def chat_generation_invoke(query_request:schemas.chatRequest):
    return JSONResponse(content={"assistant":utils.rag_chain.invoke(query_request.question)})
