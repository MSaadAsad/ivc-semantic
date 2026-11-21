#!/usr/bin/env python3
"""Recompute report arithmetic and inspect specifications; no dictionary reruns."""
import ast,math,json,csv
from collections import Counter
from scipy.stats import chi2, fisher_exact
import validate as v

def literal(name,file):
    tree=ast.parse((v.REPO/file).read_text());return ast.literal_eval(next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets)))
def main():
    z=json.loads((v.REPO/'work_data/key6c/combined_3wave_meta_stats.json').read_text());da=z['disjointness_audit'];w4=literal('TRACK_A_WAVE4_SPECS','work_scripts/key6a_wave4_strike.py');sets=[set(da['wave%d_key%s_signs'%(i,s)]) for i,s in [(1,'2a'),(2,'4b'),(3,'5a')]]
    overlaps={str(i+1):sorted(sets[i]&{r[0] for r in w4}) for i in range(3)}
    r=z['meta_7family']['strictly_disjoint_12_24_8']['phon_stem']['Dravidian']; ps=[r['wave%d_p'%i] for i in range(1,4)];stat=-2*sum(math.log(p) for p in ps)
    summaries=[]
    key={r['item']:r for r in v.read('work_data/decoy/KEY_do_not_open.csv')}
    print('decoy key columns',list(next(iter(key.values()))),flush=True)
    for file,field in [('results_A.csv','outcome'),('results_B.csv','outcome'),('replay_A.csv','final'),('replay_B.csv','final')]:
        rows=v.read('work_data/decoy/'+file);statuses=Counter(r[field] for r in rows);summaries.append({'file':file,'n':len(rows),'outcomes':dict(statuses)})
    wave2=v.read('work_data/key4b/test4b1_top30_sign_table.csv');prom=[r for r in wave2 if r['status']=='building on it']
    v.save('reported_claims_arithmetic.json',{'note':'Stored outputs plus code/specification inspection only; dictionary shuffles were not independently rerun in this continuation.','fisher_inputs':ps,'fisher_statistic':stat,'fisher_independence_reference_p':float(chi2.sf(stat,6)),'fisher_bonf7_reference_p':float(min(1,7*chi2.sf(stat,6))),'fisher_caveat':'Distinct signs do not imply independent statistics because shared dictionary entries/domains and adaptive selection can couple waves. A valid joint-null/selection-aware rerun remains necessary.','wave4_signs':[r[0] for r in w4],'wave4_overlap_with_prior_TESTED_signs':overlaps,'decoy_output_counts':summaries,'wave2_promoted_n':len(prom),'wave2_promoted_stem_p_below_0_05':sum(float(r['p_shuf_phonst'])<.05 for r in prom),'wave2_promoted_stem_bonf30':sum(float(r['p_shuf_phonst'])<.05/30 for r in prom),'family4_stored_table':v.read('work_data/key6a/trackA_7family_5000shuf.csv')})
if __name__=='__main__':main()
