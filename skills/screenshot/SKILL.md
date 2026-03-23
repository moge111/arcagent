---
name: screenshot
description: "Take screenshots of websites and read visual content using a headless browser"
allowed-tools: ["shell_exec", "read_file"]
---

# Screenshot Skill

Take screenshots of websites using a headless browser, then read/OCR them.

## Take a screenshot of a website

```bash
python3 -c "
from playwright.sync_api import sync_playwright
import sys

url = sys.argv[1]
output = sys.argv[2] if len(sys.argv) > 2 else '/tmp/screenshot.png'

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1280, 'height': 720})
    page.goto(url, timeout=30000)
    page.wait_for_timeout(2000)  # Wait for JS to render
    page.screenshot(path=output, full_page=False)
    browser.close()
    print(f'Screenshot saved to {output}')
" "URL_HERE" "/tmp/screenshot.png"
```

## Take a full-page screenshot
```bash
python3 -c "
from playwright.sync_api import sync_playwright
import sys

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1280, 'height': 720})
    page.goto(sys.argv[1], timeout=30000)
    page.wait_for_timeout(2000)
    page.screenshot(path='/tmp/screenshot_full.png', full_page=True)
    browser.close()
    print('Full-page screenshot saved')
" "URL_HERE"
```

## Read text from a screenshot (OCR)
```bash
python3 -c "
from PIL import Image
import pytesseract
text = pytesseract.image_to_string(Image.open('/tmp/screenshot.png'))
print(text)
"
```

## Get page text content (no screenshot needed)
```bash
python3 -c "
from playwright.sync_api import sync_playwright
import sys

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(sys.argv[1], timeout=30000)
    page.wait_for_timeout(2000)
    print(page.inner_text('body')[:50000])
    browser.close()
" "URL_HERE"
```

## If playwright is not installed
```bash
pip install playwright
playwright install chromium --with-deps
```

## Notes
- Screenshots are saved to /tmp/ and can be sent as Discord attachments
- Full-page screenshots can be very large — use viewport screenshots for sharing
- The headless browser CAN execute JavaScript, unlike simple curl/fetch
