"""Streamlit UI for the AI vs Human detector."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from ai_detector.paths import METRICS_PATH, MODEL_PATH, SAMPLES_PATH
from ai_detector.predictor import load_metrics, predict_text

st.set_page_config(
    page_title="AI vs Human Detector",
    page_icon="🤖",
    layout="wide",
)

st.title("HW5 Q1 — AI vs Human 文章偵測器")
st.caption(
    "輸入任意段文字，即時判斷其為 AI 所寫或人工撰寫。"
    " 模型使用 HC3 open_qa 資料集並以 TF-IDF + Logistic Regression 訓練而成。"
)

model_ready = Path(MODEL_PATH).exists()
if not model_ready:
    st.error(
        "找不到模型檔案。請先在本機執行 `python3 aiot_hw5/Q1/train.py` 產生模型與報表。"
    )
    st.stop()

with st.container():
    st.subheader("Step 1 — 貼上要檢測的文章")
    default_text = (
        "Artificial intelligence systems excel at producing polished paragraphs "
        "with balanced structure, but often reuse patterns and lack personal anecdotes."
    )
    text = st.text_area(
        "文字輸入",
        value=default_text,
        height=200,
        help="支援中英文或混合內容，建議至少 2 句以上能更準確。",
    )
    analyze = st.button("分析這段文字", type="primary", use_container_width=True)

    if analyze:
        try:
            result = predict_text(text)
        except ValueError as exc:
            st.warning(str(exc))
        else:
            ai_pct = result["ai_probability"] * 100
            human_pct = result["human_probability"] * 100
            label = "AI 生成" if result["label"] == "ai" else "Human 撰寫"
            st.metric("判斷結果", label)
            cols = st.columns(2)
            cols[0].progress(min(max(ai_pct / 100, 0.0), 1.0), text=f"AI: {ai_pct:.2f}%")
            cols[1].progress(
                min(max(human_pct / 100, 0.0), 1.0), text=f"Human: {human_pct:.2f}%"
            )
            st.json(result, expanded=False)

st.divider()
st.subheader("Step 2 — 模型與資料統計")

metrics_payload = load_metrics()
if metrics_payload:
    summary = metrics_payload.get("summary", {})
    cols = st.columns(len(summary) or 1)
    for idx, (name, value) in enumerate(summary.items()):
        cols[idx].metric(name.replace("_", " ").title(), value)
else:
    st.info("尚未找到 metrics.json，可重新訓練模型產生。")


@st.cache_data
def load_samples(limit: int = 5) -> pd.DataFrame | None:
    path = Path(SAMPLES_PATH)
    if not path.exists():
        return None
    df = pd.read_csv(path)
    return df.head(limit)


samples_df = load_samples()
if samples_df is not None and not samples_df.empty:
    st.dataframe(samples_df, use_container_width=True, hide_index=True)
else:
    st.info("尚未生成 sample_predictions.csv。")

st.divider()
with st.expander("如何部署到 Streamlit Cloud？", expanded=False):
    st.markdown(
        """
1. `pip install -r requirements.txt`
2. `python3 aiot_hw5/Q1/train.py` 產出模型與 metrics。
3. 本機測試：`streamlit run aiot_hw5/Q1/streamlit_app.py`
4. 部署前請將 `aiot_hw5/Q1/artifacts` 與 `aiot_hw5/Q1/reports` 同步到 GitHub。
5. 前往 [streamlit.io](https://streamlit.io/cloud) → 使用此 repo 建立應用並設定主程式：`aiot_hw5/Q1/streamlit_app.py`
        """
    )
