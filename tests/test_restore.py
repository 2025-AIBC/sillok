import sys
import os
from datetime import datetime
import pytest
from fastapi.testclient import TestClient
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
import types

import api.database as api_database
sys.modules["database"] = api_database
import api.models as api_models
sys.modules["models"] = api_models
import api.schemas as api_schemas
sys.modules["schemas"] = api_schemas
models = api_models
dummy_web3 = types.ModuleType('web3')
class DummyWeb3:
    class HTTPProvider:
        def __init__(self, url):
            self.url = url
    class Eth:
        accounts = ["0x0"]
        @staticmethod
        def contract(address=None, abi=None):
            class Funcs:
                @staticmethod
                def storeFileMetadata(*args, **kwargs):
                    class Tx:
                        def transact(self, *a, **k):
                            class TH:
                                def hex(self):
                                    return "0x0"
                            return TH()
            class Contract:
                functions = Funcs()
            return Contract()
    def __init__(self, provider):
        self.eth = self.Eth()
dummy_web3.Web3 = DummyWeb3
sys.modules['web3'] = dummy_web3
import api.utils as api_utils
sys.modules["utils"] = api_utils
import api.main as main
utils = api_utils
from api.database import SessionLocal, engine

client = TestClient(main.app)

class DummyVectorStore:
    def __init__(self):
        self.docs = {}
    def add_documents(self, docs, ids=None):
        for doc_id, doc in zip(ids, docs):
            self.docs[doc_id] = doc
    def delete(self, ids):
        for doc_id in ids:
            self.docs.pop(doc_id, None)
    def as_retriever(self):
        return self

def setup_module(module):
    models.Base.metadata.create_all(bind=engine)


def test_create_delete_restore(monkeypatch):
    dummy_store = DummyVectorStore()
    ipfs_store = {}

    def fake_create_file(file, db):
        cid = "cid123"
        ipfs_store[cid] = {
            "metadata": {
                "fname": file.fname,
                "user_id": file.user_id,
                "last_update": datetime.now().strftime("%Y-%m-%d_%H:%M:%S"),
                "is_deleted": False,
                "raw_content_type": file.type,
            },
            "raw_content": file.content,
            "splits": [file.content],
            "split_ids": [cid + "-0"],
            "vectors": [0.1],
        }
        db_file = models.File(
            CID=cid,
            fname=file.fname,
            type=file.type,
            last_update=datetime.now(),
            is_deleted=False,
            user_id=file.user_id,
            TXHash="tx",
            content=file.content,
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        dummy_store.add_documents([file.content], ids=[cid + "-0"])
        return db_file

    def fake_restore(cid, db):
        data = ipfs_store[cid]
        db_file = models.File(
            CID=cid,
            fname=data["metadata"]["fname"],
            type=data["metadata"]["raw_content_type"],
            last_update=datetime.strptime(data["metadata"]["last_update"], "%Y-%m-%d_%H:%M:%S"),
            is_deleted=False,
            user_id=data["metadata"]["user_id"],
            TXHash="restored",
            content=data["raw_content"],
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        dummy_store.add_documents([data["raw_content"]], ids=data["split_ids"])
        return db_file

    monkeypatch.setattr(utils, "vector_store", dummy_store)
    monkeypatch.setattr(utils, "retriever", dummy_store)
    monkeypatch.setattr(utils, "create_file", fake_create_file)
    monkeypatch.setattr(utils, "restore_file_by_cid", fake_restore)

    # ensure user exists
    with SessionLocal() as db:
        existing = db.query(models.User).filter_by(account="testuser").first()
        if existing:
            uid = existing.user_id
        else:
            user = models.User(name="tester", account="testuser", password="pw", email="t@example.com", birthday=datetime.now(), gender="M")
            db.add(user)
            db.commit()
            uid = user.user_id

    payload = {
        "user_id": uid,
        "fname": "example.md",
        "type": "markdown",
        "content": "# hello"
    }
    resp = client.post("/api/create/", json=payload)
    assert resp.status_code == 200
    cid = resp.json()["CID"]

    with SessionLocal() as db:
        assert db.query(models.File).count() == 1
        db.query(models.File).delete()
        db.commit()
        assert db.query(models.File).count() == 0

    resp = client.post("/api/restore/", json={"cid": cid})
    assert resp.status_code == 200
    with SessionLocal() as db:
        file_row = db.query(models.File).filter_by(CID=cid).first()
        assert file_row is not None
        assert file_row.fname == "example.md"
    assert cid + "-0" in dummy_store.docs
