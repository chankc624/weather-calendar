
#!/usr/bin/env python3
"""Macau SMG warnings snapshot for CHAN Family Dashboard V2.6.2."""

import datetime as dt
import json
from pathlib import Path
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

TZ = dt.timezone(dt.timedelta(hours=8))
NOW = dt.datetime.now(TZ)
OUTPUT = Path("smg_warnings.json")

RSS_URL = "https://rss.smg.gov.mo/c_WSignal_rss.xml"

XML_URLS = {
    "熱帶氣旋／颱風": "https://xml.smg.gov.mo/c_typhoon.xml",
    "暴雨": "https://xml.smg.gov.mo/c_rainstorm.xml",
    "強烈季候風": "https://xml.smg.gov.mo/c_monsoon.xml",
    "雷暴": "https://xml.smg.gov.mo/c_thunderstorm.xml",
    "風暴潮": "https://xml.smg.gov.mo/c_stormsurge.xml",
    "海嘯": "https://xml.smg.gov.mo/c_tsunami.xml",
}

# Conservative temporary verification window.
# Older active reports remain unverified, not confirmed inactive.
MAX_ACTIVE_AGE_HOURS = 48


def fetch_xml(url):
    request = Request(
        url,
        headers={"User-Agent": "CHAN-Family-Dashboard/2.6.2"},
    )
    with urlopen(request, timeout=20) as response:
        return ET.fromstring(response.read(1024 * 1024))


def field(root, name):
    for element in root.iter():
        tag = element.tag.split("}")[-1]
        if tag.lower() == name.lower():
            return (element.text or "").strip()
    return ""


def parse_time(value):
    if not value:
        return None
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"):
        try:
            return dt.datetime.strptime(value, fmt).replace(tzinfo=TZ)
        except ValueError:
            pass
    return None


def check_warning(name, url):
    record = {
        "name": name,
        "source": url,
        "state": "unknown",
        "status": "",
        "inforce": "",
        "warncode": "",
        "issued_at": "",
        "description": "",
    }

    try:
        root = fetch_xml(url)
        status = field(root, "Status")
        issued_at = field(root, "IssuedAt")
        issued = parse_time(issued_at)

        record.update({
            "status": status,
            "inforce": field(root, "Inforce"),
            "warncode": field(root, "Warncode"),
            "issued_at": issued_at,
            "description": field(root, "Description")[:300],
        })

        if status in ("0", "2", "3"):
            record["state"] = "inactive"
        elif status == "1":
            if issued is None:
                record["reason"] = "missing_or_invalid_issue_time"
            else:
                age_hours = (NOW - issued).total_seconds() / 3600
                if 0 <= age_hours <= MAX_ACTIVE_AGE_HOURS:
                    record["state"] = "active"
                else:
                    record["reason"] = "active_report_not_recently_verified"
        else:
            record["reason"] = "unknown_status"

    except Exception as exc:
        record["reason"] = "fetch_or_parse_error"
        print(name, type(exc).__name__, str(exc)[:180])

    return record


def fetch_rss():
    items = []
    status = "unavailable"

    try:
        root = fetch_xml(RSS_URL)
        for item in root.findall(".//item")[:5]:
            title = (item.findtext("title") or "").strip()
            published = (item.findtext("pubDate") or "").strip()
            if title:
                items.append({
                    "title": title[:180],
                    "published": published[:100],
                })
        status = "fetched"
    except Exception as exc:
        print("RSS:", type(exc).__name__, str(exc)[:180])

    return status, items


def main():
    warnings = [
        check_warning(name, url)
        for name, url in XML_URLS.items()
    ]

    active = [
        item for item in warnings
        if item["state"] == "active"
    ]

    rss_status, items = fetch_rss()

    result = {
        "source": RSS_URL,
        "checked_at": NOW.astimezone(dt.timezone.utc).isoformat(),
        "status": rss_status,
        "active_state": "active" if active else "unknown",
        "items": items,
        "xml_checked_at": NOW.isoformat(),
        "warnings": warnings,
        "active_warnings": active,
        "display_warnings": bool(active),
        "verification_note": (
            "Active warnings require a recent issued timestamp. "
            "Unknown status must not be interpreted as safe."
        ),
    }

    OUTPUT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print("XML feeds checked:", len(warnings))
    print("Confirmed active candidates:", len(active))
    print("Unknown:", sum(w["state"] == "unknown" for w in warnings))
    print("Display warnings:", result["display_warnings"])
    print("RSS:", rss_status)


if __name__ == "__main__":
    main()
