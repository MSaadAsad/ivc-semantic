"""Extract factual register fields from cached public viewer pages, not a new reading.

The complete report remains in the external source cache. Only specimen facts and
paraphrased attachment observations are imported into the research dataset.
"""
import argparse
import csv
import gzip
from html.parser import HTMLParser
import json
from pathlib import Path
import re

BASE = Path(__file__).resolve().parent
OUT = BASE / 'western_sites_inputs'
SOURCE = 'https://www.scribd.com/document/262316120/Excavations-at-Dholavifra-1989-2005-RS-Bisht-2015'


class Text(HTMLParser):
    def __init__(self):
        super().__init__();self.tokens=[]
    def handle_data(self, data):
        if data.strip():self.tokens.append(data.strip())


def write(name, rows):
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)


def extract(cache, metadata):
    tokens=[]
    for page in range(326,348):
        raw=(cache/f'page-{page}.jsonp').read_bytes()
        text=(gzip.decompress(raw) if raw[:2]==b'\x1f\x8b' else raw).decode()
        body=json.loads(text[text.find('(')+1:text.rfind(')')])[0]
        parser=Text();parser.feed(body)
        printed=int(parser.tokens[0]);assert printed==page-18
        tokens.extend((printed,t) for t in parser.tokens)
    starts=[(i,int(t[:-1])) for i,(p,t) in enumerate(tokens) if re.fullmatch(r'\d{1,2}\.',t)]
    assert [n for i,n in starts]==list(range(1,62))
    source=[]
    areas=['Promenade to the west of East Reservoir','South Reservoir','East Reservoir','Middle Town','Lower Town','Annexe','Bailey','Castle']
    number=r'[+-]?\s*\d+(?:\.\d+)?'
    for j,(i,serial) in enumerate(starts):
        chunk=tokens[i+1:starts[j+1][0] if j+1<len(starts) else len(tokens)]
        raw=' '.join(t for p,t in chunk)
        accession=raw.split()[0];assert accession.isdigit()
        loc=re.search(r'Locus:\s*(.*?)(?=Obv\.|Rev\.|Curiously|$)',raw)
        loc=loc.group(1) if loc else ''
        # Remove layout headers carried over when a specimen spans two pages.
        loc=re.split(r'\s+(?:IV/V|III/IV|VI|IV|V)\s+\d{3}\s+Sl\.',loc)[0].strip()
        area=next((a for a in areas if loc.startswith(a)), '')
        remainder=loc[len(area):].strip(' ,')
        grid=re.split(r',?\s*(?:stratum\s*[:;]?|depth\s*:?|location:|Mixed debris)',remainder,flags=re.I)[0].strip(' ,.')
        if grid=='surface':grid=''
        strata=re.search(r'stratum\s*[:;]?\s*(.*?)(?=,?\s*depth|,?\s*location:|$)',loc,re.I)
        depth=re.search(r'(?:depth\s*:?|location:)\s*('+number+r'(?:\s*(?:-|to)\s*'+number+r')?)',loc,re.I)
        phase=re.findall(r'(?<![A-Za-z])(?:III/IV|IV/V|VI|IV|V)(?![A-Za-z])',raw)
        source.append(dict(source_record=f'DHR2015-{serial:02}',source_serial=serial,accession=accession,
                           site='Dholavira',printed_pages='; '.join(map(str,sorted(set(p for p,t in chunk)))),
                           source_area=area,source_grid=grid,source_stratum=strata.group(1).strip(' ,.') if strata else '',
                           source_depth=re.sub(r'\s+','',depth.group(1)) if depth else '',
                           depth_unit='cm' if depth and re.search(r'\bcm\b',loc) else 'not stated',
                           source_period=phase[-1] if phase else 'undetermined',surface_find='surface' in loc.lower(),
                           source_url=SOURCE,source_section='8.2.4 sealing register, printed pp309-329',
                           newly_transcribed_signs='',source_status='published excavation register; classifications kept qualified'))
    write('dholavira2015_register.csv',source)
    with metadata.open() as f:
        old=list(csv.DictReader(f))
    selected=[r for r in old if r['site'] in {'Dholavira','Gola Dhoro (Bagasra)','Shikarpur'}]
    fields=['id','cisi','site','area-section','block-house','room-grid','excavation-idno','time','period','phase','depth','type','text','preservation','complete','horizontal(mm)','vertical(mm)','thickness(mm)']
    write('existing_catalogue_subset.csv',[{k:r[k] for k in fields} for r in selected])
    print(json.dumps(dict(source_entries=len(source),distinct_accessions=len({r['accession'] for r in source}),existing_metadata_faces=len(selected)),indent=2))


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--page-cache',type=Path,required=True);ap.add_argument('--metadata',type=Path,required=True);args=ap.parse_args()
    extract(args.page_cache,args.metadata)
