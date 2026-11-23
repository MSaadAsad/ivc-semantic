"""Source review and illustrated report; does not fit or validate translations."""
import base64
import collections
import csv
import html
import json
from pathlib import Path
import re

import open_rebus as O

BASE=O.BASE;OUT=O.OUT;REPO=O.REPO
H=html.escape
SOURCE='https://github.com/DigitalPasts/ALP-MEGA2024/blob/3160b20f5cd84b387343d071749bb90419148743/Elamite_materials/EWB-EJSmithFiles/N-EWB-EJSmith.csv'
GRAMMAR='https://unora.unior.it/bitstream/11574/217200/1/basello2023introduction-elamite.pdf'
TREATY='https://www.academia.edu/161289676/The_Old_Elamite_Treaty_A_complex_diplomatic_arrangement'

LEADS=[
 dict(id='roof_protection',title='Roof → protection',bridge='ku-uk → ku-uk',
      kind='Recorded literal / figurative senses',status='Priority lexical lead',glyph='135',lipi='482',
      evidence='The old dictionary explicitly distinguishes literal roof and figurative protection. The structured release also gives ku-uk “protection” (N:1345). This is recorded polysemy, not evidence of unrelated homonyms.',
      dates='Literal roof: Neo-Elamite in the legacy gloss; protection: Middle / Neo-Elamite. No mature-Indus-period roof attestation established here.',
      limits='The chevron could depict a roof, hill or abstract shape. No inscription has been translated “protection,” and no archaeological prediction has been tested.',
      novelty='Absent from the inspected older Elamite candidate table; that table instead linked roof ku-uk to uk-ku-e “his head.” The dictionary senses themselves are pre-existing.'),
 dict(id='jar_enemy',title='Jar / jug → enemy',bridge='pi-ti → pi-ti-r',
      kind='Same stem after a documented noun-class ending',status='Priority conditional lead',glyph='342',lipi='740',
      evidence='N:888 gives pi-ti “jug”; N:890 gives pi-ti-ir “enemy-SG.” Removing the source-labelled final -r yields piti. Basello (2023, p.28) independently analyses enemy as piti-r.',
      dates='Jug: Neo-Elamite in this release. Exact pi-ti-ir: Middle Elamite; bi-ti-ir is separately labelled Old Elamite (N:889). The enemy word is documented in the Naram-Sin treaty, but this does not backdate the jug word.',
      limits='These are not identical whole words. The jug gloss is uncertain in the older dictionary. A rebus would also need to explain how the enemy noun’s ending was represented in the Indus script.',
      novelty='Absent from the inspected older Elamite candidate table; its jar candidate was pi-ti → e-ip-ti “lord.” This supplies a different meaning to investigate.'),
 dict(id='gate_court',title='Door / gate → royal court',bridge='hi-el / hu-el → royal court',
      kind='Recorded metonymy',status='Secondary lexical lead',glyph='237',lipi='',
      evidence='Legacy entries HK:1236 and HK:1270 explicitly give gate / portal and figurative royal court. English door entries preserve the same written forms.',
      dates='Figurative senses in legacy Neo- / Achaemenid-Elamite glosses; literal door entries also include Middle Elamite. No early figurative attestation verified.',
      limits='A rectangle is also described as box or brick. No unique gate sign or whole-inscription reading follows. This is a common semantic extension, not a diagnostic sound pun.',
      novelty='Not in the inspected older Elamite candidate output. The dictionary meaning is already recorded.'),
 dict(id='gate_support',title='Door / gate → royal support',bridge='zi-ip → zi-ip',
      kind='Tentative legacy multiple sense',status='Needs lexical verification',glyph='237',lipi='',
      evidence='HK:2389 lists portal / gate and “(royal) support.” The trailing German wording is tentative and truncated, so this stays below the priority leads.',
      dates='No reliable period attached to both senses in the cached entry.',
      limits='Requires the original dictionary page and attested contexts before calling it secure Elamite polysemy. No direct proof of an Indus value.',
      novelty='Absent from the inspected older Elamite candidate output; a source-recovery lead, not a confirmed new reading.'),
 dict(id='seed_descendants',title='Seed → descendants',bridge='pa-ar → pa-ar',
      kind='Recorded metaphor',status='Low specificity',glyph='373',lipi='790',
      evidence='The structured release gives pa-a-ar / pa-ar “seed” (N:314 / N:441); HK:156 gives descendants, literally seed.',
      dates='No usable period specified for these selected records.',
      limits='This leaf-like drawing is not independently established as a seed. Seed / offspring metaphors occur widely; the existing repo already discusses sprout → offspring for sign760.',
      novelty='This Elamite lexical witness is absent from the inspected old Elamite table. The general ancestry / offspring idea is already in the repo and is not newly discovered.'),
 dict(id='staff_affection',title='Staff / sceptre → affection',bridge='ha-at-ti ≈ ha-ti',
      kind='Permissive spelling match',status='Weak sound lead',glyph='25',lipi='142',
      evidence='N:2238 gives ha-at-ti “sceptre”; N:226 gives ha-ti “affection.” They match only after folding consonant doubling. The sceptre entry has source cognate flag ḫaṭṭu.',
      dates='Both selected records: Middle / Neo-Elamite.',
      limits='Gemination may reflect a real sound distinction; homophony is not established. The picture is a person with a staff, not a standalone staff. The borrowing flag reduces language specificity.',
      novelty='Absent from the inspected older Elamite table; conditional resemblance, not an assigned pronunciation.'),
 dict(id='cup_ear',title='Cup / bowl → ear',bridge='si-ir-ri ≈ si-ri',
      kind='Permissive spelling match',status='Weak, late and uncertain',glyph='342',lipi='',
      evidence='HK:2094 tentatively interprets si-ir-ri as a bowl / consecration vessel. HK:2120 includes si-ri “ear(s).” Matching requires consonant-doubling folding.',
      dates='Ear(s): Achaemenid in the legacy gloss; no early sound bridge established.',
      limits='Uncertain picture word, late target, uncertain phonology. Do not confuse this with the suspect English “shale” gloss for si-ir-ri.',
      novelty='Absent from the inspected old Elamite candidate output; not promoted to a reading.'),
 dict(id='cup_true',title='Cup / bowl → true / correct',bridge='si-ir-ri ≈ si-ri',
      kind='Permissive spelling match',status='Weak, late and uncertain',glyph='342',lipi='',
      evidence='The same HK:2120 entry also lists si-ri “true, correct.” This is an alternative to ear, not a second independent supporting inscription.',
      dates='True / correct: Achaemenid in the legacy gloss.',
      limits='Shares all uncertainty and normalization dependence of the cup → ear comparison. Multiple alternatives increase selection freedom.',
      novelty='Absent from the inspected old Elamite candidate output; lexical resemblance only.'),
]


