#!/usr/bin/env python3
"""Fetch SMG's official warning RSS; do not infer active warning status from RSS items."""
import datetime as dt
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

URL = 'https://rss.smg.gov.mo/c_WSignal_rss.xml'
OUTPUT = Path('smg_warnings.json')
result = {'source': URL, 'checked_at': dt.datetime.now(dt.timezone.utc).isoformat(),
          'status': 'unavailable', 'active_state': 'unknown', 'items': []}
try:
    req = Request(URL, headers={'User-Agent': 'CHAN-Family-Dashboard/2.6.1 (+GitHub Pages)'})
    with urlopen(req, timeout=20) as resp:
        body = resp.read(1024 * 1024)
    root = ET.fromstring(body)
    entries = root.findall('.//item')
    for item in entries[:5]:
        title = (item.findtext('title') or '').strip()
        published = (item.findtext('pubDate') or '').strip()
        if title:
            result['items'].append({'title': title[:180], 'published': published[:100]})
    result['status'] = 'fetched'
except Exception as exc:
    print('SMG RSS unavailable:', type(exc).__name__, str(exc)[:180])
OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('status:', result['status'], 'items:', len(result['items']))
