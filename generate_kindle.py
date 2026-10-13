#!/usr/bin/env python3
"""Create a landscape e-ink dashboard (Traditional Chinese, no clock, no warning banner)."""
import os
import json
import urllib.request
import datetime
import calendar
from pathlib import Path
from zoneinfo import ZoneInfo
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "kindle" / "dashboard.png"

TZ = ZoneInfo("Asia/Macau")
NOW = datetime.datetime.now(TZ)

W, H = 1448, 1072
IM = Image.new("RGB", (W, H), "white")
D = ImageDraw.Draw(IM)

FONT_PATHS = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJKtc-Regular.otf",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
]
FONT_BOLD = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/opentype/noto/noto/NotoSansCJK-Bold.ttc",
]

TEXT = "#171717"
GRAY = "#666666"
LINE = "#AAAAAA"
BORDER = "#222222"
HEADER_BG = "#171717"
WHITE = "white"

def font(size, bold=False):
    for p in (FONT_BOLD if bold else []) + FONT_PATHS:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

def txt(x, y, s, size=30, bold=False, fill=TEXT):
    D.text((x, y), str(s), font=font(size, bold), fill=fill)

def txt_right(x, y, s, size=30, bold=False, fill=TEXT):
    f = font(size, bold)
    box = D.textbbox((0, 0), str(s), font=f)
    w = box[2] - box[0]
    D.text((x - w, y), str(s), font=f, fill=fill)

def txt_center(x, y, s, size=30, bold=False, fill=TEXT):
    f = font(size, bold)
    box = D.textbbox((0, 0), str(s), font=f)
    w = box[2] - box[0]
    h = box[3] - box[1]
    D.text((x - w / 2, y - h / 2), str(s), font=f, fill=fill)

def card(box, title):
    D.rounded_rectangle(box, radius=19, outline=BORDER, width=3, fill=WHITE)
    txt(box[0] + 25, box[1] + 18, title, 32, True)
    D.line((box[0] + 24, box[1] + 72, box[2] - 24, box[1] + 72), fill=LINE, width=2)

def weather_desc(code):
    if code == 0:
        return "晴朗"
    if code in (1, 2, 3):
        return "多雲"
    if code in (45, 48):
        return "有霧"
    if 51 <= code <= 57:
        return "毛毛雨"
    if 61 <= code <= 67:
        return "有雨"
    if 71 <= code <= 77:
        return "降雪"
    if 80 <= code <= 82:
        return "陣雨"
    if 85 <= code <= 86:
        return "陣雪"
    if code >= 95:
        return "雷暴"
    return "天氣變化"

def fetch_weather():
    url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=22.1987&longitude=113.5439"
        "&current=temperature_2m,relative_humidity_2m,weather_code"
        "&daily=temperature_2m_max,temperature_2m_min"
        "&timezone=Asia%2FMacau"
        "&forecast_days=2"
    )
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "CHAN-Kindle-Dashboard/2.0"}
        )
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.load(r)

        current = data["current"]
        daily = data["daily"]
        observed = datetime.datetime.fromisoformat(current["time"]).replace(tzinfo=TZ)

        # 如果資料過舊，就唔當作即時資料顯示
        if abs((NOW - observed).total_seconds()) > 3 * 3600:
            return None

        return {
            "temp": round(current["temperature_2m"]),
            "humidity": round(current["relative_humidity_2m"]),
            "min": round(daily["temperature_2m_min"][0]),
            "max": round(daily["temperature_2m_max"][0]),
            "code": current["weather_code"],
            "source": "Open-Meteo",
        }
    except Exception as e:
        print("Weather unavailable:", e)
        return None

def next_birthday(month, day):
    today = NOW.date()
    year = today.year
    target = datetime.date(year, month, day)
    if target < today:
        target = datetime.date(year + 1, month, day)
    return target, (target - today).days

# ===== Header =====
D.rectangle((0, 0, W, 96), fill=HEADER_BG)

weekday_names = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
today_str = f"{NOW.year}年{NOW.month}月{NOW.day}日  {weekday_names[NOW.weekday()]}"

txt(36, 22, today_str, 42, True, WHITE)
txt_right(W - 36, 28, "澳門 · 金利達", 28, True, WHITE)

# ===== Cards =====
weather_box = (30, 122, 930, 468)
today_box   = (950, 122, 1418, 468)
cal_box     = (30, 500, 930, 1040)
family_box  = (950, 500, 1418, 1040)

card(weather_box, "澳門天氣 / WEATHER")
card(today_box, "今日資訊 / TODAY")
card(cal_box, "家庭日曆 / CALENDAR")
card(family_box, "家庭資訊 / FAMILY")

# ===== Weather =====
w = fetch_weather()
if w:
    txt(72, 205, f"{w['temp']}°C", 136, True)
    txt(410, 238, weather_desc(w["code"]), 52, True)

    txt(75, 365, f"今日氣溫：{w['min']}–{w['max']}°C", 34)
    txt(75, 414, f"相對濕度：{w['humidity']}%", 34)
    txt(75, 447, f"資料來源：{w['source']}", 24, False, GRAY)
else:
    txt(72, 250, "天氣資料暫不可用", 52, True)
    txt(75, 355, "未能取得可靠即時資料", 28, False, GRAY)

# ===== Today Info =====
bday_target, bday_days = next_birthday(11, 25)

txt(978, 170, "今日日期", 26, True, GRAY)
txt(978, 208, f"{NOW.year}年{NOW.month}月{NOW.day}日", 40, True)

txt(978, 278, "所在位置", 26, True, GRAY)
txt(978, 316, "澳門 · 金利達", 36, True)

txt(978, 382, "Charlotte 生日倒數", 26, True, GRAY)
txt(978, 418, f"{bday_days} 天", 42, True)

# ===== Calendar =====
txt(72, 595, f"{NOW.year} 年 {NOW.month} 月", 42, True)

weekheads = ["一", "二", "三", "四", "五", "六", "日"]
start_x = 92
start_y = 670
col_w = 108
row_h = 58

for i, s in enumerate(weekheads):
    txt(start_x + i * col_w + 15, start_y, s, 28, True)

cal = calendar.Calendar(firstweekday=0).monthdayscalendar(NOW.year, NOW.month)

for row, days in enumerate(cal):
    for i, n in enumerate(days):
        if not n:
            continue
        x = start_x + i * col_w
        y = start_y + 72 + row * row_h

        if n == NOW.day:
            D.ellipse((x - 6, y - 6, x + 44, y + 44), fill=BORDER)
            txt(x + 7, y + 2, str(n), 28, True, WHITE)
        else:
            txt(x + 7, y + 2, str(n), 28, False, TEXT)

# ===== Family Info =====
txt(975, 612, "Charlotte · MAC K1", 40, True)
txt(975, 688, "生日：11月25日", 31)
txt(975, 748, f"下次生日：{bday_target.year}年11月25日", 31)
txt(975, 808, "家庭行程：未設定", 31)

txt(975, 900, "備註", 26, True, GRAY)
txt(975, 940, "此版本已取消時鐘及氣象警告。", 26, False, GRAY)

OUT.parent.mkdir(exist_ok=True)
IM.save(OUT, optimize=True)

print("Generated:", OUT)
print("size:", IM.size)
print("weather:", bool(w))
