from pathlib import Path
import re
import requests

def get_tweet_image(tweet_url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(tweet_url, headers=headers, timeout=10)
        r.raise_for_status()
        print(f"Fetching {tweet_url} — status code: {r.status_code}")
        print(f"Fetched HTML for {tweet_url}:\n{r.text[:500]}")
        m = re.search(r'<meta property="og:image" content="([^"]+)"', r.text)
        if m:
            return m.group(1)
    except Exception as e:
        print(f"Failed to fetch image for {tweet_url}: {e}")
    return ""

def process_week_file(md_path):
    tweet_url_pattern = re.compile(r'\((https://x\.com/Trevorion/status/\d+)\)')
    output_lines = []
    with open(md_path, encoding="utf-8") as f:
        for line in f:
            m = tweet_url_pattern.search(line)
            if m:
                tweet_url = m.group(1)
                image_url = get_tweet_image(tweet_url)
                output_lines.append(image_url)
    # Output to gallery/ folder, similar name
    gallery_dir = Path("gallery")
    gallery_dir.mkdir(exist_ok=True)
    img_md = gallery_dir / Path(md_path).name.replace("-week-", "-images-")
    with open(img_md, "w", encoding="utf-8") as f:
        for url in output_lines:
            f.write(url + "\n")
    print(f"✅ Wrote {len(output_lines)} image URLs to {img_md}")

if __name__ == "__main__":
    # Edit this path to test with your actual weekly post
    process_week_file("_posts/2024-12-30-week-01.md")
