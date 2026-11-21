"""Checks for substantive sense/linkage mistakes and output consistency."""
import csv,hashlib,json
from pathlib import Path
from analyze import BASE,LANGS,meaning,form,role

def main():
    cs=json.loads((BASE/'claims.json').read_text());claims=cs['claims'];by={c['id']:c for c in claims}
    repo=BASE.parents[2]
    for path,h in cs['input_sha256'].items():assert hashlib.sha256((repo/path).read_bytes()).hexdigest()==h,path
    assert len(claims)==67 and len(by)==67
    assert sum(c['kind'] in ('bridge','polysemy') for c in claims)==48
    assert 'S008' not in by and cs['excluded'][0]['sign']=='008'
    assert form('kōṭṭai')==form('kōṭṭai')
    assert form('kaṇ')!=form('kaṉ') and form('mīn')!=form('min')
    assert not meaning('see kaṇ', ['see'])
    assert not role(dict(gloss='young shoot',language='Malayalam',entry='2149'),by['S760'],'b')
    assert not role(dict(gloss='to wear, put on (as a garland)',language='Tamil',entry='4827'),by['S503'],'b')
    matrix=list(csv.DictReader((BASE/'results/language_by_claim.csv').open()))
    ix={(r['claim'],r['language']):r for r in matrix}
    assert len(matrix)==67*22==len(ix)
    for r in matrix:
        if r['strict_complete']=='True':assert r['both_meanings']=='True' and r['one_edit_complete']=='True'
        if by[r['claim']]['kind'] in ('literal','numeral'):assert r['both_meanings']=='False'
    for c in ['S001','S002']:assert all(ix[c,l]['target_meaning']=='True' for l in LANGS)
    assert {l for l in LANGS if ix['S923',l]['target_meaning']=='True'}=={'Tamil','Kurukh','Malto','Brahui'}
    for l in ['Brahui','Kurukh','Malto']:assert not any(r['strict_complete']=='True' for r in matrix if r['language']==l)
    assert ix['S220','Malto']['both_meanings']=='True'
    assert ix['S760','Malto']['both_meanings']=='True'
    assert ix['S171','Brahui']['family_a']=='True' and ix['S171','Brahui']['meaning_b']=='False'
    assert ix['S892','Brahui']['meaning_a']=='True' and ix['S892','Brahui']['meaning_b']=='False'
    assert ix['S400','Tamil']['target_meaning']=='False'
    assert ix['S503','Kannada']['target_meaning']=='False' # explicitly a tatsama
    assert ix['S060','Brahui']['target_without_questioned']=='False'
    scope=list(csv.DictReader((BASE/'results/key_scope.csv').open()))
    assert len(scope)==163 and sum(bool(r['claim']) for r in scope)==67
    controls=json.loads((BASE/'results/northern_controls.json').read_text())
    assert controls['unique_fixed_etyma']==107 and controls['draws']==4999
    assert all(e['holm_p']==1 for e in controls['endpoints'])
    counts={}
    for field,n in [('target_meaning',67),('both_meanings',48)]:
        bins=list(csv.DictReader((BASE/'results/venn_regions.csv').open()))
        assert sum(int(r['count']) for r in bins if r['measure']==field)==n
        counts[field]=n
    assert all((BASE/'figures'/name).stat().st_size>10000 for name in ['indus_language_overlap.png','indus_language_overlap.svg','indus_all_signs.png','indus_all_signs.svg'])
    print('PASS: source freeze; Unicode and sense exclusions; 1,474 cells; northern witnesses; all 163 scope rows; controls; Venn partitions; graphics.')

if __name__=='__main__':main()
