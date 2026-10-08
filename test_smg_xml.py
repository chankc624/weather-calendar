
import urllib.request
import xml.etree.ElementTree as ET

URLS = {
    "熱帶氣旋／颱風": "https://xml.smg.gov.mo/c_typhoon.xml",
    "暴雨": "https://xml.smg.gov.mo/c_rainstorm.xml",
    "強烈季候風": "https://xml.smg.gov.mo/c_monsoon.xml",
    "雷暴": "https://xml.smg.gov.mo/c_thunderstorm.xml",
    "風暴潮": "https://xml.smg.gov.mo/c_stormsurge.xml",
    "海嘯": "https://xml.smg.gov.mo/c_tsunami.xml",
}


def get_field(root, name):
    for element in root.iter():
        tag = element.tag.split("}")[-1]
        if tag.lower() == name.lower():
            return (element.text or "").strip()
    return ""


def classify(status):
    if status == "1":
        return "active"
    if status in ("0", "2", "3"):
        return "inactive"
    return "unknown"


def visible_warnings(records):
    return [
        record for record in records
        if record["state"] == "active"
    ]


def test_display_rules():
    samples = [
        {"name": "測試颱風", "state": "active"},
        {"name": "測試暴雨", "state": "inactive"},
        {"name": "測試雷暴", "state": "unknown"},
    ]

    visible = visible_warnings(samples)
    assert len(visible) == 1
    assert visible[0]["name"] == "測試颱風"
    assert visible_warnings([]) == []
    assert classify("1") == "active"
    assert classify("0") == "inactive"
    assert classify("2") == "inactive"
    assert classify("3") == "inactive"
    assert classify("") == "unknown"

    print("PASS: 只顯示生效警告")
    print("PASS: 沒有警告時隱藏")
    print("PASS: 無法核實時隱藏")


def test_live_xml():
    records = []

    for name, url in URLS.items():
        print(f"\n=== {name} ===")

        record = {
            "name": name,
            "state": "unknown",
        }

        try:
            request = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0"},
            )

            with urllib.request.urlopen(
                request, timeout=20
            ) as response:
                data = response.read()

            root = ET.fromstring(data)

            status = get_field(root, "Status")
            inforce = get_field(root, "Inforce")
            warncode = get_field(root, "Warncode")
            issued_at = get_field(root, "IssuedAt")
            description = get_field(root, "Description")

            record["state"] = classify(status)

            print("Status:", status or "(missing)")
            print("Inforce:", inforce or "(missing)")
            print("Warncode:", warncode or "(missing)")
            print("IssuedAt:", issued_at or "(missing)")
            print("Description:", description[:120])
            print("Parsed state:", record["state"])

        except Exception as error:
            print("ERROR:", type(error).__name__, error)

        records.append(record)

    active = visible_warnings(records)

    print("\n=== 測試摘要 ===")
    print("已解析為生效警告的數量:", len(active))
    print("注意：尚未驗證資料時效及實際生效樣本")

    for record in active:
        print("ACTIVE CANDIDATE:", record["name"])

    print("XML 測試完成，未修改正式 Dashboard")


if __name__ == "__main__":
    test_display_rules()
    test_live_xml()
