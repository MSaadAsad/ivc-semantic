"""Readable counts, corrected comparisons and links to actual findspots."""
import csv, html, json, re
from pathlib import Path
from urllib.parse import urlencode
BASE=Path(__file__).resolve().parent;OUT=BASE/'results'
def rows(name):
    with (OUT/name).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def write(name,rs):
    with (OUT/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rs[0]),lineterminator='\n');w.writeheader();w.writerows(rs)
stats=rows('all_associations.csv');lookup={(r['family'],r['word_id'],r['target']):r for r in stats}
summary=json.loads((OUT/'summary.json').read_text())
def occurrence_url(r):
    params={'sign':','.join(r['signs'].split('; '))}
    f=r['family'];target=r['target']
    if f=='material':params['material']=target
    elif f=='city':params['city']=target
    elif f=='depth':params['city']='Mohenjo-daro'
    elif f in {'excavation_area','room_or_building'}:
        parts=target.split(' | ');params['city']=parts[0]
        for p in parts[1:]:
            for prefix,key in [('area ','area'),('block/house ','block'),('room/grid ','room')]:
                if p.startswith(prefix) and p[len(prefix):]!='?':params[key]=p[len(prefix):]
    elif f=='recorded_layer':
        city,levels=target.split(' | ',1);params['city']=city
        for p in levels.split('; '):
            k,v=p.split('=',1);params[k]=v
    return '../../translation_catalogue/results/catalogue.html?'+urlencode(params)
allrows=[]
for family in ['material','city','excavation_area','room_or_building','recorded_layer','depth']:
    for d in rows(family+'_descriptive.csv'):
        s=lookup.get((family,d['word_id'],d['target']))
        if s:
            d.update({k:s[k] for k in ['standardized_effect','p_conditional','p_FWER_six_axes','formula_weighted_p_FWER_six_axes','mean_local_depth_rank_word','mean_local_depth_rank_other']})
            p=float(s['p_FWER_six_axes']);wp=float(s['formula_weighted_p_FWER_six_axes'])
            d['result']='Passes the first check; does not pass the repeated-text check' if p<.05 and wp>=.05 else ('Passes both checks' if p<.05 and wp<.05 else 'Not clear after accounting for all comparisons')
        else:
            d.update({k:'' for k in ['standardized_effect','p_conditional','p_FWER_six_axes','formula_weighted_p_FWER_six_axes','mean_local_depth_rank_word','mean_local_depth_rank_other']})
            d['result']='Too few objects for an adjusted comparison' if int(d['word_events'])<5 else {
                'material':'Cannot separate material from object type/site',
                'city':'Cannot separate site from object type/material',
                'excavation_area':'Cannot separate area from the other recorded features',
                'room_or_building':'No comparable objects from different rooms/buildings',
                'recorded_layer':'No comparable objects from different recorded layers',
                'depth':'Not enough local depth variation'}[family]
        d['occurrences_url']=occurrence_url(d);allrows.append(d)
allrows.sort(key=lambda r:(float(r['p_FWER_six_axes']) if r['p_FWER_six_axes'] else 2,r['family'],r['proposed_meaning'],r['target']))
write('all_descriptive_and_adjusted_associations.csv',allrows)
selected=[]
for family,word,target in [('material','845_vari','Copper'),('material','790_valai','Copper'),('city','700_ala','Harappa'),('material','700_ala','Faience'),('excavation_area','176_irai','Harappa | area FTrench I')]:
    r=next((x for x in allrows if x['family']==family and x['word_id']==word and x['target']==target),None)
    if r:selected.append(r)
lines=['# Proposed words, materials and recorded findspots','',
       '**The descriptive patterns are real, but the stricter comparisons are less decisive.** The proposed tax/levy sign is concentrated on copper objects, and the proposed measure sign is concentrated at Harappa. Those patterns overlap object-type and material differences. Two contrasts pass the primary whole-screen cutoff; neither remains below 0.05 when repeated complete inscription formulas are downweighted.','',
       'The screen uses **4,476 Lipi physical-object / known-copy-batch representatives**, combines all faces of each object, and tests **81 proposed word/allograph groups**. It evaluates **7,773 contrasts**, using **49,999 conditional permutations** per axis and maximum-statistic correction within each axis plus correction across all six axes. These are retrospective associations, not independently established translations.','',
       '## Concrete descriptive examples','',
       '| Proposed word | Material or recorded location | Among word-bearing objects | Among other eligible objects | Controlled comparison |',
       '|---|---|---|---|---|']
