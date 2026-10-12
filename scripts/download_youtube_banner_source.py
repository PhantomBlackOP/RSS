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

OUT=Path("banner-canonical-assets")
OUT.mkdir(exist_ok=True)
SM="{http://www.sitemaps.org/schemas/sitemap/0.9}"
META="{https://sitemap.trevorion.io/ns/meta}"
BASE="https://raw.githubusercontent.com/PhantomBlackOP/Sitemap/main"
NUMBERS=[9,24,62,68,153,159,181,245,270,273,344,352,368,374,441,452,502,513,570,577,600,605,608,624,635,638,644,645,646,649]
assert len(NUMBERS)==30 and len(set(NUMBERS))==30
sess=requests.Session()
sess.headers.update({"User-Agent":"Mozilla/5.0 (compatible; TrevorionBanner/1.0; published-images-only)","Accept":"image/avif,image/webp,image/apng,image/*,*/*;q=0.8"})
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
        if not post.startswith("https://zine.trevorion.io/") or not image.startswith("https://zine.trevorion.io/wp-content/uploads/"):
            raise ValueError("Unverified media source for "+str(number))
        if number in selected and selected[number]["post_url"]!=post:
            raise ValueError(f"Ambiguous Daily {number}")
        selected[number]={"number":number,"title":title,"post_url":post,"published_image_url":image,"sitemap_xml":link}
miss=set(NUMBERS)-set(selected)
if miss:raise RuntimeError(f"Missing published Daily numbers: {sorted(miss)}")
manifest=[]
for number in NUMBERS:
    info=selected[number]
    raw=get(info["published_image_url"])
    mime=Image.open(io.BytesIO(raw))
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
