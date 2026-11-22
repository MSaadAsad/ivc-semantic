"""Check whether public residue samples can be paired with inscribed vessels.

The result is identification feasibility, not a semantic null test. Same-site
and same-grid candidates are never promoted to same-object matches.
"""
import collections,csv,hashlib,html,json,re
from pathlib import Path
BASE=Path(__file__).resolve().parent;OUT=BASE/'results';IN=BASE/'inputs'
NW={'ALM':'Alamgirpur','FRN':'Farmana','KNK':'Khanak','LHRI':'Lohari Ragho I','MSDI':'Masudpur I','MSDVII':'Masudpur VII','RGR':'Rakhigarhi'}
TARGETS={'rice':['215','216'],'millet/grain':['803','804','806','807'],'paddy/ear of paddy':['831','833'],'sesame':['854']}
def rows(p):return list(csv.DictReader(Path(p).open(encoding='utf-8-sig',newline='')))
def write(name,rs,fields=None):
    with (OUT/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rs[0]),lineterminator='\n');w.writeheader();w.writerows(rs)
def norm(s):return re.sub('[^A-Z0-9]','',s.upper())
def tokens(r):return set(re.findall(r'(?<!\d)\d{3}(?!\d)',r['sign_sequence']))
def main():
    OUT.mkdir(exist_ok=True)
    catalogue=rows(BASE.parent/'translation_catalogue/results/all_inscriptions.csv')
    potfaces=[r for r in catalogue if r['catalogue']=='Lipi' and r['object_type'].startswith('POT:')]
    objects=collections.defaultdict(list)
    for r in potfaces:objects[r['object_identifier']].append(r)
    pots=[]
    for group in objects.values():
        r=dict(group[0]);r['face_id']='; '.join(x['face_id'] for x in group)
        r['sign_sequence']=' | '.join(x['sign_sequence'] for x in group)
        if len(group)>1:r['existing_proposed_translation']=' | '.join(x['face_id']+': '+x['existing_proposed_translation'] for x in group)
        pots.append(r)
    assert len(pots)==629 and len(potfaces)==635
    proposals=json.loads((BASE.parent/'frozen/proposals.json').read_text());key={r['sign']:r for r in proposals}
    frozen=[]
    for family,signs in TARGETS.items():
        for sign in signs:
            p=key[sign];frozen.append(dict(family=family,sign=sign,proposed_root=p['root_or_gloss'],frozen_short_gloss=p['short_gloss']))
    write('frozen_food_targets.csv',frozen)
    core=set(sum(TARGETS.values(),[]));samples=[]
    def sample(study,site,sid,context='',part='',lipid='',d16='',d18='',delta='',interpretation='',starch=''):
        return dict(study=study,site=site,sample_id=sid,context_as_published=context,vessel_part=part,lipid_yield=lipid,
          delta13C_C16=d16,delta13C_C18=d18,delta13C_difference=delta,published_interpretation=interpretation,
          starch_observations=starch,inscription_record_link='Not established',sign_sequence='',identity_basis='')
    for r in rows(IN/'kotada2020_tableS1.csv'):
        samples.append(sample('Chakraborty2020','Kotada Bhadli',r['sample_id'],part=r['vessel_part'],lipid=r['total_yield_text'],d16=r['delta13C_C16'],d18=r['delta13C_C18'],delta=r['delta13C_difference'],interpretation=r['published_isotope_interpretation']))
    nw=rows(IN/'northwest2021_original_data.csv');modern=[]
    for r in nw:
        if r['Site_name'] not in NW:modern.append(r);continue
        samples.append(sample('Suryanarayan2021',NW[r['Site_name']],r['Sample'],r['Trench_Context']+'; '+r['Context_Notes'],r['Rim_base_body'],r['Lipidconc_ug_g'],r['delta13C_C16'],r['delta13C_C18'],r['bigdelta']))
    for r in rows(IN/'gujarat2022_table2.csv'):
        starch='; '.join(k+'='+r[k] for k in ['small_millet_starch_count','jobs_tears_starch_count','wheat_barley_starch_count','pulse_starch_count','ginger_starch_count','other_USO_count','unidentified_starch_count'])
        samples.append(sample('GarciaGranero2022',r['site'],r['sample_id'],part='Body sherd' if r['site']=='Loteshwar' else 'Base',lipid=r['lipid_ug_g'],d16=r['delta13C_C16'],d18=r['delta13C_C18'],delta=r['delta13C_difference'],starch=starch))
    assert len(samples)==209 and len(modern)==2
    assert len({(r['study'],r['sample_id']) for r in samples})==209
    # Equality is only a potential identifier hit, not proof that laboratory and
    # catalogue IDs name the same physical object. No such hit occurs here.
    hits=[]
    for s in samples:
        sid=norm(s['sample_id'])
        for p in pots:
            if s['site']!=p['city']:continue
            for field in ['reference','excavation_number']:
                if len(sid)>=5 and sid==norm(p[field]):
                    hits.append(dict(study=s['study'],sample_id=s['sample_id'],reference=p['reference'],face_id=p['face_id'],field=field,status='Potential exact identifier hit: requires source confirmation'))
    write('identifier_hits.csv',hits,['study','sample_id','reference','face_id','field','status'])
    write('residue_sample_inventory.csv',samples);write('excluded_modern_controls.csv',modern)
    bysite=collections.Counter(s['site'] for s in samples);shared=[p for p in pots if p['city'] in bysite]
    selected_fields=['face_id','reference','city','sign_sequence','existing_proposed_translation','current_163_key_literal_meanings','excavation_number','block_or_house','room_or_grid','found_at']
    def export(p):
        meanings='; '.join(family+' ('+'/'.join(sorted(set(signs)&tokens(p)))+')' for family,signs in TARGETS.items() if set(signs)&tokens(p))
        return dict(**{k:p[k] for k in selected_fields},frozen_food_signs='; '.join(sorted(core&tokens(p))),frozen_food_meanings=meanings)
    write('same_site_inscribed_pots.csv',[export(p) for p in shared])
    foodpots=[p for p in pots if core&tokens(p)];write('food_sign_pottery_shortlist.csv',[export(p) for p in foodpots])
    site_table=[]
    for site,n in sorted(bysite.items()):
        pp=[p for p in pots if p['city']==site]
        site_table.append(dict(site=site,available_residue_rows=n,catalogue_inscribed_pots=len(pp),inscribed_pots_with_frozen_food_signs=sum(bool(core&tokens(p)) for p in pp),verified_object_pairs=0))
    write('site_coverage.csv',site_table)
    legacy=rows(IN/'thesis2019_groupI.csv');legacy_sites={r['site_label'] for r in legacy}
    legacy_pots=[p for p in pots if p['city'] in legacy_sites]
    write('additional_legacy_collection_candidates.csv',[export(p) for p in legacy_pots])
    legacy_hits=[(s['sample_id'],p['reference']) for s in legacy for p in legacy_pots if s['site_label']==p['city'] and any(norm(s['sample_id'])==norm(p[k]) for k in ['reference','excavation_number'])]
    assert len(legacy)==10 and not legacy_hits
    # One deliberately weak contextual lead: Farmana ID5 versus 1D5, an I/1
    # reading ambiguity. Three same-grid samples remain unverified objects.
    candidates=[]
    for p in shared:
        if p['city']=='Farmana' and p['block_or_house'].strip('-')=='ID5':
            for s in samples:
                if s['site']=='Farmana' and s['context_as_published'].startswith('1D5-'):
                    candidates.append(dict(reference=p['reference'],face_id=p['face_id'],catalogue_grid=p['block_or_house'],catalogue_excavation=p['excavation_number'],sample_id=s['sample_id'],sample_context=s['context_as_published'],status='Unverified I/1 grid similarity; not a vessel match',frozen_food_signs='; '.join(sorted(core&tokens(p)))))
    write('weak_context_candidates.csv',candidates)
    assert not hits and len(shared)==13 and len(foodpots)==6 and len(candidates)==3
    assert not any(core&tokens(p) for p in shared)
    summary=dict(catalogue_observations=len(catalogue),lipi_inscribed_pottery_objects=len(pots),lipi_pottery_face_records=len(potfaces),
       core_studies=3,reported_pottery_samples_across_three_studies=259,
       available_archaeological_sample_rows=209,excluded_modern_reference_rows=2,
       main_northwest_study_reported_fragments=172,available_northwest_archaeological_rows=122,
       northwest_reported_minus_csv_count=50,northwest_SI3_low_yield_IDs_recovered=49,northwest_count_difference_unreconciled=1,same_site_inscribed_pots=13,
       same_site_pots_with_frozen_food_signs=0,identifier_equality_hits=len(hits),verified_same_object_pairs=0,
       weak_unverified_grid_candidates=len(candidates),whole_corpus_food_sign_pottery_shortlist=6,
       additional_thesis_collection_samples=10,additional_site_label_candidate_pottery_objects=len(legacy_pots),
       additional_site_label_candidate_pots_with_food_signs=sum(bool(core&tokens(p)) for p in legacy_pots),
       additional_verified_object_pairs=0,
       hypothesis_tests_run=0,decision='Direct contents validation cannot run on the verified public joins recovered here. No positive or negative decipherment result.',
       limitations=['No same-object crosswalk recovered; this does not prove every residue sample is uninscribed.',
         'The nine rice/millet/paddy/sesame readings come from the pre-existing frozen key; this feasibility grouping was curated after publication of the chemical results.',
         '413 is grain-tax/cut in the frozen key, not a direct cereal-content prediction; star/fish pictures do not imply fish contents.',
         'Broad fat categories do not identify sesame; negative plant detection is not evidence of historical absence.',
         'The 2022 supplementary vessel-description table was not recovered. The 42-page 2021 SI3 register was recovered; its listed excluded IDs leave a one-entry count discrepancy.',
         'The 2025 Karanpura/Ropar full sample tables and the full 1995 Nausharo paper were not recovered.'],
       input_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(IN.glob('*.csv'))})
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
    present(summary,site_table,shared,foodpots)
    print(json.dumps(summary,ensure_ascii=False))
