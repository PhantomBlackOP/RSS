#!/usr/bin/env python3
"""Download the EXACT published Zine images from Sitemap for a one-time banner.

Temporary workflow branch only. The files are never generated or edited by AI.
"""
import hashlib, io, json, re, time
from pathlib import Path
from urllib.parse import urlparse
import requests
import xml.etree.ElementTree as ET
from PIL import Image
from playwright.sync_api import sync_playwright

OUT=Path("daily-original-checks")
OUT.mkdir(exist_ok=True)
SM="{http://www.sitemaps.org/schemas/sitemap/0.9}"
META="{https://sitemap.trevorion.io/ns/meta}"
BASE="https://raw.githubusercontent.com/PhantomBlackOP/Sitemap/main"
NUMBERS=[167,181,226,228,236,279,297,299,300,369,371,413,421,422,424,429,430,433,435,441,450,459,460,470,513,514,520,530,534,560,562,600,604,605,619,623,625,631,642,643,645,646,648,649]
assert len(NUMBERS)==44 and len(set(NUMBERS))==44
sess=requests.Session()
sess.headers.update({"User-Agent":"Mozilla/5.0 (compatible; TrevorionBanner/1.0; published-images-only)","Accept":"image/avif,image/webp,image/apng,image/*,*/*;q=0.8"})
def establish_clearance():
    probe="https://zine.trevorion.io/wp-json/wp/v2/categories?per_page=1"
    print("Establishing SiteGround clearance with Chromium...",flush=True)
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        ctx=browser.new_context(locale="en-US")
        page=ctx.new_page()
        try:
            page.goto(probe,wait_until="domcontentloaded",timeout=120000)
            deadline=time.monotonic()+90
            while time.monotonic()<deadline:
                body=page.locator("body").inner_text(timeout=5000).strip()
                if page.url.startswith(probe.split("?")[0]) and body[:1] in {"[","{"}:
                    break
                page.wait_for_timeout(1000)
            else:raise RuntimeError("SiteGround clearance not established")
            sess.headers["User-Agent"]=page.evaluate("navigator.userAgent")
            for cookie in ctx.cookies():
                sess.cookies.set(cookie["name"],cookie["value"],domain=cookie.get("domain") or "zine.trevorion.io",path=cookie.get("path") or "/")
        finally:browser.close()
    trial=sess.get(probe,timeout=30,headers={"Accept":"application/json"})
    if trial.status_code!=200 or trial.text.lstrip()[:1] not in ("[","{"):
        raise RuntimeError("WordPress probe did not survive SiteGround clearance: "+str(trial.status_code))
    print("Clearance OK.",flush=True)

def get(url):
    last=None
    for i in range(4):
        try:
            response=sess.get(url,timeout=50)
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            last=e;time.sleep(1.5*(i+1))
    raise RuntimeError(f"Download failed: {url}: {last}")
index=ET.fromstring(get(BASE+"/zine/archive.xml"))
child_paths=[node.findtext(SM+"loc") for node in index.findall(SM+"sitemap")]
assert len(child_paths)>=12, len(child_paths)
selected={}
for link in child_paths:
    p=urlparse(link).path
    if not re.fullmatch(r"/zine/archive/20\d{2}-\d{2}\.xml",p):
        raise ValueError("Unexpected sitemap path "+str(p))
    xml=ET.fromstring(get(BASE+p))
    for node in xml.findall(SM+"url"):
        title=node.findtext(META+"title") or ""
        m=re.match(r"^(\d{3}):",title)
        if not m:continue
        number=int(m.group(1))
        if number not in NUMBERS:continue
        post=node.findtext(SM+"loc") or ""
        image=node.findtext(META+"og_image") or ""
        original_image=node.findtext(META+"og_image") or ""
        if not post.startswith("https://zine.trevorion.io/") or not image.startswith("https://zine.trevorion.io/wp-content/uploads/"):
            raise ValueError("Unverified media source for "+str(number))
        if number in selected and selected[number]["post_url"]!=post:
            raise ValueError(f"Ambiguous Daily {number}")
        selected[number]={"number":number,"title":title,"post_url":post,"published_image_url":image,"original_published_image_url":original_image,"sitemap_xml":link}
miss=set(NUMBERS)-set(selected)
if miss:raise RuntimeError(f"Missing published Daily numbers: {sorted(miss)}")
establish_clearance()
manifest=[]
for number in NUMBERS:
    info=selected[number]
    raw=get(info["published_image_url"])
    try:
        mime=Image.open(io.BytesIO(raw))
    except Exception as exc:
        raise RuntimeError(f"Published image download returned non-image for {number}: {info['published_image_url']}; first bytes={raw[:170]!r}") from exc
    mime.verify()
    with Image.open(io.BytesIO(raw)) as im:
        dimensions=list(im.size)
        im_mode=im.mode
    filepath=OUT/f"daily_{number:03d}.png"
    # Keep the downloaded file's native bytes and actual extension.
    ext=Path(urlparse(info["published_image_url"]).path).suffix.lower()
    if ext not in (".png",".jpg",".jpeg",".webp"):raise ValueError("Unexpected image format "+ext)
    filepath=OUT/f"daily_{number:03d}{ext}"
    filepath.write_bytes(raw)
    manifest.append({**info,"local_filename":filepath.name,"sha256":hashlib.sha256(raw).hexdigest(),"dimensions":dimensions,"mode":im_mode,"bytes":len(raw)})
    print(f"{number:03d}: {dimensions} {len(raw)} bytes {info['title']}",flush=True)
(OUT/"canonical_sources.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf8")
print(f"Verified {len(manifest)} exact published Zine media files; wrote manifest.",flush=True)
