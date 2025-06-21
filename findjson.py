#!/usr/bin/env python3

import argparse
import subprocess
import requests
import os
from urllib.parse import urlparse

def banner():
    print(r"""
  ______ _           _        _                 
 |  ____(_)         | |      | |                
 | |__   _ _ __   __| |      | |___  ___  _ __  
 |  __| | | '_ \ / _` |  _   | / __|/ _ \| '_ \ 
 | |    | | | | | (_| | | |__| \__ \ (_) | | | |
 |_|    |_|_| |_|\__,_|  \____/|___/\___/|_| |_|
                                                
             created by sudosama-cc
    """)

def fetch_waybackurls(domain):
    try:
        print(f"[+] Wayback: {domain}")
        r = requests.get(f"https://web.archive.org/cdx/search/cdx?url={domain}/*&output=text&fl=original&collapse=urlkey", timeout=900)
        if r.status_code == 200:
            return r.text.splitlines()
        return []
    except Exception as e:
        print(f"[-] Wayback error: {e}")
        return []

def fetch_gau(domain):
    try:
        print(f"[+] gau: {domain}")
        output = subprocess.check_output(
    	    ["gau", domain],
            text=True,
            stderr=subprocess.DEVNULL)

        return output.splitlines()
    except FileNotFoundError:
        print("[-] gau not found, skipping gau")
        return []
    except Exception as e:
        print(f"[-] gau error: {e}")
        return []

def extract_json_urls(urls):
    return sorted({u for u in urls if ".json" in u.lower()})

def process_domain(domain, out_dir):
    urls = fetch_waybackurls(domain) + fetch_gau(domain)
    json_urls = extract_json_urls(urls)

    parsed = urlparse(domain)
    fname = parsed.netloc or parsed.path
    fpath = os.path.join(out_dir, f"{fname}_json.txt")
    
    if json_urls:
        with open(fpath, "w") as f:
            f.write("\n".join(json_urls))
        print(f"[+] Saved {len(json_urls)} URLs → {fpath}")
    else:
        print(f"[-] No JSON URLs found for {domain}")

def main():
    banner()
    parser = argparse.ArgumentParser(description="Hey JSON - Find .json URLs from passive sources.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-d", "--domain", help="Target domain")
    group.add_argument("-list", "--listfile", help="List of domains (one per line)")
    parser.add_argument("-o", "--output", default="findjson_output", help="Output folder")

    args = parser.parse_args()
    os.makedirs(args.output, exist_ok=True)

    domains = []
    if args.domain:
        domains = [args.domain.strip()]
    else:
        with open(args.listfile, "r") as f:
            domains = [line.strip() for line in f if line.strip()]

    for d in domains:
        process_domain(d, args.output)

if __name__ == "__main__":
    main()
