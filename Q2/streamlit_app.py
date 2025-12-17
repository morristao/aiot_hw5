"""Streamlit helper app for testing the HW5 Q2 n8n automation workflow."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

import requests
import streamlit as st


SAMPLE_PAYLOAD_PATH = Path(__file__).resolve().parent / "samples" / "sample_payload.json"
DEFAULT_ENDPOINT = "http://localhost:5678/webhook/aiot-hw5-q2-ai-agent"


@st.cache_data(show_spinner=False)
def load_sample_payload() -> Dict[str, Any]:
    if SAMPLE_PAYLOAD_PATH.exists():
        return json.loads(SAMPLE_PAYLOAD_PATH.read_text(encoding="utf-8"))
    return {
        "title": "Podcast 企劃會議紀要",
        "content": "主持人 Amber 會同 BD 討論 S3 EP1 訪談細節，需於 5/20 前產出腳本。",
        "language": "zh",
        "target_language": "en",
        "tone": "專業且溫暖",
        "notify_channel": "webhook",
        "email": "demo@example.com",
        "source": "streamlit-form",
    }


def try_parse_payload(payload_text: str) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(payload_text)
    except json.JSONDecodeError as exc:
        st.error(f"Payload 不是合法 JSON：{exc}")
        return None


def request_webhook(url: str, payload: Dict[str, Any]) -> requests.Response:
    headers = {"Content-Type": "application/json"}
    return requests.post(url, headers=headers, json=payload, timeout=30)


def main() -> None:
    st.set_page_config(page_title="AIOT HW5 Q2 Workflow Demo", layout="wide")
    st.title("AIOT HW5 Q2 — n8n Workflow Demo")
    st.write(
        "這個 Streamlit UI 只是個前端，幫你把 JSON 丟到本地或雲端的 n8n Webhook，"
        "方便錄 Demo 或驗證 workflow 是否運作。"
    )
    st.info(
        "請先啟動 n8n 並匯入 `aiot_hw5/Q2/workflow.json`，確認 Webhook URL "
        "（預設是 `http://localhost:5678/webhook/aiot-hw5-q2-ai-agent`）。"
    )

    with st.expander("如何使用", expanded=False):
        st.markdown(
            """
1. 啟動 n8n，並設定好必要的 API Key / Notion Database ID。
2. 在這個頁面輸入 n8n Webhook URL，或直接用預設的本機端。
3. 依需求修改右側 JSON payload 後按「Send to n8n webhook」。
4. 下方會顯示 n8n 回傳的 summary / action items / Notion page id 等結果。
5. 執行過程可截圖或錄影，符合 HW5 Q2 的 Demo 要求。
            """
        )

    col_endpoint, col_payload = st.columns([1.2, 1.8])

    with col_endpoint:
        endpoint = st.text_input("n8n Webhook URL", value=DEFAULT_ENDPOINT)
        st.caption("若部署在雲端，將主機名稱換成你的 n8n domain 即可。")

        st.divider()
        st.markdown("**快速複製的 curl 指令**")
        st.code(
            f"curl -X POST {endpoint} \\\n"
            "  -H 'Content-Type: application/json' \\\n"
            "  -d @aiot_hw5/Q2/samples/sample_payload.json",
            language="bash",
        )

    with col_payload:
        sample_payload = load_sample_payload()
        payload_text = st.text_area(
            "Webhook JSON payload",
            value=json.dumps(sample_payload, ensure_ascii=False, indent=2),
            height=320,
        )

        if st.button("Send to n8n webhook", type="primary"):
            payload_obj = try_parse_payload(payload_text)
            if payload_obj is None:
                st.stop()

            with st.spinner("呼叫 n8n 中..."):
                try:
                    response = request_webhook(endpoint.strip(), payload_obj)
                    st.success(f"HTTP {response.status_code}")
                    try:
                        st.json(response.json())
                    except ValueError:
                        st.write(response.text)
                except requests.RequestException as exc:
                    st.error(f"無法連線到 webhook：{exc}")

    st.divider()
    st.write(
        "📄 相關文件：`aiot_hw5/Q2/README.md`（部署、測試與 Demo 步驟）與 "
        "`aiot_hw5/Q2/chat_log.md`（ChatGPT 對話紀錄）。"
    )


if __name__ == "__main__":
    main()
