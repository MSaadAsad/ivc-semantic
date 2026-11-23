"""Elamite lexical candidates for signs outside the current phonetic key.

The recipient language is unspecified. No Dravidian vocabulary is imported.
"""
import base64
import collections
import csv
import html
import json
from pathlib import Path
import re
import time

import open_rebus as O

H=html.escape


def tokens(s):return s.split('-')


def noun_votes(raw,noun):
    return sum(int(bit.rsplit(':',1)[1]) for bit in raw.split(';') if bit and bit.rsplit(':',1)[0]==noun)


def main():
    started=time.monotonic()
    master={r['sign'] for r in O.R.read(O.BASE.parent/'translation_catalogue/results/all_163_sign_readings.csv')}
    true={r['sign']:r for r in O.R.read(O.REPO/'work_data/signlist/true_signs.csv')}
    roles={r['sign']:r for r in O.R.read(O.REPO/'work_data/reader_v3/soundfree_lexicon.csv')}
    pictures={r['glyph']:r for r in O.R.read(O.REPO/'work_data/pictures/pictures_blind.csv')}
    unresolved={s for s in true if s not in master and true[s]['true_sign'] not in master}
    cross=[r for r in O.R.read(O.REPO/'work_data/lipi_mahadevan_crosswalk.csv') if r['rank_for_lipi_sign']=='1' and r['lipi'] in unresolved]
    entries,_,_=O.load_entries(O.REPO.parent/'elamite-sources')
    constants=O.source_constants();anchors=[]
    for c in cross:
        p=pictures.get(c['mahadevan'])
        if not p or p['level'] not in {'3of3','2of3'}:continue
        for noun in p['agreed_things'].split(';'):
            for e in entries:
                if O.picture_match(e,noun,constants):
                    anchors.append(dict(sign=c['lipi'],canonical_sign=true[c['lipi']]['true_sign'],mahadevan=c['mahadevan'],
                                        picture_noun=noun,picture_votes=p['first_votes'],crosswalk_share=c['share_of_lipi_sign'],
                                        source=e['source'],source_id=e['id'],word=e['word'],raw_gloss=e['raw_gloss'],
                                        lexical_head='; '.join(e['heads']),period=e['period'],cognate_flag=e['cognate'],
                                        flags='; '.join(e['flags']),status='Literal dictionary anchor only; not a recovered Indus word.'))
    O.write('unread_literal_Elamite_inventory.csv',anchors)
    leads={r['id']:r for r in O.R.read(O.OUT/'open_rebus_curated_leads.csv')}
    reviewed=[r for r in O.R.read(O.OUT/'open_rebus_review.csv') if r['lead_id']]
    candidates={}
    for r in reviewed:
        for c in cross:
            if c['mahadevan'] not in r['mahadevan_glyphs'].split(';'):continue
            key=(c['lipi'],r['lead_id'],r['picture_noun'])
            if key in candidates:continue
            p=pictures[c['mahadevan']];tr=true[c['lipi']];lead=leads[r['lead_id']]
            votes=noun_votes(p['first_votes'],r['picture_noun'])
            strong=float(c['share_of_lipi_sign'])>=.75 and votes>=2
            candidates[key]=dict(sign=c['lipi'],canonical_sign=tr['true_sign'],lead_id=r['lead_id'],
                                 Elamite_candidate=lead['title'].split(' → ')[1],Elamite_forms=lead['bridge'],
                                 picture_noun=r['picture_noun'],mahadevan=c['mahadevan'],shape=tr['shape'],
                                 crosswalk_share=c['share_of_lipi_sign'],picture_first_votes=p['first_votes'],noun_first_votes=votes,
                                 compound_note=tr['compound_of'],drawing_support_filter=strong,
                                 existing_soundfree_role=roles.get(c['lipi'],{}).get('soundfree_gloss',''),
                                 dates=lead['dates'],lexical_limitations=lead['limits'],
                                 status='Proposed Elamite-derived reading to investigate; borrowing is not established.')
    candidates=list(candidates.values())
    O.write('unread_Elamite_rebus_candidates.csv',candidates)
    inscriptions=O.R.read(O.BASE.parent/'translation_catalogue/results/all_inscriptions.csv')
    signs={c['sign'] for c in candidates};by_sign=collections.defaultdict(list);occurrences=[]
    for r in inscriptions:
        for sign in sorted(set(tokens(r['sign_sequence']))&signs):
            by_sign[sign].append(r)
            occurrences.append(dict(candidate_sign=sign,**{k:r[k] for k in ['catalogue','face_id','reference','city','sign_sequence',
                'existing_proposed_translation','found_at','material','object_type']},
                status='Original proposed reading retained; no new full-text translation.'))
    O.write('unread_candidate_occurrences.csv',occurrences)
    profiles=[]
    for sign in sorted(signs):
        for catalogue in ['Lipi','Mahadevan']:
            rr=[r for r in by_sign[sign] if r['catalogue']==catalogue]
            prev=collections.Counter();nxt=collections.Counter();initial=final=0
            for r in rr:
                seq=tokens(r['sign_sequence']);initial+=seq[0]==sign;final+=seq[-1]==sign
                for i,s in enumerate(seq):
                    if s!=sign:continue
                    if i:prev[seq[i-1]]+=1
                    if i+1<len(seq):nxt[seq[i+1]]+=1
            profiles.append(dict(sign=sign,catalogue=catalogue,face_records=len(rr),unique_formulas=len({r['sign_sequence'] for r in rr}),
                                 first_position_faces=initial,last_position_faces=final,
                                 sites=json.dumps(dict(collections.Counter(r['city'] for r in rr)),ensure_ascii=False),
                                 previous_signs=json.dumps(dict(prev.most_common())),next_signs=json.dumps(dict(nxt.most_common())),
                                 interpretation='Descriptive reused-corpus context, not independent semantic validation.'))
    O.write('unread_candidate_profiles.csv',profiles)
    # Display a bounded shortlist; alternatives for the same word are not all assigned.
    shortlist=[('621','gate_court','door'),('362','gate_court','door'),('572','gate_court','door'),
               ('360','gate_court','gate'),('202','seed_descendants','seed'),('484','roof_protection','roof')]
    lookup={(r['sign'],r['lead_id'],r['picture_noun']):r for r in candidates}
    focus=[lookup[k] for k in shortlist]
    O.write('unread_focus_candidates.csv',focus)
    examples={
        '621':('M-180','Candidate label: court — house. The catalogue instead says “Of the Stored house”; registrar/title is another existing sound-free guess. No completed reading is established.'),
        '362':('H-345','Illustrative gap fill: “Manager of the [court] house.” Only [362] is replaced; manager/house and English syntax remain inherited proposals, not independently verified words.'),
        '572':('H-1021','Candidate court term within a longer name-like sequence; remaining proposed Banner / First-ward / Star / House / Manager values are not confirmed by this guess.'),
        '360':('H-2217','Candidate court / gate followed by unknown257. No full reading supplied.'),
        '202':('H-183','Candidate offspring/descendants for [202], before proposed junior. The doubled seed-like picture and missing dates remain qualifications.'),
        '484':('H-2362','Candidate protection for [484], before proposed junior. Roof has no first-choice votes for this drawing; ladder has two. Kept as a lower-support possibility.'),
    }
    cards=[]
    for r in focus:
        reference,note=examples[r['sign']]
        example=next(x for x in by_sign[r['sign']] if x['catalogue']=='Lipi' and x['reference']==reference)
        p=next(x for x in profiles if x['sign']==r['sign'] and x['catalogue']=='Lipi')
        raw=(O.REPO/f'work_data/mahadevan_glyphs/{r["mahadevan"]}.png').read_bytes()
        image=base64.b64encode(raw).decode()
        cards.append(f'''<article><div class="drawing"><img alt="M77 {r['mahadevan']}" src="data:image/png;base64,{image}"><small>Lipi {r['sign']} · M77 {r['mahadevan']}</small></div><div>
<span class="tag">Outside the frozen 163-sign phonetic key</span><h2>{r['sign']}: {H(r['Elamite_candidate'])}</h2>
<p class="word">{H(r['Elamite_forms'])}</p><p><b>Existing role:</b> {H(r['existing_soundfree_role'])}</p>
<p><b>Actual find:</b> {H(reference)} · {H(example['city'])} · <code>{H(example['sign_sequence'])}</code></p>
<p class="proposal">{H(note)}</p><p><b>Recorded location:</b> {H(example['found_at'])}</p>
<p>{p['face_records']} Lipi faces / {p['unique_formulas']} formulas; {p['last_position_faces']} end with this sign. These are descriptive counts, not semantic confirmations.</p>
<details><summary>Picture and source qualifications</summary><p>Picture first choices: {H(r['picture_first_votes'])}. Rank-one crosswalk share: {H(r['crosswalk_share'])}. {H(r['dates'])}</p><p>{H(r['lexical_limitations'])}</p></details></div></article>''')
    summary=dict(frozen_phonetic_key_signs=len(master),sign_inventory_rows=len(true),unresolved_sign_ids=len(unresolved),
                 literal_anchor_rows=len(anchors),unresolved_signs_with_literal_anchors=len({r['sign'] for r in anchors}),
                 rebus_candidate_rows=len(candidates),unresolved_signs_with_rebus_candidates=len(signs),
                 focus_signs=[r['sign'] for r in focus],occurrence_rows=len(occurrences),
                 recipient_language='Unspecified; no Dravidian lexical match required.',
                 established_borrowings=0,validated_new_translations=0,
                 runtime_seconds=round(time.monotonic()-started,2),colab_units=0)
    (O.OUT/'unread_Elamite_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    page=f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Elamite candidates for unread Indus signs</title>
<style>*{{box-sizing:border-box}}body{{font:16px/1.55 system-ui;color:#20313a;background:#f2f5f4;margin:0}}main{{max-width:1120px;margin:auto;padding:36px 24px}}h1{{font-size:40px;line-height:1.1}}h2{{margin:8px 0;font-size:26px}}a{{color:#075c74}}article{{display:grid;grid-template-columns:135px 1fr;gap:22px;background:white;border:1px solid #d4dfdc;border-radius:12px;padding:24px;margin:20px 0}}img{{width:110px;height:135px;object-fit:contain}}small{{display:block;font-size:12px;color:#53666e}}.tag{{font-size:12px;color:#235b4c;background:#e1f0e9;padding:4px 7px;border-radius:4px}}.word{{font-size:23px;font-family:Georgia;color:#0b576b}}.proposal{{background:#eef4f2;padding:13px 16px;border-radius:6px}}.notice{{background:#fff0d1;border-left:4px solid #ae7713;padding:16px 20px}}details{{font-size:14px}}summary{{cursor:pointer;color:#075c74}}code{{overflow-wrap:anywhere}}@media(max-width:600px){{main{{padding:22px 15px}}h1{{font-size:32px}}article{{grid-template-columns:1fr;padding:18px;gap:10px}}.drawing{{display:flex;align-items:center;gap:20px}}img{{width:70px;height:85px}}}}</style>
<main><small>INDUS RESEARCH · ELAMITE VOCABULARY FOR UNRESOLVED SIGNS · 23 NOVEMBER 2026</small>
<h1>Elamite terms for the gaps in the script</h1><p>The recipient language is left open. The question is whether an Elamite term could supply a reading for a sign that lacks a value in the current phonetic key—not whether that word survives in modern Dravidian.</p>
<p class="notice"><b>Candidate readings, not demonstrated loanwords.</b> A dictionary match and a plausible English gap fill do not establish a sign's sound, meaning or borrowing history. Court candidates 362/621/572/360 are competing sign assignments; they have not all been given one shared pronunciation.</p>
<p>{len(unresolved)} sign IDs lie outside the frozen key after removing already-covered canonical allographs. The full inventory finds literal Elamite dictionary anchors for {summary['unresolved_signs_with_literal_anchors']} unresolved sign IDs, and the reviewed rebus directions touch {len(signs)}. Compound and uncertain-picture matches remain labelled in the files.</p>
<p><b>Do the occurrences become more coherent?</b> A <a href="../COHERENCE_REVIEW.md">review of all 127 shortlisted contexts</a> finds 362 court the clearest conditional institutional fit. Other institutional labels could fit too; 621 court does not clearly beat stored/registrar, while 202 offspring and 484 protection leave substantial difficulties. No comparative semantic improvement has been demonstrated. <a href="coherence_all_shortlisted_contexts.csv">Every original reading and illustrative gap fill</a>.</p>
{''.join(cards)}<h2>What is new, and what needs testing?</h2><p>Cúper already discusses these drawings, their slots and several tentative meanings. This extension supplies Elamite lexical alternatives for unresolved phonetic values; it does not claim to discover their structural roles. A first source check should prioritize door/court for 362 or 621. Establish its early lexical attestation, compare its behaviour with competing institutional readings, then test a frozen assignment on new evidence. Loanword status requires a supported sound and meaning plus a credible borrowing history.</p>
<p><a href="../UNREAD_ELAMITE.md">Interpretation and scope</a> · <a href="unread_focus_candidates.csv">Shortlist</a> · <a href="unread_Elamite_rebus_candidates.csv">All unresolved rebus candidates</a> · <a href="unread_literal_Elamite_inventory.csv">Literal lexical inventory</a> · <a href="unread_candidate_occurrences.csv">Every recorded occurrence</a> · <a href="unread_candidate_profiles.csv">Sequence profiles</a> · <a href="unread_Elamite_summary.json">Summary</a></p>
<small>Existing picture judgements and catalogues are reused. No fresh independent semantic assignment or language-identification result. Runtime {summary['runtime_seconds']}s; Colab 0.</small></main></html>'''
    (O.OUT/'unread_elamite.html').write_text(page)
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
