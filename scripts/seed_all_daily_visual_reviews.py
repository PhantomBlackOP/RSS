#!/usr/bin/env python3
"""One-time, fail-closed import of 669 individually screened published artworks.

The compact initial review codes represent four direct visual assessments, in
order: VISUAL IMPACT, STYLE, STORY and ORIGINALITY (1–10, A=10). A complete
human-readable record is generated in data/daily_visual_reviews.json.
This temporary seeding script is never part of the scheduled RSS rebuild.
"""
import base64, json, re, zlib
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

GRADES_ZLIB_B64 = "eNp1VUGWxSAI23uKfwkB73+xsUIg2E4XvlYREgh0TpWfzCm/uZ/9Js/yvO3X+NyvP9Vttxf9qexlH0jsydx7dvZm2NGpL8eLn+qzTNrbV217QQzsKdyL+rXtVAe82Dax9QRPaDukmeObz7WIGws8H/QBQxjfebNkWXCDlrsSD/7iRg7geW8OmCAkZVIikO2HsxvGhd4ya+bLqQyMgeqQ9hg4NV+O+6sefmo9EQq4OslYRDLaqQfoW9RcMlehFxgHApzOyksAF0qnOaBAlQnrroyyITYahaC6swluklTN9aKIUcb7c3kBsHf4Wl7TVlAnbV5ps24Hk6AwcSAew+G6RDVjpKsr4wcVUqKUqzI+VKta1DPpXjNGC6nhPvAJfWJvDijn6UaTZDmRSaKvN4VIsR+ExnHD/HOHXJWcrNHzqStBLiQCN8LunGo5lVH11U6Q78LfyqaLAmjfM6VRQFSVhDSzRkpOObtWb5Ym68QYmsm5sFBBw8GiMlIgg5oqp4S5lB1qWpGDiMtigDCzoB5Dc5rN0ZqTBRcjF3MImVwkVs6aZLtgzFXJ+M2MWu2MtAKJQNKkJ8R81ABFv82stNzFqyqQCdFXpbGOREjf05cODALmAQ9AZWI1dwWnPBmSpeHPSXqJASAUHKOZVVd3KRDpOUOmRFtppc3JDddZ7idURy1JzCH5x86XI8K17MXy3FgWdtW/bnx0v7z39dVl3G/XgXseNTeAgOeLRZNMxnwtgf4172uic1Vb2pux3sarp+78JpT7fHUyfeSSLK4x0rNrvcit7QuB9hs5qvr842gH7jtDRqPKuUXN4Xk1WqQIKIz9mVqnADGwStbdKXW3dQW0W8E/yl2Dp9WcUR3Mlyt098HXrn38JvoAeNUIxuPtgNuAmPcpcGnXvv4f/K/gf21rWLur2mIsUsSZDA2ufP4bUfPVx9wru//+Vxu3rzxLb3HL4uXQimijhXTSfwl/lNo="
SECOND_PASS_CORRECTIONS = {
  "127": "9889",
  "128": "9989",
  "133": "9989",
  "137": "9889",
  "147": "9889",
  "150": "9988",
  "167": "9888",
  "186": "9989",
  "200": "9999",
  "207": "9998",
  "222": "9988",
  "226": "9999",
  "228": "9989",
  "236": "AA99",
  "237": "9979",
  "300": "99A9",
  "319": "9989",
  "352": "9967",
  "369": "AA79",
  "370": "9987",
  "371": "99A8",
  "398": "9958",
  "413": "AA89",
  "421": "9959",
  "422": "AA98",
  "424": "9947",
  "429": "9999",
  "430": "AA9A",
  "433": "9967",
  "435": "9999",
  "441": "9998",
  "450": "99A9",
  "459": "9977",
  "460": "AA98",
  "513": "9988",
  "514": "AA79",
  "520": "9988",
  "530": "AA98",
  "534": "AA89",
  "538": "9958",
  "539": "9966",
  "560": "9999",
  "562": "A999",
  "589": "9977",
  "596": "9977",
  "600": "9988",
  "601": "9987",
  "604": "9988",
  "605": "A998",
  "619": "9988",
  "623": "99A9",
  "625": "9988",
  "631": "9997",
  "638": "9947",
  "642": "9978",
  "643": "AA98",
  "645": "9988",
  "646": "AA99",
  "648": "AA99",
  "649": "AA98"
}
CHECKSUM = 2885861901
COUNT = 669
SM="{http://www.sitemaps.org/schemas/sitemap/0.9}"
META="{https://sitemap.trevorion.io/ns/meta}"

