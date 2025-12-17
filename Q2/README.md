# HW5 Q2 — n8n AI Workflow（仿小林 AI）

這份 workflow 以 n8n 實作一條可運行的 AI 自動化流程：接收外部表單／Webhook、呼叫 OpenAI 進行多語摘要與翻譯、產生 AI 回覆、將結果寫回 Notion 並回傳 JSON，可作為小林 AI workflow 的精簡版。

## 功能重點
- **Webhook + Manual Trigger**：可用外部 HTTP POST 或 n8n 內建 Manual Trigger 測試，`Manual Trigger → Sample Payload` 內建 Sample 資料。
- **OpenAI 雙階段推論**：
  1. `Summarize & Translate (OpenAI)` 產出摘要、重點、TODO、Hashtag 與指定語言翻譯。
  2. `Compose Reply (OpenAI)` 依摘要/代辦與語氣產生 AI 回覆、主旨與英文 microcopy。
- **筆記整理**：`Build Notion Payload → Create Notion Page` 將摘要、翻譯、待辦項目寫入 Notion Database（含 to-do blocks）。
- **Webhook 回傳**：`Respond to Webhook` 回傳整包 JSON（summary、action_items、ai_reply、notion_page_id 等），也可串接其他 app（Slack、Line、自家後端）。

## 節點流程
| # | Node | 類型 | 說明 |
|---|------|------|------|
|1|Manual Trigger|manualTrigger|n8n 內建手動執行，配合下一個 Sample Payload 測試。|
|2|Sample Payload|set|提供預設測試內容，可快速驗證 workflow。|
|3|AIOT HW5 Q2 Webhook|webhook|對外入口，Path `aiot-hw5-q2-ai-agent`，回應 `Respond to Webhook`。|
|4|Prepare Input|function|統一欄位（title/content/language/...），也處理 webhook body。|
|5|Summarize & Translate (OpenAI)|httpRequest|呼叫 OpenAI Chat Completions，要求輸出 JSON (summary/action_items/translation/hashtags/key_points/tone)。|
|6|Parse Summary|function|解析 OpenAI JSON，補上 summary/translation/action_items 等欄位。|
|7|Compose Reply (OpenAI)|httpRequest|再次呼叫 OpenAI，生成 AI 回覆、subject、microcopy。|
|8|Extract Reply|function|解析回覆 JSON。|
|9|Build Notion Payload|function|組出 Notion Page payload（to-do blocks、translation 段落、標籤）。|
|10|Create Notion Page|httpRequest|POST 到 `https://api.notion.com/v1/pages`，寫入資料庫。|
|11|Assemble Response|function|整理要回傳給 webhook 的欄位。|
|12|Respond to Webhook|respondToWebhook|HTTP Response（JSON）。|

## 安裝與環境變數
1. 安裝/啟動 n8n：可用 Docker 或 npx（版本 ≥ 1.49）。
2. 設定以下環境變數（.env / Docker compose）：
   - `OPENAI_API_KEY`：OpenAI key。
   - `NOTION_API_KEY`：整合 Notion 時使用（若只想測試前半段，可留空，Notion 節點會 `ignoreResponseCode`）。
   - `NOTION_DATABASE_ID`：Notion database id，`Build Notion Payload` 預設讀取 `process.env.NOTION_DATABASE_ID`，沒設定會寫 `YOUR_NOTION_DATABASE_ID` placeholder。
3. 重新啟動 n8n，讓 env 生效。

## 匯入 / 部署
1. 進入 n8n Editor UI → `Workflows → Import from File`。
2. 選擇 repo 中的 `aiot_hw5/Q2/workflow.json`。
3. (可選) 在 `Sample Payload` 節點調整測試內容。
4. 在 `Create Notion Page` 節點設定好 Notion Credentials（若用 env key，保持 `None` 即可，n8n 會直接帶 `Authorization` header）。
5. 儲存 workflow，若要常駐運行可按 `Activate`。

## 測試方式
### Manual Trigger 動畫
1. 於 n8n 編輯器點選 `Execute Workflow`。
2. 觀察 `Summarize & Translate → Compose Reply → Create Notion Page → Respond` 各節點輸出（可錄製螢幕作為 Demo）。

### Webhook 測試 (curl)
假設 n8n host 在本機 5678 port，webhook URL 為 `http://localhost:5678/webhook/aiot-hw5-q2-ai-agent`：
```bash
curl -X POST \
  http://localhost:5678/webhook/aiot-hw5-q2-ai-agent \
  -H 'Content-Type: application/json' \
  -d @aiot_hw5/Q2/samples/sample_payload.json
```
成功時會得到：
```json
{
  "title": "Podcast 企劃會議紀要",
  "summary": "...",
  "action_items": ["撰寫腳本..."],
  "translation": "...",  
  "ai_reply": "...",
  "notion_page_id": "...",
  "subject_line": "...",
  "microcopy": "..."
}
```

## Demo / 截圖建議
- 在 n8n 畫面同時展開 `Summarize`, `Compose Reply`, `Create Notion Page`, `Respond` 四個節點，截圖成功執行狀態即可。（或錄 Loom/OBS，把 Manual Trigger→Webhook→Notion 結果走一遍。）
- Notion 端可截下一筆新建 page（含 to-do block + translation）作證據。

## Streamlit Demo
這題同樣需要提供可運作的 Streamlit 頁面，repo 內已附上簡單前端：

```
streamlit run aiot_hw5/Q2/streamlit_app.py
```

功能說明：
- 左側輸入 n8n Webhook URL（預設 `http://localhost:5678/webhook/aiot-hw5-q2-ai-agent`）
- 右側可編輯 JSON payload，或直接帶 `samples/sample_payload.json` 的內容
- 按下「Send to n8n webhook」後會顯示 HTTP status 與 n8n 回傳 JSON
- 頁面底部附上 README / chat log 連結，可一併錄影當作 Demo

若部署到 Streamlit Cloud，記得在 UI 上把 Webhook URL 指到對外可達的 n8n domain。

## 交付清單 / GitHub 要點
- **ChatGPT / Agent 對話紀錄**：`aiot_hw5/Q2/chat_log.md`（可視需要轉成 PDF 並附在報告）。  
- **GitHub**：整個 `aiot_hw5/Q2/` 目錄需 push 到 GitHub repository；若有額外截圖/影片可放在 releases 或 PR 描述。  
- **Streamlit Demo**：`aiot_hw5/Q2/streamlit_app.py` 可直接部署於 Streamlit Cloud，請在作業繳交時提供實際網址。  
- 推薦在 README 再補上你個人的 Streamlit 連結與任何 Demo 影片，方便助教驗收。

## 檔案說明
- `workflow.json`：可直接匯入的 n8n workflow。
- `samples/sample_payload.json`：Webhook 測試用 payload。
- `streamlit_app.py`：串接 n8n webhook 的 Streamlit 介面，可本機或雲端部署。
- `chat_log.md`：本題與 ChatGPT / Agent 的開發對話紀錄。

> 參考資料：<https://github.com/soluckysummer/n8n_workflows>、<https://www.youtube.com/watch?v=aXocGiEx-qc>