def present(s,sites,shared,shortlist):
    esc=html.escape
    page='''<!doctype html><meta charset="utf-8"><title>Residues and inscriptions: feasibility</title><style>body{font:17px/1.5 system-ui;max-width:1300px;margin:32px auto;padding:0 22px;color:#203644}table{border-collapse:collapse;width:100%;font-size:14px}td,th{border:1px solid #cfdae0;padding:10px;text-align:left;vertical-align:top}th{background:#eaf1f5}a{color:#156292}.finding{padding:16px;background:#fff5da}</style>
<h1>Can vessel residues independently test the proposed words?</h1><p class="finding"><b>No verified same-object pairs were recovered.</b> This is a completed feasibility check, with no new support for or against the proposed readings. The chemical data exist; the required inscription-to-vessel identities have not been established.</p>
<p>Three studies report 259 pottery samples. The main tables supply 209 archaeological sample rows. The Cambridge CSV additionally contains two modern references, excluded here, and lists 122 of the northwest study's 172 analysed fragments. Its recovered 42-page image register lists 49 low-yield IDs; one entry in the reported total remains unreconciled. These figures must not be presented as 259 independent labelled inscription tests.</p>
<p>The fixed food targets are rice (215/216), millet/grain (803/804/806/807), paddy (831/833), and sesame (854). None of the 13 catalogued inscribed pots from the shared sites carries these signs. The six target-bearing pottery records in the whole Lipi corpus are at Harappa or Mohenjo-daro, outside these three datasets' sites.</p>
<p><b>Additional source checked:</b> the 2019 doctoral thesis includes five samples labelled Mohenjo-daro and five labelled Kalibangan. The author describes their teaching-collection provenance and excavation contexts as uncertain. These site labels yield another 159 catalogue-pottery candidates (three carrying food signs), but no verified object identity. They are kept separate from the three core studies; other overlapping thesis samples are not added again.</p>
<h2>Site overlap is not object identity</h2><table><thead><tr><th>Site</th><th>Available residue rows</th><th>Inscribed pots in catalogue</th><th>With fixed food signs</th><th>Verified same-object pairs</th></tr></thead><tbody>'''
    for r in sites:page+='<tr>'+''.join('<td>'+esc(str(v))+'</td>' for v in r.values())+'</tr>'
    page+='</tbody></table><p>A possible Farmana grid correspondence (catalogue ID5 versus residue-study 1D5) gives three candidates, FRN15/16/17. It does not identify a single pot. Their possible inscription counterpart carries the proposed house sign, not one of the fixed food labels.</p><h2>Concrete target vessels for future source/laboratory work</h2><table><thead><tr><th>Reference</th><th>Site</th><th>Proposed food meaning</th><th>Recorded signs</th><th>Recorded excavation number</th></tr></thead><tbody>'
    for r in shortlist:
        e=export_food_meaning(r)
        page+='<tr>'+''.join('<td>'+esc(v)+'</td>' for v in [r['reference'],r['city'],e,r['sign_sequence'],r['excavation_number']])+'</tr>'
    page+='''</tbody></table><h2>What is still needed</h2><p>Recover a museum/excavation accession crosswalk or diagnostic photographs for a residue-tested inscribed pot. Alternatively, obtain analyses for inscribed target vessels. Then specify whether the inscription predicts contents, ownership or a transaction, and whether the chemical method can identify the proposed commodity. General animal fat or an unidentified plant oil cannot confirm sesame.</p>
<p><a href="../README.md">Full findings and limits</a> · <a href="../SOURCES.md">Primary studies and source access</a> · <a href="residue_sample_inventory.csv">All 209 main-table archaeological sample rows</a> · <a href="same_site_inscribed_pots.csv">All 13 same-site inscription candidates</a> · <a href="weak_context_candidates.csv">Unverified grid candidates</a> · <a href="food_sign_pottery_shortlist.csv">Six target pottery records</a> · <a href="additional_legacy_collection_candidates.csv">159 additional site-label candidates</a> · <a href="summary.json">Machine-readable counts</a></p>'''
    (OUT/'feasibility.html').write_text(page)
def export_food_meaning(r):
    return '; '.join(family+' ('+'/'.join(sorted(set(signs)&tokens(r)))+')' for family,signs in TARGETS.items() if set(signs)&tokens(r))
if __name__=='__main__':main()
