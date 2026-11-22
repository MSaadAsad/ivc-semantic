"""Check source retention and ensure contextual candidates are not scored as matches."""
import collections
import hashlib
import json
from run import BASE, IN, OUT, NW, TARGETS, rows

summary=json.loads((OUT/'summary.json').read_text())
inventory=rows(OUT/'residue_sample_inventory.csv')
assert len(inventory)==209
assert len({(r['study'],r['sample_id']) for r in inventory})==209
assert all(r['inscription_record_link']=='Not established' and not r['sign_sequence'] for r in inventory)
counts=collections.Counter(r['study'] for r in inventory)
assert counts=={'Chakraborty2020':59,'Suryanarayan2021':122,'GarciaGranero2022':28}

# Verify all numerical and source interpretation fields survive export.
index={(r['study'],r['sample_id']):r for r in inventory}
for name,study,fields in [
    ('kotada2020_tableS1.csv','Chakraborty2020',{'lipid_yield':'total_yield_text','delta13C_C16':'delta13C_C16','delta13C_C18':'delta13C_C18','delta13C_difference':'delta13C_difference','published_interpretation':'published_isotope_interpretation'}),
    ('northwest2021_original_data.csv','Suryanarayan2021',{'lipid_yield':'Lipidconc_ug_g','delta13C_C16':'delta13C_C16','delta13C_C18':'delta13C_C18','delta13C_difference':'bigdelta'}),
    ('gujarat2022_table2.csv','GarciaGranero2022',{'lipid_yield':'lipid_ug_g','delta13C_C16':'delta13C_C16','delta13C_C18':'delta13C_C18','delta13C_difference':'delta13C_difference'})]:
    for original in rows(IN/name):
        if study=='Suryanarayan2021' and original['Site_name'] not in NW:continue
        output=index[study,original.get('sample_id',original.get('Sample'))]
        assert all(output[dest]==original[source] for dest,source in fields.items())
        if study=='GarciaGranero2022':
            starch={part.split('=',1)[0]:part.split('=',1)[1] for part in output['starch_observations'].split('; ')}
            assert len(starch)==7 and all(original[k]==v for k,v in starch.items())

controls=rows(OUT/'excluded_modern_controls.csv')
assert len(controls)==2 and all(r['Site_name'] not in NW for r in controls)
low=rows(IN/'northwest2021_SI3_low_yield_IDs.csv')
assert len(low)==len({r['source_sample_id'] for r in low})==49
legacy=rows(IN/'thesis2019_groupI.csv')
assert collections.Counter(r['site_label'] for r in legacy)=={'Mohenjo-daro':5,'Kalibangan':5}
assert all(not r['published_lipid_ug_g'] for r in legacy if r['site_label']=='Kalibangan')
assert len(rows(OUT/'additional_legacy_collection_candidates.csv'))==159

shortlist=rows(OUT/'food_sign_pottery_shortlist.csv')
assert {r['reference'] for r in shortlist}=={'H-1417','H-2568','H-1731','M-2003','M-1576','M-1599'}
assert all(r['frozen_food_meanings'] for r in shortlist)
targets=rows(OUT/'frozen_food_targets.csv')
assert {r['sign'] for r in targets}==set(sum(TARGETS.values(),[])) and len(targets)==9
shared=rows(OUT/'same_site_inscribed_pots.csv')
assert len(shared)==13 and not any(r['frozen_food_signs'] for r in shared)
assert not rows(OUT/'identifier_hits.csv')
assert {r['sample_id'] for r in rows(OUT/'weak_context_candidates.csv')}=={'FRN15','FRN16','FRN17'}
assert summary['verified_same_object_pairs']==summary['additional_verified_object_pairs']==summary['hypothesis_tests_run']==0
assert summary['lipi_inscribed_pottery_objects']==629 and summary['lipi_pottery_face_records']==635
for name,digest in summary['input_sha256'].items():
    assert hashlib.sha256((IN/name).read_bytes()).hexdigest()==digest
print('Source values retained; 209 core rows and 10 separate uncertain-provenance samples; no contextual candidate falsely scored. Semantic tests run: 0.')
