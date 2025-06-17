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
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models, schemas, utils

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

# Initialize the database with JSON data
init_db_data()

##############################
############ APIs ############
##############################
@app.get("/api/") #TEST
def test():
    return "OK"

@app.post("/api/auth/")
async def authenticate_user(auth_request: schemas.AuthRequest, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.account == auth_request.user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="계정이 없습니다.")
    if db_user.password != auth_request.user_pw:
        raise HTTPException(status_code=401, detail="잘못된 비밀번호입니다.")
    
    return JSONResponse(content={"user_id": db_user.user_id, "name": db_user.name, "account": db_user.account, "email": db_user.email, "message": "로그인 성공."})
    # {
    #     "user_id": db_user.user_id,
    #     "name": db_user.name,
    #     "account": db_user.account,
    #     # "password": db_user.password,
    #     # "created_date": db_user.created_date,
    #     "email": db_user.email,
    #     # "birthday": db_user.birthday,
    #     # "gender": db_user.gender,
    #     "message": "로그인 성공."
    # }

@app.post("/api/create/")
async def create_file(file: schemas.FileCreate, db: Session = Depends(get_db)):
    db_file = utils.create_file(file, db)
    return JSONResponse(content={"UserID": db_file.user_id, "CID": db_file.CID,"TXHash": db_file.TXHash,"fname": db_file.fname,"last_update": db_file.last_update.strftime('%Y-%m-%d %H:%M:%S'),"message": "파일 생성 성공."})

@app.post("/api/update/")
async def create_file(file: schemas.FileUpdate, db: Session = Depends(get_db)):
    db_file = utils.update_file(file, db)
    return JSONResponse(content={"CID": db_file.CID,"TXHash": db_file.TXHash,"fname": db_file.fname,"last_update": db_file.last_update.strftime('%Y-%m-%d %H:%M:%S'),"message": "파일 생성 성공."})

@app.post("/api/delete_file/")
async def delete_file(del_request: schemas.fileDelete, db: Session = Depends(get_db)):
    fname = utils.delete_file_by_cid(del_request.cid, db)
    return JSONResponse(content={"message": f"CID {del_request.cid}에 해당하는{fname} 파일이 삭제되었습니다.", "CID":del_request.cid, "fname":fname})

@app.post("/api/restore/")
async def restore_file(req: schemas.fileDelete, db: Session = Depends(get_db)):
    db_file = utils.restore_file_by_cid(req.cid, db)
    return JSONResponse(content={"CID": db_file.CID, "fname": db_file.fname, "message": "파일 복구 성공."})
# db_file = models.File(
#         CID=cid,
#         fname=request_data.fname, 
#         type=request_data.type,
#         last_update=metadata["last_update"],
#         is_deleted=metadata["is_deleted"],
#         user_id=request_data.user_id,
#         TXHash=tx_hash,
#         content=request_data.content # 빠른 사용을 위해 CID와 병행
#     )
@app.post("/api/read_by_user_id/", response_model=list)
async def read_file(read_request:schemas.ReadRequest, db: Session = Depends(get_db)):
    return utils.get_txhash_and_cid_by_user_id(read_request.user_id, db)

@app.post("/api/restore/", response_model=list)
async def restore_files(req: schemas.RestoreRequest, db: Session = Depends(get_db)):
    return utils.restore_user_files(req.user_id, db)

@app.post("/api/chat/")
async def chat_generation_invoke(query_request:schemas.chatRequest):
    return JSONResponse(content={"assistant":utils.rag_chain.invoke(query_request.question)})