for r in selected:
    a=int(r['observed_word_target_events']);n=int(r['word_events']);c=int(r['other_target_events']);nn=int(r['other_events'])
    status=r['result'] if r['adjustable']=='False' else 'Whole-screen p='+format(float(r['p_FWER_six_axes']),'.4g')+'; formula-weighted p='+format(float(r['formula_weighted_p_FWER_six_axes']),'.4g')
    lines.append('| '+ ' | '.join([r['proposed_meaning']+' ('+r['proposed_root']+')',r['target'].replace('|','/'),f'{a}/{n} ({a/n:.1%})',f'{c}/{nn} ({c/nn:.1%})',status])+' |')
lines+=['','A large raw percentage is not an independent material or city effect. For example, all 29 copper occurrences of the tax/levy group are already expected after matching on site, object kind and inscription-length band. The present data cannot separate that material association from those factors.','',
        '## The two primary corrected contrasts','',
        '| Proposed reading | Recorded pattern | Whole-screen p | Formula-weighted whole-screen p |',
        '|---|---|---|---|']
for r in stats:
    if float(r['p_FWER_six_axes'])>=.05:continue
    pattern=(f"{r['observed_word_target_events']}/{r['word_events']} are {r['target']}; matched expectation {float(r['expected_word_target_events']):.2f}" if r['family']!='depth' else f"Mean within-area depth percentile {float(r['mean_local_depth_rank_word']):.1%}, versus {float(r['mean_local_depth_rank_other']):.1%} for other objects; lower is shallower")
    lines.append('| '+' | '.join([r['proposed_meaning'],pattern,format(float(r['p_FWER_six_axes']),'.4g'),format(float(r['formula_weighted_p_FWER_six_axes']),'.4g')])+' |')
lines+=['','No city, excavation-area, room/building or recorded-layer contrast passes the stated primary whole-screen correction. That is not proof that those associations are absent. Sparse contexts and correction across thousands of contrasts limit sensitivity.','',
        'The numeral-seven depth pattern is a relationship with **recorded excavation depth**, not a dated language change. Depths are ranked only within the same Mohenjo-daro excavation area; the calculation does not equate depth with a calendar date or compare metres across unrelated areas.','',
        '## Actual findspots behind the primary findings','',
        'All matching analysed objects and faces are released in `all_finding_occurrences.csv`. For example:','']
occs=rows('all_finding_occurrences.csv')
for r in [r for r in occs if r['proposed_meaning']=='bangle'][:5]:lines.append('- **'+r['reference']+'**: '+r['found_at']+'. '+r['recorded_stratigraphy']+'. Material: '+r['material']+'.')
lines+=['','## What was controlled','',
        '| Outcome | Comparison holds fixed | Eligible events | Tested contrasts |',
        '|---|---|---:|---:|']
