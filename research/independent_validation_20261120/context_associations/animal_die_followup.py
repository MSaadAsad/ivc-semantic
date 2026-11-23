"""Execute frozen 923-family eligibility screen and release physical-pair evidence.

This is evidence recovery and eligibility testing. It must not report an animal
prediction score or an issuer/contents comparison when their prerequisites fail.
Uses Python standard library; run from any directory in the checkout.
"""
import collections
import csv
import html
import json
import shutil
from pathlib import Path

BASE = Path(__file__).resolve().parent
REPO = BASE.parents[2]
OUT = BASE / 'results'
PAPER = 'https://doi.org/10.5281/zenodo.5513821'
LATER = 'https://doi.org/10.1080/02666030.2024.2401206'
PHOTO_ROOT = 'evidence/tmp/002390x_3335_yajnadevam_repo_trace_20260531/repo/public/seal_images/'
SNAPSHOT = '727dfd411a4faa44d193d204757540d45c7b139b'


def read(path):
    with path.open() as f:
        return list(csv.DictReader(f))


def write(name, rows):
    with (OUT / name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def norm(text):
    return tuple('706' if s == '705' else s for s in text.split('-'))


def distance(a, b):
    """Token edit distance, not character distance on printed sign numbers."""
    row = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        new = [i]
        for j, y in enumerate(b, 1):
            new.append(min(row[j] + 1, new[-1] + 1, row[j - 1] + (x != y)))
        row = new
    return row[-1]


def screen():
    pools = {n: read(REPO / 'work_data/copper' / f'{n}.csv') for n in ['objects', 'm77_objects']}
    seeds = {norm('706-033-923-740'), norm('706-033-923-740-001')}
    complete = {norm(r['text']) for rows in pools.values() for r in rows if r['complete'] == 'True'}
    family = set(seeds)
    while True:
        added = {t for t in complete - family if any(distance(t, q) <= 1 for q in family)}
        if not added:
            break
        family.update(added)
    rows = []
    for pool, records in pools.items():
        for r in records:
            if '923' not in r['text'].split('-'):
                continue
            if r['complete'] != 'True':
                status = 'excluded: incomplete; family identity unresolved'
            elif norm(r['text']) in family:
                status = 'excluded: known formula or connected near-variant'
            else:
                status = 'candidate: different formula; outcome/source review required'
            rows.append(dict(catalogue=pool, reference=r.get('cisi', '') or r.get('textnum', ''),
                             object_or_text_id=r.get('obj', '') or r.get('textnum', ''),
                             text=r['text'], other_text=r['second'], complete=r['complete'], status=status))
    write('animal_prediction_eligibility.csv', rows)
    event_counts, secondary = [], []
    for pool in ['lipi', 'new', 'mah_all']:
        records = json.loads((REPO / f'work_data/sem/events_{pool}.json').read_text())
        for kind in ['ctab', 'mtab']:
            subset = [r for r in records if r['kind'] == kind]
            hits = [r for r in subset if '923' in r['signs']]
            event_counts.append(dict(event_source=pool, kind=kind, event_rows=len(subset),
                                     sign923_event_rows=len(hits),
                                     note='Copy-events, not raw objects. Sources overlap; never sum as independent finds.'))
            if kind == 'mtab':
                for r in hits:
                    secondary.append(dict(event_source=pool, event_id=r['id'], reference=r['cisi'],
                                          site=r['site'], text=r['full_text'],
                                          status='existing discovery record; different material; no fresh blind outcome'))
    write('animal_prediction_event_coverage.csv', event_counts)
    write('animal_prediction_other_tablets.csv', secondary)
    eligible = [r for r in rows if r['status'].startswith('candidate:')]
    return dict(raw_first_catalogue_rows=len(pools['objects']), raw_second_catalogue_rows=len(pools['m77_objects']),
                sign923_raw_rows=len(rows), known_formula_rows=sum('known formula' in r['status'] for r in rows),
                incomplete_rows=sum('incomplete' in r['status'] for r in rows),
                eligible_different_formula_rows=len(eligible), animal_prediction_trials=0,
                animal_prediction_test_run=False, event_counts=event_counts,
                warning='Catalogue rows overlap. Zero eligible trials is absence of a test, not failed prediction.')


def review_pairs():
    objs = {r['face']: r for r in read(REPO / 'work_data/stamps/objects.csv')}
    candidates = read(OUT / 'animal_followup_die_candidates.csv')
    reviewed = []
    for r in candidates:
        imp, seal = objs[r['imp_face']], objs[r['seal_face']]
        if r['seal_cisi'] == 'M-895':
            status = 'prior Cuper image rejection; no new positive match'
            observation = ('L-161 elephant versus M-895 catalogue unicorn/different design already inspected in jobs/out/stamps.md. '
                           'Ten related Lothal impressions are not ten newly verified matches; not all independently re-inspected here.')
            new = False
        elif r['seal_cisi'] in {'M-1697', 'M-1777'}:
            status = 'unresolved: required exact-object photographs missing'
            observation = ('No seal photograph in the recovered tracked image set. For the Rupar candidate, '
                           'Rpr-1 photographs show a different two-sided object; they cannot substitute for object 3872.2.')
            new = True
        else:
            status = 'unresolved: photos inspected; physical identity not established'
            observation = {
                'M-712': 'K-82 preserves a partial unicorn impression and four-sign layout; M-712 has compatible text/species. No diagnostic shared carving flaw is securely resolved at this image quality.',
                'M-122': 'L-146 preserves the three-sign line and partial unicorn. M-122 is a complete unicorn seal. Compatible text is not a verified identical die; worn details and perspective prevent secure identification.',
                'M-1359': 'M-1359 is a text-only rectangular object; recovered B-F views show the other sides. L-146 has animal traces below the line. A different format is a warning, but possible separate stamping prevents a categorical image-only exclusion.'
            }[r['seal_cisi']]
            new = True
        reviewed.append(dict(impression=r['imp_cisi'] if r['imp_cisi'] != '-' else 'Rupar object 3872, face 2',
                             seal=r['seal_cisi'], text=r['imp_signs'], status=status,
                             followup_review=new, observation=observation,
                             impression_photos=imp['photos'], seal_photos=seal['photos'],
                             package_contents='', contents_basis='No independently identified contents recovered.'))
    write('physical_die_candidate_review.csv', reviewed)
    # These are literature identifications, not new die discoveries by this script.
    # Frenez 2020 p22 explicitly includes both L-201 and L-208; 2024 prose
    # assigns L-208 indirectly through another seal while its figure includes L-6.
    # Preserve that conflict rather than silently choosing a preferred reading.
    links = [
        dict(seal='L-6', impression='L-201', published_match='Frenez 2020 p22, citing Parpola 2007 pp6-7',
             own_image_check='L-6 available; L-201 photo unavailable; no independent die confirmation here',
             source_conflict='No direct conflict found for this pair', container='Undiagnostic',
             context='warehouse', source_marker='filled circle'),
        dict(seal='L-6', impression='L-208', published_match='Frenez 2020 p22 and figure1 p23',
             own_image_check='Both photos inspected; worn partial impressions do not independently resolve the die',
             source_conflict='Frenez 2024 prose describes an indirect L-201/L-208 connection via an undiscovered seal; figure11 still juxtaposes L-6/L-208. Retain unresolved.',
             container='Single rope', context='other context', source_marker='open square'),
        dict(seal='L-37', impression='L-210', published_match='Frenez 2020 p22 and figure1 p23; reiterated Frenez 2024 figure11',
             own_image_check='Both photos inspected: corresponding upper impression, partial four-sign line and unicorn; published identification retained, not a new independent geometric verification',
             source_conflict='No direct conflict found for this pair', container='Locker',
             context='other context', source_marker='open square'),
    ]
    for r in links:
        r.update(container_source='Frenez 2020 table2 part2, p32 (PDF page12)',
                 container_is_contents=False, package_contents='', issuer_contents_trial_eligible=False,
                 source_url=PAPER, later_source_url=LATER)
    write('published_physical_links_and_context.csv', links)
    return reviewed, links


def table(rows, cols):
    return '<table><thead><tr>' + ''.join(f'<th>{html.escape(c)}</th>' for c in cols) + '</tr></thead><tbody>' + ''.join(
        '<tr>' + ''.join(f'<td>{html.escape(str(r.get(c, "")))}</td>' for c in cols) + '</tr>' for r in rows) + '</tbody></table>'


def present(summary, reviewed, links):
    shutil.copy2(BASE / 'FOLLOWUP_PROTOCOL.md', OUT / 'followup_protocol.md')
    imgs = OUT / 'die_images'
    imgs.mkdir(exist_ok=True)
    for p in (BASE / 'sources/die_images').glob('*.jpg'):
        shutil.copy2(p, imgs / p.name)
    image_sources = [dict(file=p.name, upstream_path=PHOTO_ROOT + p.name, upstream_commit=SNAPSHOT,
                          original_url=f'https://github.com/Cuuper22/ivc/blob/{SNAPSHOT}/{PHOTO_ROOT}{p.name}',
                          treatment='Unmodified recovered catalogue reproduction; review orientation per panel; no automated die match claimed.')
                     for p in sorted(imgs.glob('*.jpg'))]
    write('physical_photo_sources.csv', image_sources)
    panels = [('K-82_A.jpg', 'M-712_a.jpg', 'Unresolved: K-82 / M-712'),
              ('L-146_A_L-146_B.jpg', 'M-122_a.jpg', 'Unresolved: L-146 / M-122'),
              ('L-146_A_L-146_B.jpg', 'M-1359_a.jpg', 'Unresolved: L-146 / M-1359'),
              ('L-210_A_1-2.jpg', 'L-37_a.jpg', 'Published match: L-210 / L-37'),
              ('L-208_A_1-2.jpg', 'L-6_a.jpg', 'Published L-208 / L-6 link: later prose conflict retained')]
    cards = ''.join('<section><h3>' + title + '</h3><div class="pair">' + ''.join(
        f'<figure><a href="die_images/{n}"><img src="die_images/{n}" alt="{n}"></a><figcaption>{n}</figcaption></figure>'
        for n in (a, b)) + '</div></section>' for a, b, title in panels)
    body = f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Animal prediction and physical seal matches</title><style>
body{{font:17px/1.55 system-ui,sans-serif;color:#203044;background:#f7f5ef;max-width:1140px;margin:40px auto;padding:0 22px}}
h1{{font-size:36px;line-height:1.15}}h2{{margin-top:40px}}a{{color:#125f79}}.callout{{padding:20px;background:#e4eeed;border-left:5px solid #237a73}}
table{{border-collapse:collapse;width:100%;font-size:14px;background:white}}td,th{{border:1px solid #d3d9d9;padding:10px;text-align:left;vertical-align:top}}th{{background:#e7ebe8}}
.scroll{{overflow:auto}}.pair{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}figure{{margin:0;padding:15px;background:white}}img{{width:100%;height:400px;object-fit:contain}}figcaption{{font-size:13px;color:#536575}}
section{{margin:32px 0}}@media(max-width:650px){{.pair{{grid-template-columns:1fr}}h1{{font-size:29px}}img{{height:320px}}}}
</style><h1>Which new tests could actually be run?</h1><p>23 November 2026 · source recovery after the prior-work review</p>
<div class="callout"><b>No fresh 923-family prediction or issuer-versus-contents experiment could be scored.</b>
The search recovered actual photographs and published physical links beyond the 15 exact-text candidates. Neither an existing formula in another catalogue nor a known container type supplies a new semantic validation.</div>
<h2>1. Sign 923: elephant-related content</h2><p>The frozen prediction concerns copper tablets with genuinely different complete text families. In {summary['raw_first_catalogue_rows']} first-catalogue and {summary['raw_second_catalogue_rows']} second-catalogue records (overlapping objects), {summary['sign923_raw_rows']} records contain 923: {summary['known_formula_rows']} repeat the known family and {summary['incomplete_rows']} is incomplete. Eligible new families: <b>{summary['eligible_different_formula_rows']}</b>. The new-event subset has 38 copper and 85 other tablet events, with no 923 in either. These are coverage counts, not failures of the prediction.</p>
<p>Parpola 2008's discussion of figure1 connects the elephant B6 and horned-tiger B12 designs through a shared inscription. This is previously published context, not a fresh holdout: a different picture does not by itself establish a different text family. It also cautions against assuming that a shared inscription simply names the animal.</p>
<p><a href="animal_prediction_eligibility.csv">All 923 copper candidates and exclusions</a> · <a href="animal_prediction_event_coverage.csv">Event coverage</a> · <a href="animal_prediction_other_tablets.csv">Other-material discovery records</a></p>
<h2>2. Seal identity before issuer or contents</h2><p>The old 15 exact-text pairs remain unverified physical matches. Cúper had already rejected the Lothal elephant/M-895 comparison by image. Here three remaining pairs have both sides inspected; two others lack required exact-object photographs. No diagnostic common carving defect was established. The recovered Rupar Rpr-1 images are a different object and are not substituted for the unnumbered candidate.</p>
{cards}<h2>Published matches and independent context labels</h2><p>These physical identifications belong to Parpola and Frenez. They are additions to this continuation's explicit evidence table, not newly discovered matches. The L-6/L-208 source discrepancy remains visible. “Locker,” “single rope” and “undiagnostic” describe supports/fastenings, not what was stored.</p>
<div class="scroll">{table(links, ['seal','impression','container','context','own_image_check','source_conflict'])}</div>
<p>Independent package contents for these links: <b>none recovered</b>. Thus there is no issuer-versus-commodity test result. One seal could identify a person, office, institution, commodity or a combination; container backing alone does not decide among them.</p>
<p><a href="physical_die_candidate_review.csv">All 15 candidate reviews</a> · <a href="published_physical_links_and_context.csv">Published physical links and context evidence</a> · <a href="physical_photo_sources.csv">Photo sources</a></p>
<h2>What changed, and what was already done?</h2><p>New here: a frozen eligibility screen; recovery and inspection of actual candidate photographs; explicit publication-to-object links and object-specific context categories omitted from the exact-text shortlist; retention of a source disagreement. Already done by Cúper: broad animal/sign tests, family/copy controls, ordinary-seal animal transfer and the L-161/M-895 photo rejection. Already done in scholarship: Lothal die identifications and cross-container use. These are credited rather than presented as new tests.</p>
<p>The next required observations are a securely identified 923-bearing tablet from a different text family, and independently identified contents for physically matched sealings. We have not recovered either in this search. This bounded search is not a claim that neither exists anywhere.</p>
<p>Sources: <a href="{PAPER}">Frenez 2020, pp22–23 and tables1–2</a>; <a href="{LATER}">Frenez 2024, figure11 and discussion</a>; <a href="https://tuhat.helsinki.fi/ws/portalfiles/portal/127257447/Parpola_A_2008._Copper_tablets_from_Mohenjo_daro._ECL_During_Caspers_Vol.pdf">Parpola 2008, figure1 and discussion</a>. <a href="followup_protocol.md">Frozen protocol</a>. Colab units: 0.</p></html>'''
    (OUT / 'animal_die_followup.html').write_text(body)


def main():
    OUT.mkdir(exist_ok=True)
    summary = screen()
    reviewed, links = review_pairs()
    summary.update(exact_text_candidates=len(reviewed), existing_candidate_physical_matches_verified_here=0,
                   candidate_pairs_both_images_reviewed_here=3, published_seal_impression_links_recovered=len(links),
                   published_links_with_source_conflict=1, independently_verified_new_die_matches=0,
                   issuer_contents_test_run=False, issuer_contents_eligible_trials=0, colab_units=0)
    assert summary['sign923_raw_rows'] == 22
    assert summary['known_formula_rows'] == 21 and summary['incomplete_rows'] == 1
    assert summary['eligible_different_formula_rows'] == 0
    assert len(reviewed) == 15 and len(links) == 3
    assert all(not r['issuer_contents_trial_eligible'] for r in links)
    (OUT / 'animal_die_followup_summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    present(summary, reviewed, links)
    print(json.dumps({k:v for k,v in summary.items() if k != 'event_counts'}, indent=2))


if __name__ == '__main__':
    main()
