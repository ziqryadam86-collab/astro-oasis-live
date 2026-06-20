import cloudscraper
import re
import sys

URL = "https://www.kds.tw/tv/malaysia-tv-channels-online/oasis/"

def get_link():
    # Cipta scraper yang boleh melepasi Cloudflare
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    
    try:
        # Request ke laman web utama
        res = scraper.get(URL, timeout=20)
        
        if res.status_code == 403:
            print("# Error: Akses masih disekat Cloudflare (403).", file=sys.stderr)
            return None
            
        html_content = res.text
        
        # Carian pertama: Cari link m3u8 terus
        found = re.search(r'(https?[:\/\\]+[^\s"\']+\.m3u8[^\s"\']*)', html_content, re.IGNORECASE)
        if found:
            return found.group(1).replace('\\/', '/').replace('\\', '')
            
        # Carian kedua: Cari dalam iframe jika ada
        iframe_found = re.search(r'iframe[^>]+src=["\']([^"\']+)["\']', html_content, re.IGNORECASE)
        if iframe_found:
            iframe_url = iframe_found.group(1)
            if iframe_url.startswith('//'): iframe_url = 'https:' + iframe_url
            elif iframe_url.startswith('/'): iframe_url = 'https://www.kds.tw' + iframe_url
                
            res_iframe = scraper.get(iframe_url, timeout=15)
            found_in_iframe = re.search(r'(https?[:\/\\]+[^\s"\']+\.m3u8[^\s"\']*)', res_iframe.text, re.IGNORECASE)
            if found_in_iframe:
                return found_in_iframe.group(1).replace('\\/', '/').replace('\\', '')

    except Exception as e:
        print(f"# Error: {e}", file=sys.stderr)
    return None

def main():
    link = get_link()
    if link:
        m3u8_content = f"#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-STREAM-INF:BANDWIDTH=500000,RESOLUTION=1920x1080\n{link}\n"
        
        with open("oasis.m3u8", "w", encoding="utf-8") as f:
            f.write(m3u8_content)
            
        print("Berjaya kemas kini oasis.m3u8!")
    else:
        print("# Gagal dapatkan link m3u8 baru disebabkan sekatan.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
            
