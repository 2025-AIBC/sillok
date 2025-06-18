# TODO
# 0. IPFS와 Blockchian 연동 및 이를 활용하는 로직과 LLM은 FastAPI main.py파일 참고
# 1. 해당 로직으로 Verify되면 결과를 보여주는 함수 기능 추가
# 2. Verify된 결과를 공유하는 기능 추가
import re
import time
from copy import deepcopy
import gradio as gr
import requests
from bs4 import BeautifulSoup

import threading
import os

DEFAULT_STATUS_DATA = {
    "status": "New file",
    "title": "N/A",
    "last_update": "N/A",
    "cid": "N/A",
    "txhash": "N/A"
}

# FASTAPI_SERVER = "http://fastapi_url:8000/api"
FASTAPI_SERVER = os.getenv("FASTAPI_SERVER", "http://fastapi_url:8000/api")
USER_ID = None
USER_FILES = None
FILE_STATUS_HTML = """
<div>
<p><strong>Status</strong>: {status}</p>
<p><strong>Title</strong>: {title}</p>
<p><strong>Last Update</strong>: {last_update}</p>
<p><strong>CID</strong>: {cid}</p>
<p><strong>TXHash</strong>: {txhash}</p>
</div>
"""
DEFAULT_STATUS_DATA = {
    "status": "New file",
    "title": "N/A",
    "last_update": "N/A",
    "cid": "N/A",
    "txhash": "N/A"
}
#####################################################################################
# Utility Functions
#####################################################################################
def extract_title(markdown_content):
    # 특수 문자를 언더바(_)로 대체하고, 마침표 제거하는 함수
    def clean_text(text):
        text = re.sub(r'[^\w\s]', '_', text)  # 특수 문자는 언더바로 대체
        return text.replace('.', '')  # 마침표 제거

    # #으로 시작하는 가장 처음 등장하는 문장 찾기
    for line in markdown_content.splitlines():
        if line.startswith('#'):
            title = line.strip('#').strip()  # '#' 제거 후 양쪽 공백 제거
            return clean_text(title)

    # 만약 #으로 시작하는 문장이 없다면, 첫 번째 문장 사용
    first_sentence = markdown_content.splitlines()[0]
    words = first_sentence.split()[:5]  # 최대 5개의 단어 선택
    title = ' '.join(words)

    return clean_text(title)    

def custom_chat(user_query, _):
    # 실시간 스트림으로 받으려고 했으나, 스트림으로 수신하는 유니코드를 디코딩하는 과정에서 한글의 복잡성(?)으로 처리가 어려움.
    # 따라서, 그냥 invoke로 좀 늦더라도 받아오고, 그 다음 애니메이션으로 동작하도록 구현.
    chat_data = {"question": user_query}
    response = requests.post(f"{FASTAPI_SERVER}/chat/", json=chat_data)
    answer = ""
    answer += "[🤖Sillok AI]\n\n"
    for word in response.json()["assistant"]:
        time.sleep(0.01)
        answer += word
        yield answer

def read_cid(cid):
    # IPFS API 대신 HTTP 게이트웨이 사용
    # 컨테이너가 8080 포트를 노출했다면:
    IPFS_GATEWAY = "http://ipfs:8080/ipfs"
    resp = requests.get(f"{IPFS_GATEWAY}/{cid}")
    if resp.status_code != 200:
        raise requests.HTTPError(f"Failed to fetch {cid}: {resp.status_code} {resp.text}")
    # text = resp.text
    text = resp.json().get("raw_content", "")

    # JSON 형태로 메타/원본을 묶어 반환하는 구조였다면 그대로,
    # 아니면 단순히 plain text라면
    return {
        "raw_content": text,
        "metadata": {
            "last_update": "—",   # 만약 IPFS에 metadata가 별도로 있다면 parsing
            "is_deleted": False
        }
    }    
    
    # # FastAPI 거치면 느려지니까.. 발표자료에는 FastAPI 건너는거로 그리긴했는데 실제로는 이렇게 direct하게 구현했음.
    # IPFS_HOST = "ipfs" # Check `docker-compose.yml`
    # IPFS_PORT = 5001
    # response = requests.get(
    #     f"http://{IPFS_HOST}:{IPFS_PORT}/api/v0/cat?arg={cid}"
    # )
    # if not response.ok:
    #     raise requests.HTTPError(
    #         f"Failed to fetch {cid}: {response.status_code} {response.text}"
    #     )
    # content = response.json()
    # print(content)
    # # content에 저장된 내용
    # # - meatadata:{fname, user_id, last_update, is_deleted, raw_content_type, embeddings, text_splitter}
    # # - raw_content: 텍스트 내용
    # return content

