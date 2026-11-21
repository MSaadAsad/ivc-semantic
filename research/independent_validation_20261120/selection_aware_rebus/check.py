"""Check exhaustive reselection, failure retention, null replay and reported inference."""
import argparse
import csv
import json
import numpy as np
import run as R

def explicit(bits,poly,primary,groups,winners):
    # Candidate/normalizer loops, independent of the packed optimizer's aggregation.
    def hit(i,m):return bool(bits[m]&(1<<i) or poly&(1<<i))
    fixed=sum(hit(i,0) for i in range(48))
    sounds=sum(any(hit(i,m) for m in range(3)) for i in range(48))
    meanings=sum(any(hit(i,0) for i in groups[s]) for s in primary)
    both=sum(any(hit(i,m) for i in groups[s] for m in range(3)) for s in primary)
    global_mode=max(sum(any(hit(i,m) for i in groups[s]) for s in primary) for m in range(3))
    uncapped=sum(any(hit(i,m) for i in ids for m in range(3)) for ids in groups.values())
    naive=sum(hit(i,m) for i,m in winners)
    return [fixed,sounds,meanings,both,global_mode,min(48,uncapped),uncapped,naive]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cache',type=R.Path,required=True);args=ap.parse_args()
    frozen,cases,primary,groups=R.inventory()
    pm=[R.case_mask(groups[s]) for s in primary];am=[R.case_mask(g) for g in groups.values()]
    rng=np.random.default_rng(3710)
    for _ in range(40):
        flags=rng.random((3,len(cases)))<.08
        bits=[R.case_mask(np.flatnonzero(v)) for v in flags]
        pflags=rng.random(len(cases))<.025;poly=R.case_mask(np.flatnonzero(pflags))
        winners=R.choose_winners(bits,poly,primary,groups)
        got=R.scored_masks(bits,poly,pm,am,winners)
        assert got.tolist()==explicit(bits,poly,primary,groups,winners)
        # Duplicate source rows cannot create additional successful sign IDs.
        gg={s:list(ids) for s,ids in groups.items()};new_bits=list(bits);new_poly=poly
        for k,old in enumerate(range(0,len(cases),7)):
            new=len(cases)+k;gg[cases[old]['sign']].append(new)
            for m in range(3):
                if flags[m,old]:new_bits[m]|=1<<new
            if pflags[old]:new_poly|=1<<new
        duplicate_score=R.scored_masks(new_bits,new_poly,[R.case_mask(gg[s]) for s in primary],
            [R.case_mask(g) for g in gg.values()],winners)
        assert np.array_equal(got,duplicate_score)
    meta=json.loads((R.BASE/'results/run.json').read_text());data=np.load(R.BASE/'results/search_nulls.npz')
    assert meta['n_controls']==9999 and meta['n_source_rows']==178 and meta['n_candidate_sign_ids']==93
    assert meta['plan_sha256']==R.sha(R.BASE/'PLAN.md')
    assert meta['runner_sha256']==R.sha(R.BASE/'run.py')
    assert meta['source_cases_sha256']==R.sha(R.BASE.parent/'expanded_rebus_test/cases.json')
    assert meta['reused_engine_sha256']==R.sha(R.BASE.parent/'expanded_rebus_test/run.py')
    for p,h in {**frozen['input_sha256'],**meta['lexical_inputs']['inputs'],**meta['lexical_inputs']['code']}.items():
        assert R.sha(R.REPO/p)==h,p
    rows=list(csv.DictReader((R.BASE/'results/summary.csv').open()))
    chosen=list(csv.DictReader((R.BASE/'results/chosen_readings.csv').open()))
    promoted=list(csv.DictReader((R.BASE/'results/candidate_promotions.csv').open()))
    assert len(rows)==112 and len(chosen)==336 and len(promoted)==651
    for language,lexicon,is_de in R.E.engine.PRIMARY_7_FAMILIES:
        real=data[language+'_observed'];assert real[3]==real[7]
        assert real[3]>=max(real[0],real[1],real[2],real[4])
        for kind in R.KINDS:
            a=data[language+'_'+kind];assert a.shape==(9999,8)
            assert np.all(a[:,3]>=a[:,7]) # Full reselection always contains the real fixed recipe.
            assert np.all(a[:,3]>=a[:,1]) and np.all(a[:,3]>=a[:,2])
            assert np.all(a[:,4]<=a[:,3])
            assert np.all(a[:,5]==np.minimum(48,a[:,6]))
            assert np.all(a[:,6]>=a[:,3])
            assert np.all(a[:,:6]<=48) and np.all(a[:,7]<=48) and np.all(a[:,6]<=93)
        rr=[r for r in chosen if r['language']==language]
        assert sum(r['success']=='True' for r in rr)==real[3]
        for r in rr:
            assert cases[int(r['chosen_case_index'])]['sign']==r['sign']
        pp=[r for r in promoted if r['language']==language]
        assert sum(r['success']=='True' for r in pp)==real[6]
        assert sum(r['promoted_at_cap48']=='True' for r in pp)==real[5]
        for r in pp:assert cases[int(r['chosen_case_index'])]['sign']==r['sign']
        # Recreate stochastic draws with the source dictionary, checking graph equivalence too.
        R.E.engine.TMP_LEX=str(args.cache)
        L=R.E.engine.CleanCognateLex(language,lexicon,is_de=is_de)
        assert R.sha(args.cache/(lexicon+'.tsv'))==meta['dictionaries'][lexicon]
        A,B,P,_=R.E.match_inputs(L,cases);AP,BP=R.E.packed_columns(A),R.E.packed_columns(B)
        poly=R.case_mask(np.flatnonzero(P.diagonal()));bits=R.uniform_masks(L,AP,BP)
        winners=R.choose_winners(bits,poly,primary,groups)
        assert explicit(bits,poly,primary,groups,winners)==real.tolist()
        for mode,got in zip(R.E.MODES,bits):assert got==R.E.edge_masks(L,mode,AP,BP)[1]
        for kind in R.KINDS:
            seed=int(next(r['seed'] for r in rows if r['language']==language and r['null']==kind))
            replay=R.null_scores(L,AP,BP,poly,pm,am,winners,19,kind,seed)
            assert np.array_equal(replay,data[language+'_'+kind][:19])
        for sign,(i,m) in zip(groups,R.choose_winners(bits,poly,list(groups),groups)):
            assert cases[i]['sign']==sign
            expected=any((b|poly)&R.case_mask(groups[sign]) for b in bits)
            assert bool((bits[m]|poly)&(1<<i))==expected
    assert int(data['Dravidian_observed'][0])==38 and int(data['Sumerian_observed'][0])==11
    for row in rows:
        pi=R.POLICIES.index(row['policy']);obs=int(row['observed'])
        null=data[row['language']+'_'+row['null']][:,pi]
        assert abs(float(row['p'])-R.E.pvalue(obs,null))<1e-12
        assert int(row['exceedances'])==int(np.sum(null>=obs))
        assert abs(float(row['null_mean'])-float(null.mean()))<1e-12
    for kind in R.KINDS:
        for which,key in [(lambda r:r['primary']=='True','p_holm_primary7'),
                          (lambda r:r['valid_inferential_endpoint']=='True','p_holm_global49')]:
            rr=[r for r in rows if r['null']==kind and which(r)]
            assert np.allclose(R.E.holm([float(r['p']) for r in rr]),[float(r[key]) for r in rr])
    print('PASS: exhaustive search vs explicit loops; duplicate/failure invariants; all 112 result cells; 336 chosen readings; 651 candidates; exact null replay; source hashes; baseline reproduction; selection-aware and multiplicity calculations.')

if __name__=='__main__':main()
