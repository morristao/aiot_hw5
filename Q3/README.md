# HW5 Q3 — AI PowerPoint Redesign

這題實作「原始 PPT → AI 重新設計」，並產出兩種全新風格：

| 版本 | 說明 | 檔案 |
|------|------|------|
|Baseline|原始簡報（白底、預設字型），作為對照組|`output/smart_campus_original.pptx`|
|Pulse Neon|ChatGPT 提供的霓虹霧面色票 + 幾何光暈，強調 AI x 科技展場感|`output/smart_campus_pulse_neon.pptx`|
|Zen Canvas|ChatGPT 規劃的暖色留白、生態素材，走策略簡報 / 咨詢顧問風|`output/smart_campus_zen_canvas.pptx`|

所有 deck 皆由 `python-pptx` 自動生成，可重跑取得一致輸出。

## 專案結構
```
aiot_hw5/Q3
├── data/presentation_outline.json   # 簡報內容（標題、段落、量化 KPI）
├── generate_ppts.py                 # 產生 Baseline / Pulse Neon / Zen Canvas 的腳本
├── output/*.pptx                    # 生成後的 PPT 檔案
├── streamlit_app.py                 # Demo：按鈕產生並下載指定風格的 PPT
├── chat_log.md                      # ChatGPT 對話節錄（色票 / 版面設計建議）
└── README.md
```

## 重新產生 PPT
1. 安裝依賴：`pip install -r aiot_hw5/requirements.txt`
2. 執行腳本：
   ```bash
   python3 aiot_hw5/Q3/generate_ppts.py --style all
   ```
   - 也可改成 `--style pulse_neon` 或 `--style zen_canvas` 只輸出單一風格。
3. 檔案會寫入 `aiot_hw5/Q3/output/`，開啟後即可另存成 PDF 報告。

### Streamlit Demo
```
streamlit run aiot_hw5/Q3/streamlit_app.py
```
- 左右兩欄各代表一種 AI 版型，可線上觸發生成並點擊 Download 取得 PPT。
- 頁面同時列出 slide outline，方便確認內容一致。

## 關於 AI 參與
- `chat_log.md` 紀錄我向 ChatGPT 詢問色彩趨勢、視覺語彙及資訊層級的對話片段。
- 霓虹／禪風兩種設計語氣皆來自該對話：我依回覆產生色票、裝飾圖形與文字階層，`python-pptx` 則依結構化 JSON 重建整份 PPT。
- 不同風格仍共用相同情節（Smart Campus Pilot），以凸顯「AI 重新設計版型」之差異。

## 可交付項目
- **PPT**：兩個 AI 風格 (`pulse_neon`, `zen_canvas`) 以及 baseline 對照。
- **PDF**：使用 PowerPoint / LibreOffice 將上述 PPT 另存為 PDF，供總報告彙整。
- **程式碼 / Workflow**：`generate_ppts.py` + `streamlit_app.py` 同 repo 分享。
- **ChatGPT 對話**：`chat_log.md`。

## 驗證建議
1. 開啟 `smart_campus_original.pptx` vs `smart_campus_pulse_neon.pptx`，可看到背景、色票、圖塊完全不同。
2. 於 Streamlit Demo 中點擊按鈕產生 PPT，核對下載的檔名與 `output/` 目錄一致。
3. 任意調整 `data/presentation_outline.json`（例如加入 slide），重新執行腳本即可同步修改三個版本的 deck。