def parse_html_to_dict(html):
    soup = BeautifulSoup(html, 'html.parser')
    file_status_data = {}
    for p_tag in soup.find_all('p'):
        key = p_tag.find('strong').text.lower()  # strong 태그의 텍스트를 키로 사용
        value = p_tag.text.split(": ")[1]  # : 이후의 값을 추출
        file_status_data[key] = value
    return file_status_data

def clear_text_and_status():
    print(DEFAULT_STATUS_DATA)
    return [gr.Textbox(value=""), gr.HTML(FILE_STATUS_HTML.format(**DEFAULT_STATUS_DATA))]
#####################################################################################
# API-based Functions
#####################################################################################
def authenticate_user(user_id: str, user_pw: str):  
    global USER_ID # SHA3 value for each user.
    user_account = user_id
    auth_data = {"user_id": user_account, "user_pw": user_pw}
    response = requests.post(f"{FASTAPI_SERVER}/auth/", json=auth_data)
    if response.status_code == 200:
        USER_ID = response.json()["user_id"]
        return True
    else:
        print(f"요청 실패: {response.status_code}, 메시지: {response.text}")
        return False

def save_markdown(user_text, file_status_html):
    global USER_ID
    file_status_data = parse_html_to_dict(file_status_html)

    if user_text == "":
        gr.Info("🤔 저장할 내용이 없습니다.")
        return [user_text, gr.HTML(FILE_STATUS_HTML.format(**file_status_data))]

    fname = extract_title(user_text)

    url = FASTAPI_SERVER + "/create/"
    payload = {
        "user_id": USER_ID,
        "fname": fname,
        "type": "markdown",
        "content": user_text
    }
    if file_status_data["cid"] != "N/A":
        payload["CID"] = file_status_data["cid"]
        url = FASTAPI_SERVER + "/update/"

    response = requests.post(url, json=payload)
    if response.status_code == 200:
        data = response.json()
        tx = data["TXHash"]
        cid = data["CID"]
        fname = data["fname"]
        last_update = data["last_update"]

        # 화면에 보여줄 상태 업데이트
        file_status_data = {
            "status": "Saved file",
            "title": fname,
            "last_update": last_update,
            "cid": cid,
            "txhash": tx
        }

        gr.Info(f"✅ 저장 완료! TxHash: {response.json().get('TXHash', 'N/A')}")
        user_text = ""
    else:
        gr.Info(f"❌ 저장 실패: {response.text}")

    return [user_text, gr.HTML(FILE_STATUS_HTML.format(**file_status_data))]
    

def delete_file_by_cid(cid):
    cid_data = {"cid": cid}
    response = requests.post(f"{FASTAPI_SERVER}/delete_file/", json=cid_data)
    if response.status_code == 200:
        response_data = response.json()
        gr.Info(f"✅ 파일을 성공적으로 삭제했습니다.\n파일명:{response_data["fname"]}\n파일CID:{response_data["CID"]}")
    else:
        gr.Info(f"❌ 파일을 삭제하지 못했습니다.\n\n에러메세지:\n{response.text}")

def get_user_files():
    global USER_ID
    response = requests.post(f"{FASTAPI_SERVER}/read_by_user_id/", json={"user_id": USER_ID})
    results = response.json()
    return results

def update_markdown_list():
    global USER_FILES
    USER_FILES = get_user_files()
    updated_user_file_list = [user_file["fname"] for user_file in USER_FILES]
    return gr.Dropdown(updated_user_file_list, label="📝 선택", value="", interactive=True)

def replace_text_to_selected_file(selected_file):
    global USER_FILES # CID, fname, TXHash
    file_status_data = deepcopy(DEFAULT_STATUS_DATA)
    for user_file in  USER_FILES:
        # 지금의 구현으로는 마크다운 제목이 겹치면 첫번째 파일만 불러오게 구현됨. 추후 수정 필요.
        if user_file['fname'] == selected_file:
            content = read_cid(user_file["CID"])
            replace_value = content["raw_content"]
            file_status_data["status"] = "Saved file"
            file_status_data["title"] = user_file["fname"]
            file_status_data["last_update"] = content["metadata"]["last_update"]
            file_status_data["cid"] = user_file["CID"]
            file_status_data["txhash"] = user_file["TXHash"]
            break
        else:
            content = "Not Found"
    return [gr.Textbox(lines=25, max_lines=30, label="# Plain Text", value=replace_value), gr.HTML(FILE_STATUS_HTML.format(**file_status_data))]

def delete_selected_file(selected_file):
    global USER_FILES # CID, fname, TXHash
    file_status_data = deepcopy(DEFAULT_STATUS_DATA)
    if USER_FILES != None:
        for user_file in  USER_FILES:
            # 지금의 구현으로는 마크다운 제목이 겹치면 첫번째 파일만 불러오게 구현됨. 추후 수정 필요.
            if user_file['fname'] == selected_file:
                delete_file_by_cid(user_file["CID"])
            else:
                gr.Info("ERROR: 파일명이 잘못되었습니다.")
    return [gr.Dropdown([""], label="📝 선택", value="", interactive=True), gr.HTML(FILE_STATUS_HTML.format(**file_status_data))]