def review(r):
    n=r['picture_noun'];head=r['target_heads'];target=r['target_source_id']
    if r['channel']=='one_edit_whole_form':
        return 'unvalidated_near_spelling','', 'One character edit after permissive normalization; not established homophony. No full source review claimed.'
    if n=='roof' and (head=='protection' or head=='schutz'):
        return 'retained_lexical_lead','roof_protection','Same-form recorded roof / protection senses.'
    if n=='jar' and head=='enemy':
        return 'retained_conditional_stem_lead','jar_enemy','Requires source-supported -r noun-class analysis; not a whole-word identity.'
    if n in {'gate','door'} and target in {'HK:1236','HK:1270'} and 'hof' in head:
        return 'retained_lexical_lead','gate_court','Explicit figurative royal-court sense.'
    if n in {'gate','door'} and target=='HK:2389' and head=='unterstutzung':
        return 'tentative_source_lead','gate_support','Royal support sense requires original dictionary/context verification.'
    if n=='seed' and head=='nachkommenschaft':
        return 'recorded_metaphor_low_specificity','seed_descendants','Seed / offspring concept is not unique and a related concept already occurs in the repo.'
    if n=='staff' and r['picture_word']=='ha-at-ti' and r['target_word']=='ha-ti':
        return 'weak_normalization_dependent_lead','staff_affection','Requires folding doubling; picture word has source cognate/borrowing warning.'
    if n=='cup' and target=='HK:2120':
        lead='cup_ear' if head in {'ohr','ohren'} else 'cup_true'
        return 'weak_normalization_dependent_lead',lead,'Tentative bowl gloss, doubled-consonant folding, Achaemenid target sense.'
    if n=='house' and (head in {'not','neg'} or 'ja nicht' in head):
        return 'already_known_semantic_direction','','House → negative already appears in old Elamite evidence; changed form witnesses do not make it new.'
    if n=='house' and target=='HK:1549':
        return 'quarantined_source_and_morphology','','Truncated silver gloss and possessed/plural house form; not a verified bare-noun rebus.'
    if n=='house' and target in {'HK:6','HK:7'}:
        return 'quarantined_conflicting_interpretations','','Legacy relatives / kin versus structured house interpretation; not independent homonyms.'
    if n=='cup' and head=='shale':
        return 'quarantined_possible_translation_error','','English shale conflicts with tentative German Schale (bowl); inspect source before interpreting.'
    if n in {'gate','door'} and target=='HK:714' and 'auge' in head:
        return 'rejected_orthographic_shortening','','Source says abbreviated writing for elt (eye); spelling identity does not establish spoken homophony.'
    if n=='man':
        return 'rejected_ethnonym_as_picture_word','','Man from Harku / Mimuras is an ethnonym or gentilic, not a bare lexical word for man.'
    if n=='horn' and target=='HK:820':
        return 'rejected_transparent_derivation','','Horn-people / herdsmen is a derived expression, not the bare horn word with an unrelated meaning.'
    if n=='weight' and head=='hang':
        return 'already_known_concept_direction','','Hang ↔ weigh already occurs in the frozen recipes; inanimate derivation is not a new Indus reading.'
    return 'discarded_synonym_inflection_or_editorial','','Reviewed non-near witness supplies a synonym, same-word inflection, untranslated item, uncertain interpretation or editorial fragment; no retained alternative meaning.'


