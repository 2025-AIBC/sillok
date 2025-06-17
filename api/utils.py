import pytz
from datetime import datetime
import uuid
import json
import requests
from io import BytesIO
import numpy as np
from fastapi import HTTPException
from web3 import Web3
from sqlalchemy.orm import Session
import models, schemas
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_postgres.vectorstores import PGVector
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, PromptTemplate
from langchain_core.output_parsers.string import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document
import unicodedata

#####################################################################################
# Langchain setup: VectorStore, TextSplitter, Embeddings, LLM, ChatPrompt
#####################################################################################
connection = "postgresql+psycopg://postgres:4321@postgres_addr:5432/sillok-test"
collection_name = "sillok-test"
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
embeddings = OpenAIEmbeddings(model="text-embedding-3-large") # dim: 3072 for text-embedding-3-large
vector_store = PGVector(
    embeddings=embeddings,
    collection_name=collection_name,
    connection=connection,
    use_jsonb=True,
)
retriever = vector_store.as_retriever()
llm = ChatOpenAI(model="gpt-4.1")

# PromptTemplate 정의
prompt_template = PromptTemplate(
    input_variables=['context', 'question'],
    template=(
        "당신은 질의응답을 돕는 조수입니다."
        "아래의 검색된 맥락을 사용해 질문에 답해주세요."
        "정답을 모르면 모른다고 말해야 합니다."
        "답변은 최대한 한국어로 제공해주세요."
        "답변을 제공하기 이전에 질문에 답하기 위한 논리적 절차를 구성하고 그에 따라 답변을 제공해야 합니다.\n"
        "질문: {question} \n맥락: {context} \nAnswer:"
    )
)

# HumanMessagePromptTemplate 정의
human_message_prompt_template = HumanMessagePromptTemplate(
    prompt=prompt_template
)

# ChatPromptTemplate 정의
custom_chat_template = ChatPromptTemplate(
    input_variables=['context', 'question'],
    messages=[human_message_prompt_template]
)
# 맥락 포맷팅을 위한 함수 정의
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)
# 최종 RAG chain
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | custom_chat_template
    | llm
    | StrOutputParser()
)
#####################################################################################
# IPFS setup
#####################################################################################
IPFS_HOST = "ipfs" # Check `docker-compose.yml`
IPFS_PORT = 5001

#### IPFS + requests 테스트 코드
## 아래 파일 1회 작성해서 올려둬봄.
# with open('example.md', 'rb') as file:
#     response = requests.post(
#         f'http://{IPFS_HOST}:{IPFS_PORT}/api/v0/add',
#         files={'file': file}
#     )
# print(response.json())
## 출력
# cid = "QmV1VCeLMQxgtEo3234KtVukK3maL79syJ9pmXMqXgvbLN"
# response = requests.post(f"http://{IPFS_HOST}:{IPFS_PORT}/api/v0/cat?arg={cid}")
# print(response.content.decode('utf-8'))
####

#####################################################################################
# Blockchain setup
#####################################################################################
ganache_address = "http://ganache_url:8545"
web3 = Web3(Web3.HTTPProvider(ganache_address))

## 빌드 아티팩트 파일 경로
build_artifact_path = "/app/ganache_build/contracts/MetaDataStoreContract.json"

## ABI 및 컨트랙트 주소 로드
with open(build_artifact_path) as f:
    contract_json = json.load(f)
    contract_abi = contract_json["abi"]
    network_id = '1337'  ## Ganache의 네트워크 ID

    ## 컨트랙트 주소 가져오기
    if network_id in contract_json['networks']:
        contract_address = contract_json['networks'][network_id]['address']
    else:
        raise Exception(f"Contract not deployed on network {network_id}")

## Smart contract instance
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

#####################################################################################
# 아래는 FastAPI에서 사용할 함수들을 정의한 부분입니다.
#####################################################################################

def create_user(user: schemas.UserCreate, db: Session):
    # Check the user is already in the Database.
    if (db_user := db.query(models.User).filter(models.User.account == user.account).first()):
        return db_user 
    # Else create the user.
    db_user = models.User(name=user.name, account=user.account, password=user.password, email=user.email, birthday=user.birthday, gender=user.gender)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# TODO: Async로 변경 필요