# 체인 상태를 가져오는 함수
def fetch_chain_status():
    try:
        r = requests.get(f"{FASTAPI_SERVER}/chain_status/")
        r.raise_for_status()
        data = r.json()
        return f"🌐 체인 ID: {data['chainId']} · ⛓ 최신 블록: {data['latestBlock']}"
    except:
        return "⚠️ 체인 상태를 가져올 수 없습니다"
#####################################################################################
# User Interface
#####################################################################################
with gr.Blocks() as demo:
    chain_status = gr.HTML(fetch_chain_status(), label="체인 상태")
    refresh_btn = gr.Button("🔄 상태 갱신")
    refresh_btn.click(lambda: fetch_chain_status(), outputs=chain_status)
    
    
    user_text = gr.State(value="")
    user_file_list = [""]
    gr.Markdown("# 📝 Sillok")

    # gr.HTML(MM_STATUS_HTML) # 페이지 로드 직후 MetaMask 상태 표시
    gr.Markdown("[🌐 Connect 🌎 WorldLand and 🦊Metamask ](http://127.0.0.1:8081/)")
    
    # Web UI 링크 버튼 추가
    with gr.Row():
        # 연결 확인 버튼 & 결과 표시용 텍스트박스
        check_btn = gr.Button("🔌 연결 상태 확인")
        conn_status = gr.Textbox(label="연결 상태", interactive=False)    

        def check_connection():
            r = requests.get(f"{FASTAPI_SERVER}/eth_accounts")
            addrs = r.json().get("accounts", [])
            if addrs:
                return f"✅ 연결됨: {addrs[0]}"
            else:
                return "❌ 연결되지 않음"

        check_btn.click(fn=check_connection, inputs=None, outputs=conn_status)
            
    with gr.Row():
        with gr.Column(scale=3):
            with gr.Tab("Text", id="text") as text_tab:
                with gr.Row():
                    user_text = gr.Textbox(
                        lines=25,
                        max_lines=30,
                        label="# Plain Text"
                    )
                with gr.Row():
                    clear_btn = gr.Button("🗑️ Clear", scale=1)
                    # TODO: 이 verify의 역할을 다시 생각. 지금 쓴 노트의 검증?? 필요없으면 그냥 삭제할 예정
                    save_btn = gr.Button("✅ Save", scale=1)
                file_status = gr.HTML(FILE_STATUS_HTML.format(**DEFAULT_STATUS_DATA))
                # TODO: 기능에 맞는 함수로 수정 필요
                clear_btn.click(clear_text_and_status, outputs=[user_text, file_status])
                # verify_btn.click(lambda: gr.Textbox(value=""), None, user_text)
                save_btn.click(save_markdown, inputs=[user_text, file_status], outputs=[user_text, file_status])
            with gr.Tab("Markdown", id="markdown") as markdown_tab:
                markdown_output = gr.Markdown(
                    latex_delimiters=[{"left":"$$", "right":"$$"}],
                )
                # gr.Textbox.update(source=user_text, outputs=markdown_output) #추가 작동안되면 제거
            # [TODO]: Live Editor 탭 추가
            
            markdown_tab.select(
                fn=lambda text: text,
                inputs=[user_text],
                outputs=[markdown_output]
            )

        with gr.Column(scale=1):
            # TODO: ChatInterface에 맞는 함수로 수정 및 기타 세부 설정 필요
            foo = gr.ChatInterface(
                fn=custom_chat,
                title="🤖 Sillok Bot",
                # placeholder="Ask anything about your notes..."
                # multimodal=True
            )
            # 여기 하다가 말았음. 상황 보고 수정 필요. // 조회 기능 개발 중 => 이후 RAG 기능 추가하면 일단락..
            with gr.Accordion("📑 마크다운 목록", open=True):
                markdown_list = gr.Dropdown(user_file_list, label="📝 선택", value=user_file_list[0], interactive=True)
                markdown_list.focus(update_markdown_list, outputs=markdown_list)
                # markdown_list.select(replace_text_to_selected_file, inputs=markdown_list, outputs=user_text)
                with gr.Column():
                    load_btn = gr.Button("📤 Load", scale=1)
                    del_btn = gr.Button("❌ Delete", scale=1)
                    load_btn.click(replace_text_to_selected_file, inputs=markdown_list, outputs=[user_text, file_status])
                    del_btn.click(delete_selected_file, inputs=markdown_list, outputs=[markdown_list, file_status])
if __name__ == "__main__":
    # Sever name 0.0.0.0 인 것이 중요. Container 내부에서 이렇게 설정해야 외부 로컬 브라우저에서 정상 동작.
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        auth=authenticate_user
    )
