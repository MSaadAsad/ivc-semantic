"""Post-pilot diagnostic: apply the same cluster-gate ablation to the ORIGINAL 12-pair panel.
This is not a corrected etymology, new preregistered result, or full Key6 rerun.
"""
import argparse,csv,sys,re
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE.parents[2]/'work_scripts'))
import key2a_rebus_lock as engine

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cache',type=Path,required=True);a=ap.parse_args();engine.TMP_LEX=str(a.cache)
    pairs=engine.CLEAN_WAVE2B_12;rows=[]
    for family,name,de in engine.PRIMARY_7_FAMILIES:
        L=engine.CleanCognateLex(family,name,is_de=de)
        A=np.array([L.match_regex_bool(re.compile(p[3] if de else p[2],re.I)) for p in pairs])
        B=np.array([L.match_regex_bool(re.compile(p[5] if de else p[4],re.I)) for p in pairs])
        for mode in ['phon_exact','phon_stem','ascii_exact']:
            original=engine.eval_edges_vectorized(L,mode,A,B)
            U,V=L.edges[mode]
            ablated=((A[:,U]&B[:,V])|(A[:,V]&B[:,U])).any(axis=1) if len(U) else np.zeros(len(pairs),bool)
            rows.append(dict(language=family,mode=mode,n_cases=len(pairs),original_hits=int(original.sum()),distinct_entry_hits=int(ablated.sum()),
                original_signs='; '.join(str(pairs[i][0]) for i,h in enumerate(original) if h),distinct_entry_signs='; '.join(str(pairs[i][0]) for i,h in enumerate(ablated) if h)))
    with (BASE/'results/indus12_cluster_sensitivity.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    print([r for r in rows if r['mode']=='phon_exact'])

if __name__=='__main__':main()