def create_file(request_data: schemas.FileCreate, db: Session):
    # file: user_id, fname, type, content
    global retriever # global로 일단 구현하고 추후 안정화를 위한 작업을 진행할 예정.
    
    if request_data.type != "markdown":
        # 여기서 리턴하는 유형은 좀 더 생각해야함.. 지금은 일단 raise로 처리.
        raise HTTPException(status_code=400, detail="Only markdown files are supported.")
    
    # # Check the file is already in the Database.
    # if (db_file := db.query(models.File).filter(models.File.CID == file.CID).first()):
    #     return db_file
    
    # 1. file_id 준비
    file_id = uuid.uuid4().hex
    # 2. TextSplitter로 분리
    print("입력 문서를 TextSplitter로 분리하는 중입니다...")
    document = Document(page_content=request_data.content, metadata={"id": file_id})
    splits = text_splitter.split_documents([document])
    # 3. Embedding 및 VectorStore에 저장
    print("분리된 청크를 임베딩하고 벡터 스토어에 저장하는 중입니다...")
    splits_ids = [file_id+"-"+str(i) for i in range(len(splits))]
    vector_store.add_documents(splits, ids=splits_ids)
    retriever = vector_store.as_retriever() # retriever 업데이트
    # 4. Embedding된 벡터들을 가져오기
    embedding_records = (
        db.query(models.LangchainPGEmbedding)
        .filter(models.LangchainPGEmbedding.id.in_(splits_ids))
        .all()
    )
    vectors = [list(record.embedding) for record in embedding_records]
    
    # 5. IPFS에 저장 (with metadata)
    print("데이터를 IPFS에 저장하는 중입니다...")
    metadata = {
        "fname": request_data.fname,
        "user_id": request_data.user_id,
        "last_update": datetime.now(pytz.timezone("Asia/Seoul")).strftime("%Y-%m-%d_%H:%M:%S"),
        "is_deleted": False,
        "raw_content_type": "markdown",
        "embeddings": "text-embedding-3-large",
        "text_splitter": "RecursiveCharacterTextSplitter(Langchain)",
    }
    data_for_IPFS = {
        "metadata": metadata,
        "raw_content": request_data.content,
        "splits": [{"page_content": split.page_content, "metadata": split.metadata} for split in splits],
        "split_ids": splits_ids,
        "vectors": [
            [float(v) if isinstance(v, np.float32) else v for v in vector]
            for vector in vectors
        ],
    }
    json_content = json.dumps(data_for_IPFS)
    file_like_object = BytesIO(json_content.encode('utf-8'))
    file_like_object.name = request_data.fname.split('.')[0] + ".json"
    files = {'file': (file_like_object.name, file_like_object)}
    response = requests.post(f'http://{IPFS_HOST}:{IPFS_PORT}/api/v0/add', files=files)
    result = response.json()
    # print(result) #{'Name': 'example.json', 'Hash': 'QmcjjzgPnUcSkESKCQcfHTcP1C5YBXQUPL462cTkdv4t8A', 'Size': '69284'}
    # 6. 블록체인에 저장
    print("CID와 메타데이터들을 블록체인에 저장합니다.")
    cid = result["Hash"]
    tx_hash = contract.functions.storeFileMetadata(
        cid, # CID
        "json", # fileType
        int(datetime.now().timestamp()), # lastUpdate
        False, # isDeleted
        request_data.user_id # userId
    ).transact({
        'from': web3.eth.accounts[0],
        'gas': 2000000
    })
    print(f"데이터가 TxHash={tx_hash.hex()} 에 저장되었습니다. 이제 원본임을 보장합니다.")
    # 성공!
    # fastapi_app-1  | Data stored with transaction hash: 240080e13d28d6fe20e306bad3a2e9371e17b03f6e367e08665dfe21724b82b8
    # fastapi_app-1  | File created successfully.
    
    # (아래) 추후 검증용 코드
    # receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    # print(f"Data stored with transaction hash: {receipt.transactionHash.hex()}")
    
    # 7. DB에 저장
    db_file = models.File(
        CID=cid,
        fname=request_data.fname, 
        type=request_data.type,
        last_update=metadata["last_update"],
        is_deleted=metadata["is_deleted"],
        user_id=request_data.user_id,
        TXHash=tx_hash,
        content=request_data.content # 빠른 사용을 위해 CID와 병행
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    print("성공적으로 저장했습니다!🎉")
    return db_file

def get_files_by_user_id(user_id:str, db: Session):
    records = db.query(models.File).filter(models.File.user_id.in_([user_id])).all()
    results = []
    for record in records:
        if not record.is_deleted:
            results.append(record.dict())
    return results

def get_txhash_and_cid_by_user_id(user_id:str, db: Session):
    records = db.query(models.File).filter(models.File.user_id.in_([user_id])).all()
    results = []
    for record in records:
        if not record.is_deleted:
            results.append({"CID":record.CID, "fname":record.fname, "TXHash":record.TXHash})
    return results

def delete_file_by_cid(cid:str, db: Session):
    global retriever
    db_file = db.query(models.File).filter(models.File.CID == cid).first()
    if db_file is None:
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")
    response = requests.post(f"http://{IPFS_HOST}:{IPFS_PORT}/api/v0/cat?arg={cid}")
    content = response.json()
    splits_ids = content["split_ids"]
    vector_store.delete(ids=splits_ids)
    retriever = vector_store.as_retriever() # retriever 업데이트
    
    fname = db_file.fname
    db_file.is_deleted = True
    db.commit()
    db.refresh(db_file)
    return fname

def update_file(request_data: schemas.FileUpdate, db: Session):
    file_create_data = request_data.dict(exclude={"CID"})
    delete_file_by_cid(request_data.CID, db)
    return create_file(schemas.FileCreate(**file_create_data), db)

def check_fname_exists(fname:str, db:Session):
    records = db.query(models.File).filter(models.File.fname.in_([fname])).all()
    if len(records) > 0:
        return True
    return False

def check_decodable(text:str):
    enc_text = text.encode("utf-8")
    if unicodedata.normalize('NFC', text) == unicodedata.normalize('NFC', enc_text.decode("utf-8")):
        return True
    return False

def restore_user_files(user_id: str, db: Session):
    """Restore user's files from IPFS into the vector store."""
    global retriever
    records = (
        db.query(models.File)
        .filter(models.File.user_id == user_id, models.File.is_deleted == False)
        .all()
    )

    for record in records:
        response = requests.post(
            f"http://{IPFS_HOST}:{IPFS_PORT}/api/v0/cat?arg={record.CID}"
        )
        content = response.json()
        splits = [
            Document(page_content=s["page_content"], metadata=s["metadata"])
            for s in content.get("splits", [])
        ]
        split_ids = content.get("split_ids", [])
        vectors = content.get("vectors", [])
        if vectors:
            vector_store.add_embeddings(
                texts=[doc.page_content for doc in splits],
                embeddings=vectors,
                metadatas=[doc.metadata for doc in splits],
                ids=split_ids,
            )
        else:
            vector_store.add_documents(splits, ids=split_ids)

    retriever = vector_store.as_retriever()