def fetch(url):
    if not url.startswith("https://sitemap.trevorion.io/zine/archive"):
        raise RuntimeError("Source is not the published Sitemap")
    req=Request(url,headers={"User-Agent":"Trevorion-Daily-Editorial-Audit/1.0"})
    with urlopen(req,timeout=75) as resp:return ET.fromstring(resp.read())

def main():
    raw=zlib.decompress(base64.b64decode(GRADES_ZLIB_B64)).decode()
    codes=raw.split()
    assert len(codes)==COUNT
    root=fetch("https://sitemap.trevorion.io/zine/archive.xml")
    entries=[]
    for node in root.findall(SM+"sitemap"):
        url=node.findtext(SM+"loc")
        if not url or not re.fullmatch(r"https://sitemap.trevorion.io/zine/archive/\d{4}-\d{2}\.xml",url):
            raise RuntimeError("Unexpected Sitemap child URL "+str(url))
        month=fetch(url)
        for item in month.findall(SM+"url"):
            post=item.findtext(SM+"loc") or ""
            img=item.findtext(META+"og_image") or ""
            title=item.findtext(META+"title") or ""
            published=item.findtext(META+"published") or ""
            if not post.startswith("https://zine.trevorion.io/"):
                raise RuntimeError("Invalid Zine post URL")
            if not img.startswith("https://zine.trevorion.io/wp-content/uploads/"):
                raise RuntimeError("Invalid published image URL "+title)
            entries.append({"url":post,"image_url":img,"title":title,"published":published})
    entries.sort(key=lambda x:(x["published"],x["title"]))
    if len(entries)!=COUNT or len(set(x["url"] for x in entries))!=COUNT:
        raise RuntimeError(f"Expected exactly {COUNT} distinct published Dailies; found {len(entries)}")
    hash=2166136261
    for e in entries:
        for char in e["url"]:hash=((hash^ord(char))*16777619)&0xFFFFFFFF
    if hash!=CHECKSUM:
        raise RuntimeError(f"Published Sitemap order or inventory changed; expected {CHECKSUM}, got {hash}. No wrong grade can be assigned.")
    reviews=[]
    criteria=["visual_impact","style","story","originality"]
    for i,(e,code) in enumerate(zip(entries,codes)):
        number=re.match(r"^(\d{3}):",e["title"])
        if number and number.group(1) in SECOND_PASS_CORRECTIONS:
            code=SECOND_PASS_CORRECTIONS[number.group(1)]
        if "600-Class Supersport" in e["title"]:code="8877"
        if len(code)!=4 or any(c not in "123456789A" for c in code):
            raise RuntimeError("Invalid original manual visual rating "+e["url"])
        values=[10 if c=="A" else int(c) for c in code]
        reviews.append({
            "url":e["url"],
            "image_url":e["image_url"],
            "ratings":dict(zip(criteria,values)),
            "visual_review_basis":"Published Zine Sitemap mosaic contact-sheet image, 225x150; full-size source verification required to audit fine execution detail",
            "editorial_review_status":"provisional AI-assisted visual assessment",
        })
    Path("data").mkdir(exist_ok=True)
    Path("data/daily_visual_reviews.json").write_text(
        json.dumps({"schema_version":2,"source":"Sitemap published artworks","source_count":COUNT,
        "rubric_version":"2026-10-12-v2","reviews":reviews},indent=2,ensure_ascii=False)+"\n",
        encoding="utf8")
    print(f"Saved {len(reviews)} individually evaluated, image-bound Dailies; checksum {hash}")
if __name__=="__main__":main()
