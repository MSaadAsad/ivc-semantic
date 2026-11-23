"""Recovery, source-meaning pitfalls, channel separation and inventory checks."""
import collections
import hashlib
import json

import open_rebus as O
import open_rebus_report as P


def entry(word,meaning):
    stem,basis=O.nominal_stem(word,meaning)
    return dict(word=word,strict=O.R.norm(word),permissive=O.permissive(word),stem=stem,
                stem_basis=basis,heads=O.R.senses(meaning),language='en')


def main():
    a=entry('ka-at','roof');b=entry('ka-at','a previously unlisted meaning')
    c=entry('ka-ap','another meaning');d=entry('ša-at','a different onset')
    ee=[a,b,c,d];found=list(O.search_targets(a,ee,O.build_neighbors(ee)))
    assert ('equal_conservative_form',b) in found
    assert ('one_edit_whole_form',c) not in found  # Too short after normalization.
    assert not O.picture_match(b,'roof',O.source_constants())
    # Separate senses from the same source can be recovered by the same search.
    a['source']=b['source']='synthetic';a['id']=b['id']='same-entry'
    assert ('equal_conservative_form',b) in list(O.search_targets(a,ee,O.build_neighbors(ee)))
    jug=entry('pi-ti','jug');enemy=entry('pi-ti-ir','enemy-SG');unanalysed=entry('pi-ti-ir','enemy')
    ee=[jug,enemy,unanalysed];found=list(O.search_targets(jug,ee,O.build_neighbors(ee)))
    assert ('equal_nominal_class_stem',enemy) in found
    assert ('equal_conservative_form',enemy) not in found
    assert ('equal_nominal_class_stem',unanalysed) not in found
    assert O.nominal_stem('ba-at-ip','foot-PL')[0]=='bati'
    assert O.nominal_stem('ba-at-ir','foot')[0]=='batir'
    assert O.nominal_stem('ba-at-ir','foot-PL')[0]=='batir'
    sceptre=entry('ha-at-ti','sceptre');affection=entry('ha-ti','affection')
    ee=[sceptre,affection];found=list(O.search_targets(sceptre,ee,O.build_neighbors(ee)))
    assert ('equal_permissive_key',affection) in found
    assert ('equal_conservative_form',affection) not in found
    a=entry('ha-al-ti','door');b=entry('ha-al-mi','document');c=entry('ša-al-ti','other')
    ee=[a,b,c];found=list(O.search_targets(a,ee,O.build_neighbors(ee)))
    assert ('one_edit_whole_form',b) in found
    assert ('one_edit_whole_form',c) not in found
    assert O.picture_match(entry('x','gate'),'door',O.source_constants())
    assert 'possible_untranslated_self_gloss' in O.target_flags('zippi','zip','en',('zippi',),{'zippi'}) or 'English_head_requires_translation_review' in O.target_flags('zippi','zip','en',('zippi',),set())
    assert 'name_or_label_risk' in O.target_flags('PN','x','en',('pn',),{'pn'})
    assert 'schutz' in O.german_senses('ne Dach (wörtliche Bedeutung), Schutz (übertragene Bedeutung); G')
    assert 'krug' not in O.german_senses('Mann mit Krug')
    rows=O.R.read(O.OUT/'open_rebus_all_candidates.csv')
    reviewed=O.R.read(O.OUT/'open_rebus_review.csv')
    summary=json.loads((O.OUT/'open_rebus_summary.json').read_text())
    assert len(rows)==len(reviewed)==summary['candidates']==680
    assert len({r['candidate_id'] for r in rows})==len(rows)
    assert dict(collections.Counter(r['channel'] for r in rows))==summary['candidate_channels']
    inventory=O.R.read(O.OUT/'open_rebus_all_417_pictures.csv')
    assert len(inventory)==len({r['mahadevan_glyph'] for r in inventory})==417
    coverage=O.R.read(O.OUT/'open_rebus_picture_coverage.csv')
    assert len(coverage)==73 and sum(int(r['lexical_picture_rows'])>0 for r in coverage)==24
    assert sum(int(r['nominal_stem_pairs']) for r in coverage)==6
    for r in O.R.read(O.OUT/'open_rebus_input_hashes.csv'):
        assert hashlib.sha256((O.REPO/r['path']).read_bytes()).hexdigest()==r['sha256']
    for r in rows:
        assert r['picture_source_id'] and r['target_source_id'] and r['picture_raw_gloss'] and r['target_raw_gloss']
        if r['channel']=='equal_conservative_form':assert O.R.norm(r['picture_word'])==O.R.norm(r['target_word'])
        if r['channel']=='equal_nominal_class_stem':
            assert r['picture_stem_key']==r['target_stem_key']
            assert r['picture_stem_basis'] or r['target_stem_basis']
    assert len({r['lead_id'] for r in reviewed if r['lead_id']})==len(P.LEADS)==8
    assert all(not r['lead_id'] for r in reviewed if r['channel']=='one_edit_whole_form')
    assert any(r['review_disposition']=='quarantined_possible_translation_error' for r in reviewed)
    assert any(r['review_disposition']=='rejected_orthographic_shortening' for r in reviewed)
    assert all(r['review_disposition']=='already_known_semantic_direction' for r in reviewed if r['picture_noun']=='house' and r['target_heads']=='not')
    jar=[r for r in reviewed if r['lead_id']=='jar_enemy']
    assert len(jar)==2 and all(r['channel']=='equal_nominal_class_stem' for r in jar)
    assert any(r['lead_id']=='roof_protection' and r['target_source_id']=='N:1345' for r in reviewed)
    occurrences=O.R.read(O.OUT/'open_rebus_example_sign_occurrences.csv')
    assert len(occurrences)==3560
    assert len({(r['lead_id'],r['catalogue'],r['face_id']) for r in occurrences})==len(occurrences)
    assert all(r['example_sign'] in r['sign_sequence'] for r in occurrences)
    print('PASS: synthetic unrestricted-target and same-entry recovery; whole/stem/permissive/near separation; morphology guards; semantic/source pitfalls; all417 drawings;24/73 noun coverage;680 provenance witnesses; eight qualified directions;3,560 reference occurrences. Colab0.')


if __name__=='__main__':main()
