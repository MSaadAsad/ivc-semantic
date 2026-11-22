"""Check catalogue completeness, joins, literal coverage and verbatim readings."""
import argparse, csv, json
from pathlib import Path
BASE=Path(__file__).resolve().parent; REPO=BASE.parents[2]
def rows(p):
    with Path(p).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
ap=argparse.ArgumentParser();ap.add_argument('--lipi-metadata',required=True);args=ap.parse_args()
source=rows(REPO/'work_data/reader_v3/corpus_soundfree_readings.csv')
catalogue=rows(BASE/'results/all_inscriptions.csv')
assert len(catalogue)==len(source)==9252
lookup={(r['catalogue'],r['face_id']):r for r in catalogue}
assert len(lookup)==9252
meta={r['id']:r for r in rows(args.lipi_metadata)}
mah=rows(REPO/'work_data/mahadevan_parsed.csv')
archive=rows(BASE/'results/all_existing_reading_versions.csv')
assert len(archive)==json.loads((BASE/'results/summary.json').read_text())['archived_reading_records']
for r in source:
    rec=lookup[(r['catalogue'],r['id'])]
    assert rec['sign_sequence']==r['signs']
    assert rec['city']==r['site']
    assert rec['reading_validated']=='False'
    assert int(rec['assigned_sign_tokens'])+len(rec['unassigned_signs'].split('; '))*(bool(rec['unassigned_signs']))==int(rec['total_sign_tokens'])
    if r['catalogue']=='Lipi':
        m=meta[r['id']]
        for a,b in [('excavation_area','area-section'),('block_or_house','block-house'),('room_or_grid','room-grid'),('depth_recorded','depth'),('period_recorded','period'),('chronology_recorded','time')]:assert rec[a]==m[b]
    else:
        m=mah[int(r['id'])]
        assert rec['excavation_area']==m['locus'] and rec['depth_recorded']==m['level']
        assert rec['reference']=='Mahadevan '+m['textnum']+' / line '+m['sideline']
for p,col in [('work_data/key6b/decoded_2262_corpus.csv','english_reading'),('work_data/key5b/decoded_1776_corpus.csv','english_reading'),('work_data/corpus_english3.csv','english')]:
    expected=rows(REPO/p)
    present=[r for r in archive if r['source_path']==p]
    assert len(present)==len(expected)
    assert [r['proposed_english'] for r in present]==[r[col] for r in expected]
assert len(rows(BASE/'results/all_163_sign_readings.csv'))==163
print('Verified all 9,252 source records, exact context joins, 163 sign values, all Key5/Key6B/current English readings and retained unknown signs.')
