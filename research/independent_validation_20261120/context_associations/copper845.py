"""Within-copper 845 audit; see COPPER_845_PLAN.md for the specification."""
import collections, csv, hashlib, html, json, re, time
from pathlib import Path
from urllib.parse import urlencode
import numpy as np
from threadpoolctl import threadpool_limits

BASE=Path(__file__).resolve().parent; OUT=BASE/'results'; REPO=BASE.parents[2]
ITERATIONS=19999
def rows(p):
    with Path(p).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(name,rs):
    with (OUT/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rs[0]),lineterminator='\n');w.writeheader();w.writerows(rs)
def has(r,s):return s in r['signs'].split('; ')
def remainder(r):return '|'.join('-'.join(s for s in face.split('-') if s!='845') for face in r['full_text'].split('|'))
def test(rs,endpoint,controls,weighted,rng):
    labels=sorted({r[endpoint] for r in rs}); lookup={s:i for i,s in enumerate(labels)}
    y=np.array([int(has(r,'845')) for r in rs]); n=len(rs)
    weights=np.array([1/formula_counts[r['full_text']] if weighted else 1 for r in rs])
    z=np.zeros((n,len(labels)))
    if n:z[np.arange(n),[lookup[r[endpoint]] for r in rs]]=weights
    strata=collections.defaultdict(list)
    for i,r in enumerate(rs):strata[tuple(r[k] for k in controls)].append(i)
    expected=np.zeros(len(labels)); variance=np.zeros(len(labels)); movable=[]
    for ix in strata.values():
        ix=np.array(ix);nn=len(ix);m=int(y[ix].sum());v=z[ix]
        expected+=m/nn*v.sum(axis=0)
        if 0<m<nn:
            variance+=m*(nn-m)/(nn*(nn-1))*(np.sum(v*v,axis=0)-v.sum(axis=0)**2/nn)
            movable.append((ix,m))
    valid=variance>1e-12
    result=dict(endpoint=endpoint,controls=' + '.join(controls),weighting='formula_weighted' if weighted else 'objects',
                eligible_objects=n,sign845_objects=int(y.sum()),categories=len(labels),mixed_exposure_strata=len(movable),
                objects_in_mixed_strata=sum(len(ix) for ix,m in movable),statistic='',p_conditional='',p_bonferroni_12='',
                status='No comparable variation after these controls')
    if not valid.any():return result,None
    obs=z.T@y; stat=float(np.sum((obs[valid]-expected[valid])**2/variance[valid])); sims=[]
    for start in range(0,ITERATIONS,1000):
        b=min(1000,ITERATIONS-start); yy=np.tile(y,(b,1))
        for ix,m in movable:
            yy[:,ix]=0
            chosen=np.argsort(rng.random((b,len(ix))),axis=1)[:,:m]
            yy[np.arange(b)[:,None],ix[chosen]]=1
        ss=np.sum((yy@z[:,valid]-expected[valid])**2/variance[valid],axis=1);sims.append(ss)
    sims=np.concatenate(sims);p=(1+int(np.sum(sims>=stat-1e-10)))/(ITERATIONS+1)
    result.update(statistic=stat,p_conditional=p,p_bonferroni_12=min(1.,12*p),status='Exploratory conditional comparison')
    return result,sims

