
import urllib.request
import xml.etree.ElementTree as ET

URLS = {
    "暴雨": "https://xml.smg.gov.mo/c_rainstorm.xml",
    "雷暴": "https://xml.smg.gov.mo/c_thunderstorm.xml",
}

for name, url in URLS.items():
    print(f"\n=== {name} ===")
    try:
        request = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(request, timeout=20) as response:
            data = response.read()

        root = ET.fromstring(data)
        for element in root.iter():
            value = (element.text or "").strip()
            if value and len(value) < 150:
                print(element.tag, "=", value)

    except Exception as error:
        print("讀取失敗：", type(error).__name__, str(error))
