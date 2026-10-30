# weather-calendar

澳門家庭天氣與日曆 dashboard，提供瀏覽器顯示頁面。

## 顯示入口

| 入口 | 用途 |
| --- | --- |
| [index.html](index.html) | 主 dashboard：相片輪播、時鐘、農曆、天氣、家庭日曆及重要日子 |
| [v2/index.html](v2/index.html) | 另一版 Lenovo Home Dashboard；設定及更新邏輯與主頁獨立 |

## 本機預覽

需要 Git、Python 3，以及可連上網的現代瀏覽器。網頁沒有 npm 安裝或編譯步驟。

```sh
git clone https://github.com/chankc624/weather-calendar.git
cd weather-calendar
python3 -m http.server 8000 --bind 127.0.0.1
```

開啟 <http://localhost:8000/>；另一版在 <http://localhost:8000/v2/>。請用 HTTP 預覽，避免直接開啟 HTML 時的瀏覽器存取限制。按 Ctrl+C 停止伺服器。

主頁點擊側欄以外位置可切換資訊顯示；螢幕常亮功能視瀏覽器權限及支援而定。

## 檔案導覽

| 檔案 | 說明 |
| --- | --- |
| `index.html` | 主頁樣式、JavaScript 與 `CFG` 個人化設定 |
| `v2/index.html` | 獨立版本頁面 |
| `fetch_smg.py` | 讀取澳門氣象局 XML／RSS，寫入警告快照 |
| `smg_warnings.json` | 自動產生的快照，不宜手動維護 |
| `test_smg_xml.py` | 顯示規則斷言及官方 XML 連線診斷 |
| `test-warning.html` | 模擬警告顯示頁，不是真實氣象資訊 |
| `.github/workflows/` | 自動更新及手動診斷工作流程 |

## 更新時間

| 項目 | 目前設定 |
| --- | --- |
| 主頁相片 | 每 15 秒輪播 |
| 主頁天氣 | 開啟頁面時及每 30 分鐘更新 |
| 主頁警告快照讀取 | 開啟頁面時及每 10 分鐘更新 |
| 主頁版本檢查 | 開啟約 1 分鐘後，之後每 6 小時 |
| SMG 快照產生 | GitHub Actions 每 15 分鐘排程 |

GitHub Actions 的 cron 使用 UTC，排程可能延遲，並非準時服務保證。`v2/` 有自己的更新間隔，詳見[維護說明](docs/MAINTENANCE.md)。

## 資料及限制

- 天氣使用 [Open-Meteo](https://open-meteo.com/)，目前座標為澳門（22.1987, 113.5439），時區為 `Asia/Macau`。
- 警告資料來源為[澳門地球物理氣象局](https://www.smg.gov.mo/) XML／RSS。RSS 標題本身不會被當作已核實的生效警告。
- 主頁隱藏過期、無法核實或不符合顯示規則的警告；**沒有顯示警告不代表已確認沒有警告或安全**。請以氣象局官方資訊為準。
- 約兩小時降雨提示根據逐小時預報推算，並非逐分鐘雷達。
- 相片由外部網址載入；天氣、相片及警告更新需要網絡。
- 家庭行程及生日目前由程式內設定提供，未有 Outlook／iCloud 日曆同步。
- 本 repository 為公開；加入相片、生日或行程前，請考慮資料會否公開。

個人化、部署、手動更新及故障排查見[維護說明](docs/MAINTENANCE.md)。