def main():
    global formula_counts
    started=time.monotonic();events=rows(OUT/'events.csv'); raw={r['stone_id']:r for r in rows(REPO/'work_data/sem/objects_lipi.csv')}
    cat=rows(BASE.parent/'translation_catalogue/results/all_inscriptions.csv'); byobj=collections.defaultdict(list)
    for r in cat:
        if r['catalogue']=='Lipi':byobj[r['face_id'].split('.')[0]].append(r)
    ct=[dict(r) for r in events if r['material']=='Copper' and r['kind']=='ctab']
    formula_counts=collections.Counter(r['full_text'] for r in ct)
    for r in ct:
        r['has_845']=int(has(r,'845'));r['has_407']=int(has(r,'407'))
        r['motif']=raw[r['object_id']]['ctab_animal'];r['remainder_family']=remainder(r)
        r['independently_verified_context_function']='Unknown: no specimen-level excavation-function crosswalk established'
        cr=byobj[r['object_id']][0]
        for k in ['found_at','recorded_stratigraphy','excavation_number']:r[k]=cr[k]
    assert len(ct)==150 and sum(r['has_845'] for r in ct)==29
    assert all(r['city']=='Mohenjo-daro' and r['has_407'] for r in ct if r['has_845'])
    write('copper845_all_copper_tablets.csv',ct);tax=[r for r in ct if r['has_845']];write('copper845_29_specimens.csv',tax)
    models=[['city'],['city','has_407'],['city','has_407','motif'],['city','has_407','motif','remainder_family']]
    rng=np.random.default_rng(8454072026);results=[];nulls={}
    with threadpool_limits(limits=1):
        for endpoint in ['area','recorded_layer','motif']:
            selected=[r for r in ct if r[endpoint]]
            for controls in models:
                if endpoint=='motif' and 'motif' in controls and 'remainder_family' not in controls:continue
                # Do not condition on the outcome itself; retain remainder matching for the motif audit.
                actual=[c for c in controls if not(endpoint=='motif' and c=='motif')]
                for weighted in [False,True]:
                    result,sims=test(selected,endpoint,actual,weighted,rng);results.append(result)
                    if sims is not None:nulls[str(len(results)-1)]=sims
    write('copper845_comparisons.csv',results);np.savez_compressed(OUT/'copper845_nulls.npz',**nulls)
    motifs=[]
    for motif in sorted({r['motif'] for r in ct}):
        g=[r for r in ct if r['motif']==motif];motifs.append(dict(motif=motif or 'Not recorded',with_845=sum(r['has_845'] for r in g),without_845=sum(not r['has_845'] for r in g)))
    write('copper845_motif_counts.csv',motifs)
    fam=collections.defaultdict(list)
    for r in ct:fam[r['remainder_family']].append(r)
    fr=[dict(remainder_family=k,objects=len(v),with_845=sum(r['has_845'] for r in v),without_845=sum(not r['has_845'] for r in v),references='; '.join(r['reference']+' [object '+r['object_id']+']' for r in v)) for k,v in sorted(fam.items())]
    write('copper845_remainder_families.csv',fr)
    summary=dict(copper_tablets=len(ct),copper_tablet_sites=dict(collections.Counter(r['city'] for r in ct)),
        sign845_copper_objects=len(tax),sign845_unique_recorded_formulas=len({r['full_text'] for r in tax}),
        sign845_without407=sum(not r['has_407'] for r in tax),remainder_families=len(fr),
        remainder_families_with_both_exposures=sum(r['with_845']>0 and r['without_845']>0 for r in fr),
        tax_objects_with_area=sum(bool(r['area']) for r in tax),tax_objects_with_room_or_grid=sum(bool(r['room']) for r in tax),
        tax_objects_with_recorded_layer=sum(bool(r['recorded_layer']) for r in tax),verified_function_objects=0,
        permutations=ITERATIONS,seed=8454072026,runtime_seconds=time.monotonic()-started,
        source_sha256={str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [OUT/'events.csv',REPO/'work_data/sem/objects_lipi.csv',BASE/'COPPER_845_PLAN.md']})
    (OUT/'copper845_summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
    (OUT/'COPPER_845_PLAN.md').write_text((BASE/'COPPER_845_PLAN.md').read_text())
    report(summary,ct,tax,results,motifs)
    print(json.dumps(summary,ensure_ascii=False))

def report(summary,ct,tax,results,motifs):
    lines=['# Sign 845: comparison within copper tablets','',
      '**The 29 specimens have now been individually listed. The available data still do not independently establish “845 = tax”.** All 29 are Mohenjo-daro copper tablets and all also contain sign 407. They represent 13 distinct recorded all-face inscription formulas, including damaged readings, not 29 independently different texts.','',
      '## What the narrower comparison adds','',
      f"The comparison contains {len(ct)} copper-tablet representatives: 149 from Mohenjo-daro and one from Kalibangan. Sign 845 occurs on 29; the other 121 lack it. Among the Mohenjo-daro tablets that also carry 407, the comparison is 29 with 845 versus 21 without it. The 29 are the actual observed 845 specimens; damaged copies inferred from matching texts are not added.",'',
      'After removing 845 from each inscription, **none of the 90 exact remainder families contains both a specimen with 845 and a specimen without it**. The otherwise-identical-text comparison therefore has no evidence to estimate a separate 845 effect. This does not refute the reading; it means this corpus cannot perform the requested fully matched test. Matching on the full inscription would be circular because that includes 845 itself. The remainder match avoids that circularity, but leaves no matched contrast.','',
      'The area and recorded-layer comparisons show no clear 845-specific difference. Existing motif categories do differ after controlling 407 (adjusted p=.0114 by objects), but the same comparison is weaker after weighting repeated formulas (p=.0798). For example, hare-labelled tablets are 6 with 845 versus 0 without; human/archer labels are 7 versus 3. This supports an inscription/motif grouping, not the English meaning tax; text–picture grouping was already demonstrated in the repository.','',
      '## Recorded locations','',
      f"Of the 29 specimens, {summary['tax_objects_with_area']} have an excavation-area label, {summary['tax_objects_with_room_or_grid']} have a room/grid label, and {summary['tax_objects_with_recorded_layer']} have a recorded phase/period. None has an independently verified functional classification in this analysis. Missing function is not evidence that the object came from a domestic or non-economic context.",'',
      '| Specimen | Actual recorded findspot | Recorded strata | Existing motif category |','|---|---|---|---|']
    for r in tax:
        lines.append('| '+' | '.join([r['reference']+' [object '+r['object_id']+']',r['found_at'],r['recorded_stratigraphy'],r['motif'] or 'Not recorded']).replace('| area','/ area')+' |')
    lines+=['','## Conditional comparisons','',
       'Each row compares the distribution of the named outcome between 845-present and 845-absent tablets, within the listed controls. Unknown outcomes are excluded separately. These are retrospective checks of existing labels, not new independent tax evidence. Motif labels are inherited from the existing semantic catalogue; they have not been independently reassigned here.','',
       '| Outcome | Controls | Eligible objects (845 present) | Objects in groups with both readings | Adjusted p, objects | Adjusted p, formula weighting |','|---|---|---|---|---|---|']
    objects=[r for r in results if r['weighting']=='objects']
    for r in objects:
        w=next(q for q in results if q['endpoint']==r['endpoint'] and q['controls']==r['controls'] and q['weighting']=='formula_weighted')
        fmt=lambda q:format(q['p_bonferroni_12'],'.4g') if q['p_bonferroni_12']!='' else 'No comparable variation'
        lines.append('| '+' | '.join([r['endpoint'],r['controls'],f"{r['eligible_objects']} ({r['sign845_objects']})",str(r['objects_in_mixed_strata']),fmt(r),fmt(w)])+' |')
    lines+=['','Method: 19,999 within-control-group label permutations, plus-one p values; Bonferroni factor 12 over the planned outcome/control combinations. Statistic is the sum of squared category residuals divided by their conditional variances. Both counts and complete-formula weighting are reported. All conditional null statistics are archived in `copper845_nulls.npz`. The weighting sensitivity does not create independent specimens or supply missing archaeological functions. See [the specification](../COPPER_845_PLAN.md).','',
       '## What was already done','',
       'The May 31 report `risky_copper_register_subsigns_095_845_20260531.json` already found 15 distinct 845 texts, six on Copper/TAB:C; after removing 407, four 845 texts remained and none was Copper/TAB:C. Its text unit and input snapshot differ from this all-face physical-object table. The original `vector4_targeted_context_nulls_20260531.md` already found that 061–845/copper did not survive site/type controls. The November 17 `copper_2_pairs.py` already tested text–picture agreement, and `copper_6_spots.py` already tested copper-set findspot clustering. Those are prior findings, not discoveries of this extension.','',
       'The added work is the explicit specimen list, observed 845/407 cross-tabulation, outcome-specific nested controls, missing-context accounting, formula-weighted sensitivity and direct audit of whether a 845-removed inscription has a comparable negative specimen.','',
       '## Archaeological source checks','',
       '- **A real economic context exists, but is not one of the 29 tax-sign tablets.** Mackay’s primary report, Chapter XV, p. 243, identifies stone/jewellery manufacture and fourteen weights plus copper scale pans in Chanhu-daro square 9/D, locus 215. The current catalogue places seal C-22 at “loc. 215sq. 9/D”. It is a steatite seal with signs `790-390-ALT-390-440`, with neither 845 nor 407. The shared locus supports a source-checkable script/economic-context link; it does not demonstrate taxation or corroborate 845. The exact seal’s original excavation-entry/level should still be checked. [Primary report, PDF page 9](https://richardsproat.com/indus_weights/Hemmy_Hall-1943-weights-Chanhudaro-Mackay.pdf#page=9).',
       '- **Harappa is a different copper-object tradition.** The excavators identify H2000-4498/9889-01 as a raised-script copper tablet from Trench 43. It joins to catalogue H-2251 in the broader table, whose current proposed values include the bangle sign 790. It is outside the Mohenjo-daro 845 set and outside this ctab comparison; the broad Copper material category must not conceal that distinction. [HARP specimen description](https://www.harappa.com/slide/copper-tablet).',
       '- Kenoyer’s *Measuring the Harappan World*, p. 109, describes seals and weights concentrated near gateways and craft areas. That supports an economic context for some objects, not specimen-level evidence that any of these 29 tablets recorded taxes. [Excavator’s study](https://www.harappa.com/sites/default/files/pdf/Kenoyer%202010%20Measuring%20the%20Harappan%20World.pdf#page=5).',
       '- Mukhopadhyay’s 2023 tax/licensing proposal is another interpretation, not an independently verified label to assign to these tablets. [Published proposal](https://www.nature.com/articles/s41599-023-02320-7).','',
       '## What would change the reading’s evidential status','',
       'Recover a specimen-level crosswalk from the original Mohenjo-daro excavation entries and plans to independently documented workshops, gateways, storage and domestic deposits, preserving uncertainty and secondary deposition. Assign those functions without seeing 845 or its proposed meaning. Freeze a directional prediction for 845, then compare fresh or genuinely withheld copper tablets within the same genre and against 407/motif/formula alternatives. This work has not supplied that independent semantic evidence; room numbers alone cannot supply it.','',
       'Files: [all 29 specimens](copper845_29_specimens.csv), [all 150 comparison tablets](copper845_all_copper_tablets.csv), [all comparisons](copper845_comparisons.csv), [all remainder families](copper845_remainder_families.csv), [motif counts](copper845_motif_counts.csv), [provenance/counts](copper845_summary.json).']
    lines=[line.replace('../COPPER_845_PLAN.md','COPPER_845_PLAN.md') for line in lines]
    (OUT/'COPPER_845.md').write_text('\n'.join(lines)+'\n')
    # Render this report's restricted headings, paragraphs, tables and links without another dependency.
    def inline(s):
        s=html.escape(s)
        s=re.sub(r'\[([^]]+)\]\(([^)]+)\)',r'<a href="\2">\1</a>',s)
        s=re.sub(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>',s)
        return re.sub(r'`([^`]+)`',r'<code>\1</code>',s)
    parts=[];intable=False
    for line in lines:
        if line.startswith('|'):
            if not intable:parts.append('<table>');intable=True
            cells=line.strip('|').split('|')
            if all(re.fullmatch(r'\s*[-:]+\s*',c) for c in cells):continue
            parts.append('<tr>'+''.join('<td>'+inline(c.strip())+'</td>' for c in cells)+'</tr>');continue
        if intable:parts.append('</table>');intable=False
        if line.startswith('#'):
            level=len(line)-len(line.lstrip('#'));parts.append(f'<h{level}>'+inline(line.lstrip('# '))+f'</h{level}>')
        elif line:parts.append('<p>'+inline(line)+'</p>')
    if intable:parts.append('</table>')
    body='\n'.join(parts)
    (OUT/'copper845.html').write_text('<!doctype html><meta charset="utf-8"><title>Sign 845 and copper tablets</title><style>body{font:17px/1.5 system-ui;margin:35px auto;max-width:1250px;padding:0 25px;color:#192f3a}table{border-collapse:collapse;font-size:14px;width:100%}td,th{border:1px solid #c8d5db;padding:9px;text-align:left;vertical-align:top}th{background:#e8f1f4}a{color:#17618e}code{white-space:normal}</style><a href="associations.html">All word/context comparisons</a>'+body)

if __name__=='__main__':main()
