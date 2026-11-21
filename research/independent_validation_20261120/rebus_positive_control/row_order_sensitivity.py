"""Post-pilot diagnostic: does reversing identical input records change the score?"""
import argparse,collections,csv,hashlib,json,re,sys
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE.parents[2]/'work_scripts'))
import key2a_rebus_lock as engine

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cache',type=Path,required=True);a=ap.parse_args()
    rev=a.cache/'reversed';rev.mkdir(exist_ok=True)
    spec=json.loads((BASE/'cases.json').read_text())['primary_cases'];rows=[]
    for family,name,de in engine.PRIMARY_7_FAMILIES:
        lines=(a.cache/(name+'.tsv')).read_text().splitlines()
        (rev/(name+'.tsv')).write_text('\n'.join(reversed(lines))+'\n')
        eids=collections.defaultdict(set)
        for line in lines:
            r=line.split('\t');eids[r[0]].add(r[1])
        for label,path in [('original',a.cache),('reversed',rev)]:
            engine.TMP_LEX=str(path);L=engine.CleanCognateLex(family,name,is_de=de)
            A=np.array([L.match_regex_bool(re.compile(c['a_de' if de else 'a_en'],re.I)) for c in spec])
            B=np.array([L.match_regex_bool(re.compile(c['b_de' if de else 'b_en'],re.I)) for c in spec])
            hits=engine.eval_edges_vectorized(L,'phon_exact',A,B)
            rows.append(dict(language=family,input_order=label,primary_hits=int(hits.sum()),hit_cases='; '.join(c['id'] for c,h in zip(spec,hits) if h),
                entries_with_multiple_source_cluster_ids=sum(len(v)>1 for v in eids.values()),
                record_multiset_sha256=hashlib.sha256('\n'.join(sorted(lines)).encode()).hexdigest()))
    with (BASE/'results/row_order_sensitivity.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    print(rows)

if __name__=='__main__':main()