def main():
    rows=O.R.read(OUT/'open_rebus_all_candidates.csv')
    reviewed=[]
    for r in rows:
        disposition,lead,reason=review(r)
        reviewed.append(dict(**r,review_disposition=disposition,lead_id=lead,review_reason=reason))
    O.write('open_rebus_review.csv',reviewed)
    pictures={p['glyph']:p for p in O.R.read(REPO/'work_data/pictures/pictures_blind.csv')}
    enriched=[]
    for lead in LEADS:
        witnesses=[r for r in reviewed if r['lead_id']==lead['id']]
        assert witnesses,lead['id']
        enriched.append(dict(**lead,witness_rows=len(witnesses),witness_ids=';'.join(r['candidate_id'] for r in witnesses),
                             picture_votes=pictures[lead['glyph']]['first_votes'],
                             source_picture_nouns=pictures[lead['glyph']]['agreed_things'],
                             picture_source_ids=';'.join(sorted({r['picture_source_id'] for r in witnesses})),
                             target_source_ids=';'.join(sorted({r['target_source_id'] for r in witnesses}))))
    O.write('open_rebus_curated_leads.csv',enriched)
    # Reference-only occurrence inventory; no outcome-based target selection or test.
    signs={x['lipi']:x['id'] for x in LEADS if x['lipi']}
    inscriptions=O.R.read(BASE.parent/'translation_catalogue/results/all_inscriptions.csv')
    occurrences=[]
    for r in inscriptions:
        # Catalogue sign strings are hyphen-separated three-digit codes.
        tokens=set(re.findall(r'(?<!\d)\d{3}(?!\d)',r['sign_sequence']))
        for sign in sorted(tokens & signs.keys()):
            occurrences.append(dict(lead_id=signs[sign],example_sign=sign,
                                    **{k:r[k] for k in ['catalogue','face_id','reference','city','sign_sequence',
                                                        'existing_proposed_translation','found_at','material','object_type']},
                                    interpretation='Existing proposed reading only. No Elamite inscription translation or archaeological validation.'))
    O.write('open_rebus_example_sign_occurrences.csv',occurrences)
    old=[r for r in O.R.read(REPO/'work_data/lang_m2/evidence.csv') if r['dict']=='elamite_hinzkoch']
    old_unique=sorted({(r['noun'],r['picture_word'],r['soundalike']) for r in old})
    summary=json.loads((OUT/'open_rebus_summary.json').read_text())
    audit=dict(non_near_witnesses_reviewed=sum(r['channel']!='one_edit_whole_form' for r in reviewed),
               near_witnesses_not_promoted=sum(r['channel']=='one_edit_whole_form' for r in reviewed),
               dispositions=dict(collections.Counter(r['review_disposition'] for r in reviewed)),
               retained_semantic_directions=len(enriched),priority_directions=2,
               older_Elamite_witness_rows=len(old),older_distinct_word_pairs=old_unique,
               novelty_scope='Inspected materialized Elamite candidate table and frozen pair recipes, not first in scholarship.',
               occurrence_rows=len(occurrences),occurrence_role='Reference only; no semantic or archaeological inference.',
               validated_Indus_readings=0,language_identification_pvalue=None,colab_units=0)
    (OUT/'open_rebus_review_summary.json').write_text(json.dumps(audit,indent=2)+'\n')
    def drawing(g):
        blob=(REPO/f'work_data/mahadevan_glyphs/{g}.png').read_bytes()
        return f'<img alt="Mahadevan drawing {g}" src="data:image/png;base64,{base64.b64encode(blob).decode()}">'
    cards=[]
    for x in enriched:
        sign=f'Lipi {x["lipi"]} / ' if x['lipi'] else ''
        cards.append(f'''<article class="card"><div class="draw">{drawing(x['glyph'])}<small>{sign}M77 {x['glyph']}</small></div>
<div><span class="tag">{H(x['status'])}</span><h2>{H(x['title'])}</h2><div class="bridge">{H(x['bridge'])}</div>
<p><b>{H(x['kind'])}.</b> {H(x['evidence'])}</p><p><b>Dating:</b> {H(x['dates'])}</p>
<p class="limit">{H(x['limits'])}</p><details><summary>Picture, sources and prior work</summary>
<p>Original first-choice picture votes: {H(x['picture_votes'])}. Alternative picture labels: {H(x['source_picture_nouns'])}. The source agreement level applies to the drawing, not each alternative noun. The drawings are reused from the repo; no new blind archaeological assignment was obtained.</p>
<p>Picture witnesses: {H(x['picture_source_ids'])}; target witnesses: {H(x['target_source_ids'])}. {x['witness_rows']} witness rows, not independent confirmations.</p>
<p>{H(x['novelty'])}</p></details></div></article>''')
    columns=['candidate_id','picture_noun','picture_word','target_word','target_heads','channel','review_disposition','review_reason']
    trs=['<tr>'+''.join('<td>'+H(str(r[k]))+'</td>' for k in columns)+'</tr>' for r in reviewed]
    page=f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>New Elamite rebus leads for Indus signs</title><style>
