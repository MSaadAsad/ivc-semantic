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
    classification=json.loads((BASE/'classification.json').read_text())
    groups=classification['groups'];displayed=[l for g in groups for l in g['languages']]
    assert len(displayed)==len(set(displayed))==22 and set(displayed)==set(LANGS)
    group_of={l:g['id'] for g in groups for l in g['languages']}
    assert group_of['Tamil']==group_of['Malayalam']==group_of['Kannada']=='south_i'
    assert group_of['Telugu']==group_of['Gondi']==group_of['Kui']==group_of['Kuwi']=='south_ii'
    assert group_of['Kolami']==group_of['Parji']==group_of['Naiki']==group_of['Naikri']=='central'
    assert group_of['Kurukh']==group_of['Malto']=='kurukh_malto' and group_of['Brahui']=='brahui'
    counts={}
    for field,n in [('target_meaning',67),('both_meanings',48),('strict_complete',48)]:
        bins=list(csv.DictReader((BASE/'results/branch_overlap_regions.csv').open()))
        assert sum(r['measure']==field for r in bins)==32
        assert sum(int(r['count']) for r in bins if r['measure']==field)==n
        counts[field]=n
    grouped=list(csv.DictReader((BASE/'results/branch_by_claim.csv').open()))
    assert len(grouped)==67*5
    for r in grouped:
        ls=next(g['languages'] for g in groups if g['id']==r['group'])
        for field in ['target_meaning','both_meanings','strict_complete','one_edit_complete']:
            yes=[l for l in ls if ix[r['claim'],l][field]=='True']
            assert (r[field]=='True')==bool(yes)
            assert r[field+'_languages']=='; '.join(yes)
    semantics=list(csv.DictReader((BASE/'results/semantics_catalogue.csv').open()))
    assert len(semantics)==67
    for r in semantics:
        c=next(c for c in claims if c['sign']==r['sign'])
        assert r['proposed_picture_or_first_meaning']==' / '.join(c['a'])
        if c['kind'] in ('bridge','polysemy'):assert r['proposed_intended_meaning']==' / '.join(c['b'])
    meta=json.loads((BASE/'results/graphic_revision.json').read_text())
    assert meta['matrix_sha256']==hashlib.sha256((BASE/'results/language_by_claim.csv').read_bytes()).hexdigest()
    # The correction changes presentation/aggregation, not any source lexical judgments.
    assert meta['matrix_sha256']=='a1303637d398551ce2682e721394aa6829207c9a0d2989852076d2ad899f6f4b'
    svg=(BASE/'figures/indus_language_overlap.svg').read_text()
    assert all(c['title'] in svg for c in claims if c['kind'] in ('bridge','polysemy'))
    assert all(l in (BASE/'figures/indus_all_signs.svg').read_text() for l in LANGS)
    assert all((BASE/'figures'/name).stat().st_size>10000 for name in ['indus_language_overlap.png','indus_language_overlap.svg','indus_all_signs.png','indus_all_signs.svg'])
    print('PASS: source freeze; unchanged 1,474 lexical cells; historical subgroup assignments; within-language aggregation; all English semantics; all 22 displayed varieties; 163-row scope; controls; corrected set partitions and graphics.')

if __name__=='__main__':main()
