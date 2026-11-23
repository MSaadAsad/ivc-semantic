"""Download pinned public Elamite CSV inputs; preserve original bytes."""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request

BASE = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--destination', type=Path, required=True)
    args = ap.parse_args()
    meta = json.loads((BASE/'inputs/source_files.json').read_text())
    args.destination.mkdir(parents=True, exist_ok=True)
    for spec in meta['files']:
        name = Path(spec['path']).name
        if name == 'PN-EWB-EJSmith.csv':
            continue  # Personal names are outside the lexical experiment.
        target = args.destination/name
        if target.exists():
            data = target.read_bytes()
        else:
            url = f'https://raw.githubusercontent.com/{meta["repository"]}/{meta["commit"]}/{spec["path"]}'
            with urllib.request.urlopen(url, timeout=60) as response:
                data = response.read()
        git_hash = hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()
        assert git_hash == spec['blob_sha'], name
        target.write_bytes(data)
        print(name, len(data), 'source identity verified')


if __name__ == '__main__':
    main()