*{{box-sizing:border-box}}body{{font:16px/1.55 system-ui,sans-serif;color:#1c2931;background:#f3f5f4;margin:0}}
main{{max-width:1160px;margin:auto;padding:36px 24px}}h1{{font-size:clamp(30px,5vw,48px);line-height:1.08;margin:14px 0 18px;letter-spacing:-1px}}h2{{font-size:25px;margin:8px 0}}a{{color:#095c72}}
.eyebrow{{letter-spacing:.12em;font-size:12px;font-weight:750;color:#46636c}}.intro{{max-width:880px;font-size:19px}}.notice{{padding:16px 20px;background:#fff0cf;border-left:4px solid #b27910;border-radius:6px}}
.stats{{display:flex;flex-wrap:wrap;gap:12px;margin:24px 0}}.stat{{background:white;border:1px solid #d9e1df;border-radius:8px;padding:13px 18px;flex:1;min-width:160px}}.stat strong{{display:block;font-size:27px}}
.card{{background:white;border:1px solid #d9e1df;border-radius:12px;padding:24px;display:grid;grid-template-columns:135px 1fr;gap:24px;margin:18px 0}}
.draw img{{width:110px;height:135px;object-fit:contain}}small{{display:block;color:#53666b;font-size:12px}}.tag{{font-size:12px;background:#e4f1ee;color:#145447;border-radius:4px;padding:4px 8px;font-weight:650}}.bridge{{font-size:25px;color:#10576a;font-family:Georgia,serif}}
.limit{{padding:12px 15px;background:#f5f6f5;border-radius:6px}}details{{font-size:14px}}summary{{cursor:pointer;color:#1e606f}}.tablewrap{{overflow:auto;border:1px solid #ccd7d7;max-height:680px;background:white}}table{{border-collapse:collapse;min-width:1220px;width:100%;font-size:13px}}th,td{{text-align:left;padding:10px 12px;vertical-align:top;border-bottom:1px solid #e5eae8}}th{{position:sticky;top:0;background:#eaf0ef}}input{{width:100%;padding:13px;font:inherit;border:1px solid #aebfbe;border-radius:6px;margin:12px 0}}.links{{display:flex;flex-wrap:wrap;gap:12px 20px}}footer{{font-size:13px;color:#52666c;margin:35px 0}}@media(max-width:620px){{main{{padding:24px 15px}}.card{{grid-template-columns:1fr;padding:18px;gap:12px}}.draw{{display:flex;align-items:center;gap:18px}}.draw img{{height:90px;width:75px}}.stats{{gap:8px}}.stat{{min-width:125px;padding:10px}}}}
</style><main><div class="eyebrow">INDUS RESEARCH · ELAMITE CANDIDATE DISCOVERY · 23 NOVEMBER 2026</div>
<h1>New meanings to test,<br>starting from the sign pictures</h1>
<p class="intro">The two priority leads are <b>roof → protection</b> and <b>jar → enemy</b>. They use Elamite words and alternative meanings, without requiring Cúper’s Dravidian sounds or target meanings.</p>
<p class="notice"><b>These are lexical leads, not translated inscriptions.</b> Roof / protection is recorded polysemy. Jar / enemy requires a noun-class analysis. Neither establishes the language of the Indus script, and neither has a verified early picture-word bridge here.</p>
<div class="stats"><div class="stat"><strong>417</strong>drawings inventoried</div><div class="stat"><strong>24 / 73</strong>picture nouns covered</div><div class="stat"><strong>680</strong>raw candidate witnesses</div><div class="stat"><strong>2</strong>priority directions</div></div>
<p>All <b>{sum(x['rows'] for x in summary['source_counts']):,} source rows</b> from five common-vocabulary CSVs and the existing Hinz–Koch-derived table were considered. Filtering leaves {summary['eligible_source_rows']:,} source rows / {summary['eligible_lexical_records']:,} split sense records. These are <b>not independent roots</b>; the resources share dictionary ancestry.</p>
<p>There are 164 conservative-form, 14 permissive-key, six noun-class-stem and 496 one-edit witnesses. All 184 non-near witnesses received the source review below; the 496 one-edit witnesses remain unvalidated. Eight semantic directions are shown with different evidence levels. Witnesses, spellings and senses must not be added together as separate discoveries.</p>
<section id="priority"><h2>Two priority lexical leads</h2><p>Candidate sign values to investigate. No new Indus inscription has been translated.</p>{''.join(cards[:2])}</section>
<h2>Additional directions, with weaker or less specific evidence</h2>{''.join(cards[2:])}
<h2>What changed from Cúper’s search?</h2><p>The earlier search already included Elamite. Its materialized candidate table contains house → negative, jar → lord and roof → his head. This extension allows <b>any lexical target meaning</b>, uses the additional structured vocabulary, and records noun-class stem matches separately. The two priority directions are absent from that table. This is a bounded comparison with existing output, not a claim to have discovered the Elamite words or searched all prior scholarship.</p>
<h2>What would turn a lead into evidence?</h2><p>First verify the dictionary meanings, earliest attestations and sign pictures. Then freeze the proposed sign value and a prediction that distinguishes it from competing meanings. Evaluate that prediction on excluded inscription sequences or independent archaeological observations. Merely attaching “enemy” to the common jar sign does not explain a text; the reading must predict its surrounding signs and grammatical ending consistently. No such validation is claimed here.</p>
<h2>Source checks that prevented false discoveries</h2><p>Gate / door and pillar / post are synonyms. House → negative is already known. The apparent cup → “shale” may be a confusion with German <i>Schale</i> “bowl.” The “eye” spelling <i>el</i> is explicitly an abbreviation for <i>elt</i>, so it is not proof of a spoken door / eye pun. Man-from-a-place expressions are not general words for “man.” These remain visible in the audit.</p>
<h2>Complete candidate audit</h2><label for="filter">Search picture, word, target or review decision</label><input id="filter" type="search" placeholder="Try enemy, protection, shale or already_known"><p id="count">680 / 680 witness rows</p>
<div class="tablewrap"><table><thead><tr>{''.join('<th>'+H(c.replace('_',' '))+'</th>' for c in columns)}</tr></thead><tbody>{''.join(trs)}</tbody></table></div>
<h2>Files and sources</h2><p class="links"><a href="open_rebus_curated_leads.csv">Reviewed leads</a><a href="open_rebus_review.csv">Complete review CSV</a><a href="open_rebus_all_candidates.csv">Raw candidates</a><a href="open_rebus_all_417_pictures.csv">All drawings</a><a href="open_rebus_picture_coverage.csv">Coverage by picture</a><a href="open_rebus_example_sign_occurrences.csv">Existing inscription occurrences</a><a href="open_rebus_summary.json">Search summary</a><a href="open_rebus_review_summary.json">Review summary</a><a href="../OPEN_REBUS.md">Methods and conclusion</a></p>
<p>Occurrences are provided only as a reference for four representative sign mappings. Their existing proposed translations are not Elamite translations, and their distribution has not been used to validate these candidates.</p>
<p><a href="{SOURCE}">Pinned DigitalPasts noun source</a> · <a href="{GRAMMAR}">Basello2023, especially pp. 18–19 and 27–28</a> · <a href="{TREATY}">Badamchi2025, Old Elamite treaty</a>. The treaty verifies the early enemy word; it does not attest the jug word. Basello discusses the uncertain sound system as well as noun-class -r.</p>
<footer>Reused repo drawings and picture descriptions. No new blind semantic assignment. Search {summary['runtime_seconds']}s locally; Colab 0. No probability of language identity was calculated.</footer></main>
<script>const f=document.querySelector('#filter'),rows=[...document.querySelectorAll('tbody tr')];f.addEventListener('input',()=>{{let n=0;for(const r of rows){{r.hidden=!r.textContent.toLowerCase().includes(f.value.toLowerCase());if(!r.hidden)n++}}document.querySelector('#count').textContent=n+' / '+rows.length+' witness rows'}});</script></html>'''
    (OUT/'open_rebus.html').write_text(page)
    print(json.dumps(audit,indent=2))


if __name__=='__main__':main()
