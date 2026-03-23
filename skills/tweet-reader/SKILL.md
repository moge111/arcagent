---
name: tweet-reader
description: "Read tweet content and images from X/Twitter URLs"
allowed-tools: ["shell_exec"]
---

# Tweet Reader Skill

When a user shares a Twitter/X URL, extract the tweet content AND any images.

## Step 1: Parse the URL

Twitter/X URLs look like:
- `https://x.com/USERNAME/status/TWEET_ID`
- `https://twitter.com/USERNAME/status/TWEET_ID`
- May have `?s=20` or other query params — ignore those

Extract USERNAME and TWEET_ID from the URL path.

## Step 2: Fetch tweet text and image URLs

Try these APIs in order until one works:

### FxTwitter API (best — includes images)
```bash
curl -s "https://api.fxtwitter.com/USERNAME/status/TWEET_ID" | python3 -c "
import sys,json
d=json.load(sys.stdin)
t=d.get('tweet',{})
print('Author:', t.get('author',{}).get('name',''), '(@'+t.get('author',{}).get('screen_name','')+')')
print('Date:', t.get('created_at',''))
print('Text:', t.get('text',''))
media = t.get('media',{})
photos = media.get('photos',[]) if media else []
mosaic = media.get('mosaic',{}) if media else {}
all_media = media.get('all',[]) if media else []
urls = []
for p in photos:
    if p.get('url'): urls.append(p['url'])
for m in all_media:
    if m.get('url') and m['url'] not in urls: urls.append(m['url'])
if urls:
    print('Images:')
    for u in urls: print(u)
"
```

### VxTwitter API (fallback)
```bash
curl -s "https://api.vxtwitter.com/USERNAME/status/TWEET_ID" | python3 -c "
import sys,json
d=json.load(sys.stdin)
print('Author:', d.get('user_name',''), '(@'+d.get('user_screen_name','')+')')
print('Text:', d.get('text',''))
for u in d.get('media_urls',[]):
    print('Image:', u)
"
```

### oEmbed API (text only, last resort)
```bash
curl -s "https://publish.twitter.com/oembed?url=https://x.com/USERNAME/status/TWEET_ID&omit_script=true" | python3 -c "import sys,json,re; d=json.load(sys.stdin); print(d.get('author_name','')); print(re.sub('<[^>]+>','',d.get('html','')))"
```

## Step 3: If tweet has images, download and OCR them

Download the image:
```bash
curl -s -L -o /tmp/tweet_img.jpg "IMAGE_URL_FROM_STEP_2"
```

Then OCR it with Python (tesseract):
```bash
python3 -c "
try:
    from PIL import Image
    import pytesseract
    img = Image.open('/tmp/tweet_img.jpg')
    text = pytesseract.image_to_string(img)
    print(text)
except ImportError:
    print('NEED_INSTALL')
except Exception as e:
    print(f'OCR failed: {e}')
"
```

If it prints NEED_INSTALL, install the dependencies:
```bash
apt-get install -y tesseract-ocr > /dev/null 2>&1
pip install pytesseract Pillow > /dev/null 2>&1
```
Then retry the OCR.

## Step 4: Present results

- Show the tweet author, date, and text
- Show any text extracted from images
- If the user asks to "build this" or similar, use the full content (text + image text) as the spec
