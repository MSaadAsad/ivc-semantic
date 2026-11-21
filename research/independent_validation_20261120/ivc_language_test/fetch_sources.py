"""Fetch checksum-pinned source files into an external cache, not the repository."""
import argparse, hashlib, json, urllib.request
from pathlib import Path
BASE=Path(__file__).resolve().parent

def get(url,path,sha):
    if not path.exists():
        path.parent.mkdir(parents=True,exist_ok=True)
        with urllib.request.urlopen(url,timeout=120) as r:path.write_bytes(r.read())
    actual=hashlib.sha256(path.read_bytes()).hexdigest()
    if actual!=sha:raise ValueError(f'Source changed: {path}: {actual} != {sha}')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cache',type=Path,required=True);a=ap.parse_args()
    manifest=json.loads((BASE/'sources.json').read_text());root=a.cache/manifest['commit']
    for r in manifest['files']:get(r['url'],root/r['path'],r['sha256'])
    for r in manifest['additional_sources']:get(r['url'],a.cache/r['path'],r['sha256'])
    f=manifest['font'];font=a.cache/'sign-font/indus-font.woff2'
    get(f"https://raw.githubusercontent.com/Cuuper22/ivc/{f['commit']}/{f['path']}",font,f['sha256'])
    from fontTools.ttLib import TTFont
    tt=TTFont(font,recalcTimestamp=False);tt.flavor=None;tt.save(font.with_suffix('.ttf'))
    print(root)

if __name__=='__main__':main()