controls={'material':'site, object kind, length band','city':'object kind, material, length band','excavation_area':'site, object kind, material, length band','room_or_building':'site, excavation area, object kind, material, length band','recorded_layer':'site, excavation area, object kind, material, length band','depth':'site, excavation area, object kind, material, length band'}
for a in summary['axes']:lines.append('| '+' | '.join([a['family'],controls[a['family']],str(a['events']),str(a['tests'])])+' |')
lines+=['','Length bands are 1, 2–3, 4–6 and 7+ recorded sign tokens. Word groups must occur on at least ten representative objects overall and on at least five objects in the axis being tested. Material/site/area/layer targets need at least twenty objects; exact room/building labels need eight. Missing material, site and layer values are not filled. Layer labels are site-specific recorded phase/period strings, not pooled “early/middle/late” bins. Catalogue-mapped chronology is displayed to the reader but is not substituted for the raw layer labels in the test.','',
        'The formula-weighted check gives each exact whole-object inscription formula a total weight of one across the corpus, regardless of how many objects repeat it. It keeps every findspot rather than choosing an arbitrary representative room for a repeated formula. This is a repetition sensitivity, not complete elimination of every workshop or excavation dependence.','',
        'Finite-permutation resolution is 1/50,000 before correction. Primary p-values are two-sided. Maximum statistics preserve dependencies among the word groups and target labels by using shared conditional permutations. The second weighting is a stricter sensitivity, not an alternative route for promoting whichever result looks better.','',
        '## What was already in the repo','',
        'This does not claim to discover the tax/copper-tablet association for the first time. Earlier work already tested city/object functions and broad chronological bins (`jobs/out/key6b_readings_key5_atlas.md`); the independent continuation already ran site-controlled sign/artifact contrasts (`reports/statistical_report.md`). The additional work here is the full 81-group, six-axis comparison of recorded material and local context, the whole-screen correction, whole-formula weighting, complete contrast export and links to actual findspots.','',
        '## Files','',
        '- `associations.html`: searchable counts, adjusted results and links to matching catalogue records.','- `all_descriptive_and_adjusted_associations.csv`: every descriptive contrast, including comparisons that cannot be separated from the control variables.','- `all_associations.csv`: all 7,773 estimable adjusted tests.','- `all_finding_occurrences.csv`: every analysed object/face behind the two primary findings.','- `events.csv`, `word_groups.csv`, `summary_by_axis.csv`, `summary.json`: units, labels, sample sizes and results.','- `*_nulls.npz`: all primary and formula-weighted maximum-statistic null arrays.','',
        'Labels remain frozen hypotheses from the existing key. A bijective renaming of a sign would retain the same archaeological association, so these patterns alone cannot identify its spoken word or exact meaning.','',
        'Reproduce with the pinned Lipi metadata and the continuation virtual environment:','',
        '```sh','python research/independent_validation_20261120/context_associations/run.py --lipi-metadata /path/to/metadata_filtered.csv --permutations 49999','python research/independent_validation_20261120/context_associations/present.py','python research/independent_validation_20261120/context_associations/check.py','```','',
        'The calculation took about '+str(round(summary['seconds']))+' seconds with one BLAS thread. No Colab units were used.']
(BASE/'README.md').write_text('\n'.join(lines)+'\n')
with (BASE/'README.md').open('a') as f:
    f.write('\n## Narrow copper-tablet comparison\n\n[All 29 sign-845 copper specimens and the within-copper controls](results/COPPER_845.md) are released separately, with a [readable HTML table](results/copper845.html). All 29 contain 407. There is no exact 845-removed inscription family with both positive and negative specimens, so the fully matched semantic effect cannot be estimated. No independent archaeological function is assigned from a room code or a proposed translation. Reproduce with `python research/independent_validation_20261120/context_associations/copper845.py`, then `check_copper845.py`.\n')
