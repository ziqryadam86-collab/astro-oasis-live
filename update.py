import requests
import re
import sys
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

URL = "https://www.kds.tw/tv/malaysia-tv-channels-online/oasis/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.kds.tw/",
    "Origin": "https://www.kds.tw"
}

def create_session():
    session = requests.Session()
    session.headers.update(HEADERS)
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))
    return session

def get_link():
    session = create_session()
    try:
        res = session.get(URL, timeout=20)
        if res.status_code == 403:
            print("# Error: Akses disekat Cloudflare (403).", file=sys.stderr)
            return None
            
        html_content = res.text
        # Carian pertama
        found = re.search(r'(https?[:\/\\]+[^\s"\']+\.m3u8[^\s"\']*)', html_content, re.IGNORECASE)
        if found:
            return found.group(1).replace('\\/', '/').replace('\\', '')
            
        # Carian kedua (jika dalam iframe)
        iframe_found = re.search(r'iframe[^>]+src=["\']([^"\']+)["\']', html_content, re.IGNORECASE)
        if iframe_found:
            iframe_url = iframe_found.group(1)
            if iframe_url.startswith('//'): iframe_url = 'https:' + iframe_url
            elif iframe_url.startswith('/'): iframe_url = 'https://www.kds.tw' + iframe_url
                
            res_iframe = session.get(iframe_url, timeout=15)
            found_in_iframe = re.search(r'(https?[:\/\\]+[^\s"\']+\.m3u8[^\s"\']*)', res_iframe.text, re.IGNORECASE)
            if found_in_iframe:
                return found_in_iframe.group(1).replace('\\/', '/').replace('\\', '')

    except Exception as e:
        print(f"# Error: {e}", file=sys.stderr)
    return None

def main():
    link = get_link()
    if link:
        # Format teks yang awak mahukan
        m3u8_content = f"#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-STREAM-INF:BANDWIDTH=500000,RESOLUTION=1920x1080\n{link}\n"
        
        # Simpan teks ke dalam fail oasis.m3u8
        with open("oasis.m3u8", "w", encoding="utf-8") as f:
            f.write(m3u8_content)
            
        print("Berjaya kemas kini oasis.m3u8!")
    else:
        print("# Gagal dapatkan link m3u8 baru.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
