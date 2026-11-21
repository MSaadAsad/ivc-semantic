"""Full Grignard OCR screen; paragraph co-occurrence is a review queue, not a match."""
import argparse,csv,json,re
from pathlib import Path
from analyze import BASE, meaning, writecsv

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--text',type=Path,required=True);a=ap.parse_args()
    text=a.text.read_text();blocks=re.split(r'\n\s*\n',text)
    claims=json.loads((BASE/'claims.json').read_text())['claims'];hits=[];counts=[]
    for c in claims:
        if c['kind'] not in ['bridge','polysemy']:continue
        nn=0
        for i,b in enumerate(blocks):
            t=re.sub(r'\s+',' ',b)
            if meaning(t,c['a']) and meaning(t,c['b']):
                hits.append(dict(claim=c['id'],ocr_block=i,first_line=b.splitlines()[0],text=t,
                    status='Unscored paragraph co-occurrence: may contain examples, multiple entries or a split entry.'))
                nn+=1
        counts.append(dict(claim=c['id'],candidate_blocks=nn))
    writecsv(BASE/'results/kurukh_ocr_candidate_queue.csv',hits)
    out=dict(source='Grignard 1924, An Oraon-English Dictionary, complete public scan OCR',
        bytes=a.text.stat().st_size,characters=len(text),paragraph_blocks=len(blocks),
        candidate_claim_block_pairs=len(hits),distinct_candidate_blocks=len({r['ocr_block'] for r in hits}),
        interpretation='Full-text search only. Paragraph blocks are NOT headwords. No OCR candidate is added to fixed-family scores without etymological identification.',
        by_claim=counts)
    (BASE/'results/kurukh_ocr_screen.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='by_claim'},indent=2))

if __name__=='__main__':main()
