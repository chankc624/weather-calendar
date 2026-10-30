# Repository instructions

適用於整個 weather-calendar repository。詳細操作見 README.md 及 docs/MAINTENANCE.md。

## 目錄用途

- index.html：主 dashboard；HTML、CSS、JavaScript 及 CFG 設定放在同一檔。
- v2/index.html：獨立版本；不會繼承主頁設定，不要假設兩版行為相同。
- fetch_smg.py：以 Python 標準函式庫讀取 SMG XML／RSS，產生 smg_warnings.json。
- smg_warnings.json：自動產物；不要手改或把測試資料提交到正式快照。
- test_smg_xml.py、test-warning.html：XML 診斷／顯示規則斷言、瀏覽器模擬警告。
- .github/workflows/：SMG 每 15 分鐘更新及手動 XML 診斷；docs/：維護文件。
- Kindle 功能已移除；除非使用者要求，勿重新加入。

## 開發與測試

由 repo 根目錄執行；Python 工作流程使用 3.12。沒有 npm 建置、套件安裝或既定 lint 指令。

- 本機預覽：`python3 -m http.server 8000 --bind 127.0.0.1`；開啟 /、/v2/ 或 /test-warning.html。
- Python 語法：`python3 -m py_compile fetch_smg.py test_smg_xml.py`。
- 離線規則測試：`python3 -c "import test_smg_xml as t; t.test_display_rules()"`。
- 連線診斷：`python3 test_smg_xml.py`；需網絡，會捕捉連線錯誤，不能只憑 exit code 判定來源正常。它不涵蓋正式 fetch_smg.py 的完整時效規則。
- 更新快照：`python3 fetch_smg.py`；需網絡並覆寫 JSON，僅在需要驗證資料擷取時執行。
- 修改網頁時以瀏覽器檢查受影響入口、橫向／窄螢幕、日曆完整性及 console 錯誤；警告變更另查模擬顯示／隱藏、過期及 unknown 情況。
- 文件修改只檢查內容、路徑及連結；不要為此觸發正式資料更新。

## 程式慣例

- 保留繁體中文介面、Asia/Macau 時區及澳門座標；變更地區須一起檢查固定 UTC+8 日期邏輯及 API 參數。
- 沿用所在區塊格式；Python 用四空格及 snake_case。避免無關重排或引入框架、依賴。
- 動態文字優先用 textContent；使用 innerHTML 時須跳脫不可信文字。網絡請求保留逾時及失敗處理。
- 保留 active／inactive／unknown 的區別、來源與時效核實；不可將 unknown、請求失敗或隱藏警告解讀為安全。RSS 標題不等於核實生效警告。
- 主頁 APP_VERSION 與 dashboard-version 必須一致；需要長開頁面自動更新時同步遞增。
- 主頁與 v2 的相對 JSON 路徑不同；修改其中一版時核對另一版是否受影響。
- 不提交密鑰、額外私人資料、__pycache__、虛擬環境或測試產物。

## 完成標準

- 只包含任務相關變更；檢查 diff，保留其他人的及排程產生的更新。
- 按變更範圍完成上述驗證；修改警告邏輯時補充能覆蓋實際行為的離線測試。
- 行為或操作改變時同步更新 README.md／docs/MAINTENANCE.md。
- 回報改動、實際執行的檢查結果，以及未執行項目與原因；未執行的檢查不可聲稱通過。
- 開始任務時列出實際讀取的指示檔及範圍；若只經 GitHub 工具讀取，明確標示手動讀取，不聲稱已由本機 Codex 自動載入。

依據 OpenAI 官方說明：https://developers.openai.com/codex/guides/agents-md
