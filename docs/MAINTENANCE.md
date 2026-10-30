# 維護說明

返回 [README](../README.md)。

## 個人化主頁

編輯根目錄 `index.html` 的 `CFG`：

| 欄位 | 用途 |
| --- | --- |
| `timezone` | 顯示時區，目前 `Asia/Macau` |
| `photos` | 相片網址陣列 |
| `photoFocus` | 各相片裁切焦點，例如 `'50% 50%'`；依相片次序排列 |
| `photoInterval` | 輪播間隔，單位毫秒 |
| `weatherInterval` | 天氣更新間隔，單位毫秒 |
| `annualEvents` | 每年重複的重要日子，日期欄位 `monthDay: 'MM-DD'` |
| `familyAgenda` | 家庭行程，日期欄位 `date: 'YYYY-MM-DD'` |
| `specialDays` | 單次重要日子，日期欄位 `date: 'YYYY-MM-DD'` |

新增活動時沿用現有物件格式，例如：

```js
{monthDay:'12-01',name:'家庭紀念日',region:'家'}
{date:'2026-12-20',name:'家庭活動',region:'家'}
```

`familyAgenda` 目前只列出未來 7 日內最多兩項行程。更改城市時，除了時區，亦要檢查天氣 URL 的座標、API 時區、畫面地名及日期函式內固定的 UTC+8；單改 `CFG.timezone` 並不足夠。

`v2/index.html` 和 `generate_kindle.py` 不會自動繼承主頁設定。Kindle 的地名、家庭文字、生日及天氣座標在 Python 檔內分開設定。

## 主頁版本更新

根目錄 `index.html` 內的以下兩個版本值必須一致，並在需要讓長開頁面自動載入新版本時一起更新：

- `<meta name="dashboard-version" content="…">`
- `const APP_VERSION='…';`

版本檢查讀取同目錄 `index.html`，只有版本變動才重新載入。修改後先在本機預覽，確認相片、日期、日曆及側欄排版，再提交。

## 本機產生資料

### SMG 警告快照

只需 Python 標準函式庫；由 repository 根目錄執行：

```sh
python3 fetch_smg.py
```

這會覆寫 `smg_warnings.json`，並嘗試連接六個 XML 來源及 RSS。個別來源失敗會記錄為 `unknown`，不應解讀為沒有警告。

目前 XML 的 `Status=1` 只有在 `IssuedAt` 可解析、且發佈時間在過去 48 小時內時才列為 `active`；`0/2/3` 列為 `inactive`，其餘為 `unknown`。48 小時是程式的暫時核實窗口，較舊而仍生效的官方警告可能被隱藏。

主頁另要求快照 `checked_at` 不超過 45 分鐘，且不可超前超過 5 分鐘，並要求 `display_warnings=true` 及有效的 `active_warnings`。

### Kindle 圖片

工作流程使用 Python 3.12、Pillow 及 Noto CJK 字型。Ubuntu／Debian 本機可用：

```sh
sudo apt-get update
sudo apt-get install -y fonts-noto-cjk
python3 -m venv .venv
. .venv/bin/activate
python -m pip install 'Pillow>=10,<13'
python generate_kindle.py
```

輸出為 `kindle/dashboard.png`。程式會查找 Linux Noto CJK 字型路徑；其他系統需安裝字型並調整 `FONT_PATHS`／`FONT_BOLD`。缺少中文字型可能令文字無法正常顯示。天氣請求失敗或資料時間相差超過 3 小時時，圖片會顯示資料不可用；圖片成功產生不代表天氣成功取得。

## GitHub Actions

到 repository 的 **Actions**，選工作流程，再按 **Run workflow** 可手動執行：

| 名稱 | 檔案 | 排程／用途 |
| --- | --- | --- |
| Update Macau SMG warnings | [update-smg.yml](../.github/workflows/update-smg.yml) | 每 15 分鐘更新快照 |
| Update Kindle Dashboard | [update-kindle.yml](../.github/workflows/update-kindle.yml) | 每小時產生圖片 |
| Test SMG XML | [test-smg-xml.yml](../.github/workflows/test-smg-xml.yml) | 只供手動 XML 診斷 |

兩個更新工作流程需要 `contents: write`，只在輸出有改變時提交。現有流程不需要自訂 API key 或 secret。兩者會推送至 `main`；修改分支策略時也要檢查 workflow。

## 靜態網站部署

本專案可用靜態 HTTP 主機提供服務。若使用 GitHub Pages，可在 **Settings → Pages** 檢查／設定由 `main` 的根目錄部署；本文不代表目前已啟用 Pages。

部署時保留 `index.html`、`v2/`、`smg_warnings.json` 及 `kindle/` 的相對路徑。主頁讀取 `./smg_warnings.json`，另一版讀取 `../smg_warnings.json`。Kindle 的定時下載或裝置端顯示需另行設定；repository 目前只負責產生圖片。

## 驗證及故障排查

- **警告顯示測試**：本機開啟 `/test-warning.html`，用兩個按鈕驗證模擬警告顯示／隱藏。這不是正式 XML 端到端測試。
- **XML 診斷**：執行 `python3 test_smg_xml.py`。前段有顯示規則斷言，後段連接官方來源並列印結果；連線錯誤會被捕捉，所以退出成功不代表所有來源可用，也不代表已驗證真實生效樣本。
- **天氣未更新**：檢查瀏覽器網絡及 Open-Meteo 回應；主頁請求逾時為 12 秒。
- **沒有警告區塊**：先查官方資訊，再查看快照時間、`warnings` 的 `state`／`reason` 及 Actions 日誌；不可單憑隱藏狀態判斷安全。
- **自動檔案停更**：查看 Actions 是否啟用、排程執行記錄、寫入權限及推送錯誤。SMG 和 Kindle 分別使用不同 concurrency group，若推送碰撞失敗，可檢查後重跑失敗流程。
- **相片空白或裁切不對**：檢查外部圖片網址及 `photoFocus`。
- **頁面仍是舊版**：確認兩個版本值一致，再重新整理或使用新版本查詢參數；中介快取可能影響更新。
- **另一版行為不同**：`v2/` 天氣及警告每 15 分鐘刷新，警告快照新鮮度窗口為 2 小時；設定與主頁獨立，不能套用主頁的 45 分鐘規則。

文件整理只新增說明，沒有修改程式或工作流程。
