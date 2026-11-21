"""Open the answer key only after run.py has produced its candidate witnesses."""
import csv,json,hashlib
from pathlib import Path
BASE=Path(__file__).resolve().parent

def main():
    spec=json.loads((BASE/'cases.json').read_text());truth=json.loads((BASE/'truth.json').read_text())
    scores=list(csv.DictReader((BASE/'results/case_scores.csv').open()))
    ws=list(csv.DictReader((BASE/'results/witnesses.csv').open()))
    import sys
    sys.path.insert(0,str(BASE.parents[2]/'work_scripts'))
    import key2a_rebus_lock as engine
    recovery=[]
    for c in spec['primary_cases']+spec['secondary_cases']:
        expected={engine.norm_phon(x) for x in truth[c['id']]['a_forms']}&{engine.norm_phon(x) for x in truth[c['id']]['b_forms']}
        matching=[w for w in ws if w['language']==truth['language'] and w['case']==c['id'] and w['mode']=='phon_exact' and set(w['key'].split('; '))&expected]
        recovery.append(dict(case=c['id'],expected_normalized_shared_keys=sorted(expected),
            original_correct_reading=any(w['accepted_original']=='True' for w in matching),
            distinct_entry_correct_reading=bool(matching),
            matching_witnesses=len(matching),same_cluster_blocks=sum(w['accepted_original']=='False' for w in matching)))
    family_scores=list(csv.DictReader((BASE/'results/language_scores.csv').open()))
    rankings={}
    for mode in sorted({r['mode'] for r in family_scores}):
        rows=[r for r in family_scores if r['mode']==mode];best=max(int(r['primary_hits']) for r in rows)
        rankings[mode]=dict(best_score=best,winners=[r['language'] for r in rows if int(r['primary_hits'])==best],scores={r['language']:int(r['primary_hits']) for r in rows})
    ps=list(csv.DictReader((BASE/'results/permutation_controls.csv').open()))
    foil={}
    for lang in sorted({r['language'] for r in ps}):
        rr=[r for r in ps if r['language']==lang and r['full_derangement']=='True']
        foil[lang]={field:dict(hits=sum(int(r[field]) for r in rr),trials=6) for field in ['original_hits','entry_only_hits','entry_or_same_entry_hits']}
    out=dict(primary_sign_groups=3,secondary_correlated_cases=1,truth_sha256=hashlib.sha256((BASE/'truth.json').read_bytes()).hexdigest(),rankings=rankings,reading_recovery=recovery,full_derangement_foil_results=foil,
        interpretation='Known Sumerian examples, tiny illustrative sample. Automated scoring is answer-withheld, not human-blind. Scores do not date or independently establish Indus meanings. Foils are rearranged benchmark meanings, not authenticated false ancient readings.')
    (BASE/'results/scored.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(rankings=rankings,reading_recovery=recovery),indent=2))

if __name__=='__main__':main()
