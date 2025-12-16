# HW5 Q1 — AI / Human 文章偵測器

這一題實作一個簡化版 AI vs Human 文章分類工具，並且保留原始資料來源連結、模型訓練程式、CLI 與 Streamlit 介面，方便在 GitHub 與 Streamlit Cloud 部署。

## 專案重點
- **資料來源**：HC3 Open QA split（[Hello-SimpleAI/HC3](https://huggingface.co/datasets/Hello-SimpleAI/HC3)）
- **特徵/模型**：TF-IDF (1-2 gram) + Logistic Regression
- **輸出**：`ai_human_detector.joblib`、`metrics.json`、`sample_predictions.csv`
- **UI**：`streamlit_app.py` 可顯示 AI/Human 機率、模型指標、樣本預測
- **對話紀錄**：`chat_log.md`（必要交付，可另行轉成 PDF）

## 目錄結構
```
aiot_hw5/Q1
├── ai_detector/        # dataset + model utils
├── artifacts/          # 模型檔案 (joblib)
├── data/               # raw / processed dataset
├── reports/            # metrics + sample predictions
├── train.py            # 重新訓練入口
├── predict.py          # CLI 推論
├── streamlit_app.py    # Streamlit UI
├── README.md
└── chat_log.md
```

## 快速開始
1. 安裝套件：`pip install -r requirements.txt`
2. 取得資料並訓練：`python3 aiot_hw5/Q1/train.py --limit-per-label 2000`
3. CLI 測試：
   ```bash
   echo "This paragraph sounds like it was written by AI." | python3 aiot_hw5/Q1/predict.py
   ```
4. Streamlit 本機測試：`streamlit run aiot_hw5/Q1/streamlit_app.py`

> `train.py` 會自動下載 open_qa.jsonl、建立平衡資料集、訓練模型並輸出報表。

## Streamlit.app 部署
1. 將整個 repo push 到 GitHub，確保 `aiot_hw5/Q1/artifacts` 及 `aiot_hw5/Q1/reports` 包含最新檔案。
2. 登入 [Streamlit Cloud](https://streamlit.io/cloud)，建立新 App。
3. 選擇此 repo，指向 `aiot_hw5/Q1/streamlit_app.py`。
4. Deploy 完成後，請把正式連結填到這裡：`https://your-streamlit-app-url`

## GitHub 交付
- 本題程式碼皆在 `aiot_hw5/Q1/` 目錄下，直接 push 上 GitHub 即可。

## ChatGPT / Agent 對話紀錄
- 以 Markdown 形式保存於 `aiot_hw5/Q1/chat_log.md`，若需要 PDF 可由此檔另行轉換。

## 延伸方向
- 增加中文字訓練資料（HC3 亦提供 zh split）
- 嘗試 transformers（RoBERTa、DeBERTa 等）或 zero-shot 模型
- 加入可視化（詞雲、SHAP 等）提高可解釋性

