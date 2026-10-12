#!/usr/bin/env python3
"""One-time visual review contact sheets of all published Zine Dailies.

This audit runs only on a temporary branch. No image is invented or replaced.
Uses only image URLs and editorial metadata explicitly present in Sitemap XML.
"""
from pathlib import Path
import hashlib, io, json, re, time, math, textwrap
from urllib.parse import urlparse
from xml.etree import ElementTree as ET
from PIL import Image, ImageDraw, ImageFont
import requests
from playwright.sync_api import sync_playwright

BASE="https://raw.githubusercontent.com/PhantomBlackOP/Sitemap/main"
SM="{http://www.sitemaps.org/schemas/sitemap/0.9}"
META="{https://sitemap.trevorion.io/ns/meta}"
DEST=Path("daily-review-inventory")
DEST.mkdir(exist_ok=True)
sess=requests.Session()
sess.headers.update({"User-Agent":"Mozilla/5.0","Accept":"image/avif,image/webp,image/apng,image/*,*/*;q=0.8"})
def fetch(url):
    last=None
    for k in range(4):
        try:
            z=sess.get(url,timeout=55)
            z.raise_for_status()
            return z.content
        except requests.RequestException as e:
            last=e
            time.sleep(1.0+k)
    raise RuntimeError(f"Cannot retrieve {url}: {last}")

index=ET.fromstring(fetch(BASE+"/zine/archive.xml"))
links=[n.findtext(SM+"loc") for n in index.findall(SM+"sitemap")]
all_posts=[]
for link in links:
    path=urlparse(link).path
    if not re.fullmatch(r"/zine/archive/20\d{2}-\d{2}\.xml",path):
        raise ValueError("Unexpected XML child: "+str(link))
    xml=ET.fromstring(fetch(BASE+path))
    for n in xml.findall(SM+"url"):
        title=n.findtext(META+"title") or ""
        url=n.findtext(SM+"loc") or ""
        image=n.findtext(META+"og_image") or ""
        mosaic=n.findtext(META+"mosaic_image") or ""
        tags=json.loads(n.findtext(META+"tags") or "[]")
        if not url.startswith("https://zine.trevorion.io/") or not image.startswith("https://zine.trevorion.io/wp-content/uploads/"):
            raise ValueError("Untrusted published artwork entry: "+url)
        if not mosaic.startswith("https://zine.trevorion.io/wp-content/uploads/"):
            raise ValueError("Missing small published image: "+title)
        match=re.match(r"^(\d{3}):",title)
        all_posts.append({"title":title,"url":url,"image":image,"mosaic":mosaic,"tags":tags,"published":n.findtext(META+"published") or "","number":int(match.group(1)) if match else None})
all_posts.sort(key=lambda p:(p["published"],p["title"]))
print(f"Inventory: {len(all_posts)} published Daily entries.",flush=True)
if len(all_posts)<600:raise RuntimeError("Unexpectedly small Daily inventory")

def clearance():
    probe="https://zine.trevorion.io/wp-json/wp/v2/categories?per_page=1"
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        context=browser.new_context(locale="en-US")
        page=context.new_page()
        try:
            page.goto(probe,wait_until="domcontentloaded",timeout=120000)
            deadline=time.monotonic()+90
            while time.monotonic()<deadline:
                b=page.locator("body").inner_text(timeout=5000).strip()
                if b[:1] in ("[","{") and page.url.startswith(probe.split("?")[0]):
                    break
                page.wait_for_timeout(1000)
            else:raise RuntimeError("SiteGround clearance not available")
            sess.headers["User-Agent"]=page.evaluate("navigator.userAgent")
            for cookie in context.cookies():
                sess.cookies.set(cookie["name"],cookie["value"],domain=cookie.get("domain") or "zine.trevorion.io",path=cookie.get("path") or "/")
        finally:browser.close()
    z=sess.get(probe,timeout=40)
    if z.status_code!=200 or z.text.lstrip()[:1] not in ("[","{"):
        raise RuntimeError("Clearance not reusable")

clearance()
font_path="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
font=ImageFont.truetype(font_path,13)
font_header=ImageFont.truetype(font_path,17)
font_small=ImageFont.truetype(font_path,11)
CW,CH=262,222
COLS,ROWS=5,7
PAGE_SIZE=COLS*ROWS
contact=None
for i,entry in enumerate(all_posts):
    if i%PAGE_SIZE==0:
        contact=Image.new("RGB",(CW*COLS,CH*ROWS),(12,20,33))
        draw=ImageDraw.Draw(contact)
    raw=fetch(entry["mosaic"])
    try:
        im=Image.open(io.BytesIO(raw)).convert("RGB")
        im.thumbnail((CW-14,CH-68),Image.Resampling.LANCZOS)
    except Exception as e:
        raise ValueError(f"Bad published miniature: {entry['title']} {entry['mosaic']} {raw[:80]!r}") from e
    c=i%PAGE_SIZE
    x=(c%COLS)*CW
    y=(c//COLS)*CH
    contact.paste(im,(x+(CW-im.width)//2,y+5+(CH-68-im.height)//2))
    label=entry["title"]
    label=re.sub(r"[^\x20-\x7e]","",label)
    draw=ImageDraw.Draw(contact)
    draw.text((x+8,y+CH-65),f"{i+1:03d} | {entry['number'] or 'SPECIAL'}",font=font_header,fill=(139,191,246))
    for li,line in enumerate(textwrap.wrap(label,width=34)[:2]):
        draw.text((x+8,y+CH-44+li*14),line,font=font,fill=(237,243,251))
    if i%PAGE_SIZE==PAGE_SIZE-1 or i==len(all_posts)-1:
        page_no=i//PAGE_SIZE+1
        path=DEST/f"sheet_{page_no:02d}.jpg"
        contact.save(path,quality=87,optimize=True)
        print(f"{path} {min(i+1,len(all_posts))}/{len(all_posts)}",flush=True)
(DEST/"inventory.json").write_text(json.dumps(all_posts,indent=2,ensure_ascii=False),encoding="utf8")
print("Complete.")