payload_fields=['family','proposed_meaning','proposed_root','signs','target','word_events','other_events','observed_word_target_events','other_target_events','expected_word_target_events','target_share_word_events','target_share_other_events','adjustable','p_FWER_six_axes','formula_weighted_p_FWER_six_axes','mean_local_depth_rank_word','mean_local_depth_rank_other','result','occurrences_url']
payload=json.dumps([{k:r[k] for k in payload_fields} for r in allrows],ensure_ascii=False).replace('</','<\\/')
page='''<!doctype html><meta charset="utf-8"><title>Words and archaeological context</title><style>body{font:16px Arial,sans-serif;background:#f6f8fa;color:#1b2e40;margin:28px}p{line-height:1.5;max-width:1200px}input,select,button{font:inherit;padding:10px;margin:0 10px 10px 0}input{width:380px}table{border-collapse:collapse;background:white;width:100%;font-size:14px}th,td{padding:12px;text-align:left;vertical-align:top;border-bottom:1px solid #dde3e9}th{background:#243d53;color:white;position:sticky;top:0}td:first-child{min-width:165px}td:nth-child(2){min-width:250px}td:nth-child(5){min-width:280px}.scroll{overflow:auto;max-height:66vh}details{min-width:250px;line-height:1.6}summary{cursor:pointer}a{color:#175e91}</style>
<h1>Proposed words and archaeological context</h1>
<p>81 proposed word/sign groups, 4,476 representative objects and 7,773 adjusted comparisons. <b>The tax/levy group occurs on copper objects in 29/38 known-material cases, compared with 148/3,662 other objects.</b> The proposed measure group is concentrated at Harappa. These raw patterns overlap object types and materials.</p>
<p>Two patterns pass the first statistical check: bangle/copper and numeral seven/shallower depth. They do not pass the second check, which reduces the influence of repeated inscriptions. No city, area, room/building or recorded-layer pattern passes the first corrected check. The counts remain useful observations; they do not establish word meanings.</p>
<p><a href="../../translation_catalogue/results/catalogue.html">Open the full inscription and findspot catalogue</a>. Each “View matching findspots” link below opens actual recorded locations. Catalogue links include separate faces and paired catalogue records; the statistics count representative Lipi objects.</p>
<input id="q" placeholder="Search a word, material, city or stratum"><select id="axis"><option value="">All context types</option></select><select id="scope"><option value="all">Every descriptive comparison</option><option value="tested">Adjusted tests only</option><option value="primary">Below 0.05 in primary corrected test</option><option value="both">Below 0.05 in both checks</option></select><button id="prev">Previous</button><button id="next">Next</button><p id="count"></p><div class="scroll"><table><thead><tr><th>Proposed word</th><th>Material / recorded context</th><th>Among word-bearing objects</th><th>Among other eligible objects</th><th>Controlled comparison</th><th>Actual findspots</th></tr></thead><tbody id="body"></tbody></table></div>
<script>const records=PAYLOAD;let page=0;const size=75,el=id=>document.getElementById(id);for(const f of [...new Set(records.map(r=>r.family))]){const o=document.createElement('option');o.value=f;o.textContent=f.replaceAll('_',' ');el('axis').appendChild(o)}
const percent=x=>(100*Number(x)).toFixed(1)+'%';function draw(){const q=el('q').value.toLowerCase(),axis=el('axis').value,scope=el('scope').value;const rs=records.filter(r=>(!axis||r.family===axis)&&(!q||[r.proposed_meaning,r.proposed_root,r.target].join(' ').toLowerCase().includes(q))&&(scope==='all'||scope==='tested'&&r.adjustable==='True'||scope==='primary'&&r.p_FWER_six_axes!==''&&Number(r.p_FWER_six_axes)<.05||scope==='both'&&r.p_FWER_six_axes!==''&&Number(r.p_FWER_six_axes)<.05&&Number(r.formula_weighted_p_FWER_six_axes)<.05));page=Math.min(page,Math.max(0,Math.ceil(rs.length/size)-1));el('body').replaceChildren();for(const r of rs.slice(page*size,(page+1)*size)){const tr=document.createElement('tr');const cell=text=>{const td=document.createElement('td');td.textContent=text;tr.appendChild(td);return td};cell(r.proposed_meaning+' ('+r.proposed_root+')');cell(r.family.replaceAll('_',' ')+': '+r.target);if(r.family==='depth'){cell(r.mean_local_depth_rank_word?percent(r.mean_local_depth_rank_word)+' mean local depth rank ('+r.word_events+' objects)':'Not estimable');cell(r.mean_local_depth_rank_other?percent(r.mean_local_depth_rank_other)+' mean local depth rank':'Not estimable')}else{cell(r.observed_word_target_events+'/'+r.word_events+' ('+percent(r.target_share_word_events)+')');cell(r.other_target_events+'/'+r.other_events+' ('+percent(r.target_share_other_events)+')')}const td=cell(''),details=document.createElement('details'),sum=document.createElement('summary');sum.textContent=r.result;details.appendChild(sum);const p=document.createElement('p');p.textContent=r.p_FWER_six_axes!==''?'Whole-screen p: '+Number(r.p_FWER_six_axes).toPrecision(3)+'. Formula-weighted p: '+Number(r.formula_weighted_p_FWER_six_axes).toPrecision(3)+(r.expected_word_target_events!==''?'. Expected word/context count among matched objects: '+Number(r.expected_word_target_events).toFixed(2):''):'The available data do not provide an adjusted comparison independent of the matching variables, or there are too few word occurrences.';details.appendChild(p);td.appendChild(details);const linkcell=cell(''),a=document.createElement('a');a.href=r.occurrences_url;a.textContent='View matching findspots';linkcell.appendChild(a);el('body').appendChild(tr)}el('count').textContent=rs.length.toLocaleString()+' comparisons; page '+(page+1)+' of '+Math.max(1,Math.ceil(rs.length/size));el('prev').disabled=page===0;el('next').disabled=(page+1)*size>=rs.length}for(const id of ['q','axis','scope'])el(id).oninput=()=>{page=0;draw()};el('prev').onclick=()=>{page--;draw()};el('next').onclick=()=>{page++;draw()};draw();</script>'''
(OUT/'associations.html').write_text(page.replace('PAYLOAD',payload).replace('<h1>','<p><a href="copper845.html">Sign 845: all 29 copper specimens and the narrower comparison</a></p><h1>',1))
print('Prepared',len(allrows),'descriptive rows and',len(stats),'adjusted tests, with actual-findspot links.')
