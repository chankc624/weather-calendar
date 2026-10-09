#!/usr/bin/env python3
"""Create a landscape e-ink dashboard. Missing/stale data is never presented as live."""
import json, os, urllib.request, datetime, calendar
from pathlib import Path
from zoneinfo import ZoneInfo
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'kindle'/'dashboard.png'
TZ=ZoneInfo('Asia/Macau')
NOW=datetime.datetime.now(TZ)
W,H=1448,1072
IM=Image.new('RGB',(W,H),'white'); D=ImageDraw.Draw(IM)
FONT_PATHS=['/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc','/usr/share/fonts/opentype/noto/NotoSansCJKtc-Regular.otf','/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc']
FONT_BOLD=['/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc','/usr/share/fonts/opentype/noto/noto/NotoSansCJK-Bold.ttc']
def font(n,bold=False):
    for p in (FONT_BOLD if bold else [])+FONT_PATHS:
        if os.path.exists(p): return ImageFont.truetype(p,n)
    return ImageFont.load_default()
def txt(x,y,s,size=30,bold=False,fill='#171717'):
    D.text((x,y),str(s),font=font(size,bold),fill=fill)
def card(box,title):
    D.rounded_rectangle(box,radius=19,outline='#222222',width=3,fill='white')
    txt(box[0]+25,box[1]+19,title,32,True)
    D.line((box[0]+24,box[1]+72,box[2]-24,box[1]+72),fill='#aaaaaa',width=2)

def fetch_weather():
    url=('https://api.open-meteo.com/v1/forecast?latitude=22.1987&longitude=113.5439'
         '&current=temperature_2m,relative_humidity_2m,weather_code'
         '&daily=temperature_2m_max,temperature_2m_min&timezone=Asia%2FMacau&forecast_days=2')
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'CHAN-Kindle-Dashboard/1.0'})
        with urllib.request.urlopen(req,timeout=20) as r: data=json.load(r)
        c=data['current']; d=data['daily']
        observed=datetime.datetime.fromisoformat(c['time']).replace(tzinfo=TZ)
        if abs((NOW-observed).total_seconds())>3*3600: return None
        return {'temp':round(c['temperature_2m']),'humidity':round(c['relative_humidity_2m']),
                'min':round(d['temperature_2m_min'][0]),'max':round(d['temperature_2m_max'][0]),
                'code':c['weather_code'],'time':observed.strftime('%H:%M')}
    except Exception as e:
        print('Weather unavailable:',e)
        return None

def warnings():
    """Only explicitly confirmed, fresh warnings are displayed."""
    try:
        d=json.loads((ROOT/'smg_warnings.json').read_text(encoding='utf-8'))
        checked=datetime.datetime.fromisoformat(d['checked_at'].replace('Z','+00:00'))
        if checked.tzinfo is None or not (-300 <= (NOW-checked).total_seconds() <= 45*60): return []
        if d.get('display_warnings') is not True: return []
        return [w['name'].strip() for w in d.get('active_warnings',[]) if isinstance(w,dict) and w.get('state')=='active' and isinstance(w.get('name'),str) and w['name'].strip()][:2]
    except (OSError,ValueError,KeyError,TypeError): return []

def desc(code):
    if code==0:return '晴朗'
    if code<=3:return '多雲'
    if code in (45,48):return '有霧'
    if code>=95:return '雷暴'
    if 51<=code<=82:return '有雨'
    return '天氣變化'

D.rectangle((0,0,W,104),fill='#171717')
txt(40,20,'CHAN FAMILY DASHBOARD',48,True,'white')
txt(1095,39,'KINDLE  ·  MACAU',24,False,'white')
card((30,125,710,520),'澳門時間 / TIME')
txt(72,237,NOW.strftime('%H:%M'),150,True)
week=['星期一','星期二','星期三','星期四','星期五','星期六','星期日'][NOW.weekday()]
txt(78,434,f'{NOW.year}年{NOW.month}月{NOW.day}日  {week}',37)
card((730,125,1418,520),'澳門天氣 / WEATHER')
w=fetch_weather()
if w:
    txt(775,215,f"{w['temp']}°C",113,True)
    txt(1075,255,desc(w['code']),42)
    txt(778,374,f"今日 {w['min']}–{w['max']}°C    濕度 {w['humidity']}%",32)
    txt(778,444,f"天氣觀測 {w['time']} · Open-Meteo",24,False,'#555555')
else:
    txt(775,243,'天氣暫不可用',52,True)
    txt(778,423,'未能取得可靠即時資料',26,False,'#555555')
card((30,540,710,1020),'家庭日曆 / CALENDAR')
txt(72,633,f'{NOW.year} 年 {NOW.month} 月',39,True)
weekheads=['一','二','三','四','五','六','日']
for i,s in enumerate(weekheads):txt(93+i*86,699,s,26,True)
cal=calendar.Calendar(firstweekday=0).monthdayscalendar(NOW.year,NOW.month)
for row,days in enumerate(cal):
    for i,n in enumerate(days):
        if not n:continue
        x=93+i*86;y=756+row*49
        if n==NOW.day:
            D.ellipse((x-8,y-5,x+39,y+42),fill='#222222')
            txt(x,y,str(n),27,True,'white')
        else:txt(x,y,str(n),27)
card((730,540,1418,1020),'家庭資訊 / FAMILY')
txt(775,645,'Charlotte · MAC K1',39,True)
txt(775,717,'生日：11月25日',31)
txt(775,781,'家庭行程：未設定',31)
warn=warnings()
if warn:
    D.rounded_rectangle((766,857,1383,988),radius=13,outline='#111111',width=3)
    txt(784,865,'澳門氣象局生效警告',28,True)
    for i,s in enumerate(warn):txt(784,907+i*37,s[:24],25,True)
else:
    txt(775,909,'',24)
OUT.parent.mkdir(exist_ok=True)
IM.save(OUT,optimize=True)
print('Generated:',OUT,'size:',IM.size,'weather:',bool(w),'active_warnings:',len(warn))
