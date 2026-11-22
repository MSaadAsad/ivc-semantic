"""Reproducible inventories for the user's material/findspot clue follow-up.

This inventories existing records and prior analyses. It does not assign new
sign meanings, add untranscribed objects, or turn selection clues into tests.
"""
import collections,csv,json,re,subprocess
from pathlib import Path
BASE=Path(__file__).resolve().parent;REPO=BASE.parents[2];OUT=BASE/'results/clue_followup'
def rows(p):return list(csv.DictReader(Path(p).open(encoding='utf-8-sig',newline='')))
def write(name,rs):
    with (OUT/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rs[0]),lineterminator='\n');w.writeheader();w.writerows(rs)
def main():
    OUT.mkdir(exist_ok=True)
    allrows=rows(BASE.parent/'translation_catalogue/results/all_inscriptions.csv');lipi=[r for r in allrows if r['catalogue']=='Lipi']
    gold=[r for r in allrows if r['material'].lower()=='gold'];assert len(gold)==2
    fields=['catalogue','face_id','reference','material','object_type','sign_sequence','existing_proposed_translation','existing_proposed_sounds','current_163_key_literal_meanings','found_at','recorded_stratigraphy','excavation_number']
    select=lambda rr:[{k:r[k] for k in fields} for r in rr]
    write('all_gold_records.csv',select(gold))
    write('all_645_records.csv',select([r for r in lipi if '645' in r['sign_sequence'].split('-')]))
    write('all_898_records.csv',select([r for r in lipi if '898' in r['sign_sequence'].split('-')]))
    write('workshop_locus_215_records.csv',select([r for r in lipi if r['city']=='Chanhu-daro' and re.search(r'loc\.?\s*215(?!\d)',r['room_or_grid'])]))
    physical=rows(REPO/'work_data/met/physical_tools_rods.csv')
    write('gold_physical_fields.csv',[r for r in physical if r['cisi'] in {'M-2128','M-2129'}])
    # Search the materialized original analysis scripts/reports, not this continuation's new claims.
    paths=subprocess.check_output(['git','ls-files','work_scripts','jobs/out','research/extensions_20261117'],cwd=REPO,text=True).splitlines()
    paths=[p for p in paths if Path(p).suffix in {'.py','.md','.txt'} and (REPO/p).is_file()]
    terms={
      'gold_object_used_in_reading':r'M-2129|gold object',
      'gold_hoard_area_test':r'gold hoards',
      'gold_caps_or_terminals':r'gold\s+caps?\b|gold\s+terminals?\b|bead[ -]caps?\b',
      'gold_pendants':r'gold\s+pendants?\b',
      'C87_specific':r'C-87',
      'C22_specific':r'C-22',
      'locus215_specific':r'(?:loc\.?|locus|room)\s*#?\s*215\b',
    }
    matches=[]
    for p in paths:
        for line_no,line in enumerate((REPO/p).read_text(errors='replace').splitlines(),1):
            for term,pattern in terms.items():
                if re.search(pattern,line,re.I):matches.append(dict(term=term,path=p,line=line_no,excerpt=line[:1000]))
    write('prior_source_matches.csv',matches)
    summary=dict(original_upstream_work_commit='727dfd411a4faa44d193d204757540d45c7b139b',
      original_upstream_work_checked_utc_date='2026-11-21',live_work_comparison='identical: ahead_by=0, behind_by=0',
      catalogue_records=len(allrows),gold_records=len(gold),gold_references=[r['reference'] for r in gold],
      sign645_lipi_faces=sum('645' in r['sign_sequence'].split('-') for r in lipi),
      sign645_lipi_objects=len({r['object_identifier'] for r in lipi if '645' in r['sign_sequence'].split('-')}),
      sign898_lipi_objects=len({r['object_identifier'] for r in lipi if '898' in r['sign_sequence'].split('-')}),
      original_source_files_searched=len(paths),source_match_counts=dict(collections.Counter(r['term'] for r in matches)),
      search_limits='Materialized original script/report text searched; GitHub default-branch index also consulted, which returns an older commit. Negative searches do not establish that Cuuper never considered a clue or that a cap is not catalogued under unknown material.',
      gold_caps_status='Two inscribed caps are described by Kenoyer and Miller 1999 p.134; no gold-labelled cap rows identified here. No museum crosswalk or sign transcriptions recovered. Not added to the corpus.',
      gold_mass_status='Existing physical export supplies dimensions, not measured masses, for these two records. No numerical mass test performed.',
      statistical_tests_run=0,new_accepted_translations=0)
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
    assert len(rows(OUT/'all_645_records.csv'))==26
    assert len(rows(OUT/'all_898_records.csv'))==4
    assert {r['reference'] for r in rows(OUT/'workshop_locus_215_records.csv')}=={'C-22','C-87'}
    print(json.dumps(summary,ensure_ascii=False))
if __name__=='__main__':main()
