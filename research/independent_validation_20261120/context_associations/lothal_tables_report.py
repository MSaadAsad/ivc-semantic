"""Human-readable report for the full published Lothal table expansion."""
import collections
import html
import json
import shutil

from lothal_tables import BASE, INPUT, OUT, SOURCE, CATEGORIES, GROUPS, write


def label(s):
    return s.replace('_', ' ').capitalize()


def table(rows, columns):
    return '<div class="scroll"><table><thead><tr>' + ''.join(f'<th>{html.escape(title)}</th>' for key, title in columns) + '</tr></thead><tbody>' + ''.join(
        '<tr>' + ''.join(f'<td>{html.escape(str(r.get(key, "")))}</td>' for key, title in columns) + '</tr>' for r in rows) + '</tbody></table></div>'


def coverage_chart(categories):
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 480" role="img" aria-labelledby="t d"><title id="t">Source container categories and existing transcription coverage</title><desc id="d">Each bar counts archaeological objects. Green has an existing machine-readable inscription; orange lacks one.</desc><rect width="900" height="480" fill="#faf8f2"/>']
    for i, r in enumerate(categories):
        y = 52 + 32*i
        a, b = r['corpus_joined_objects'], r['missing_transcriptions']
        out += [f'<text x="12" y="{y+18}" font-family="sans-serif" font-size="15">{label(r["container"])}</text>',
                f'<rect x="190" y="{y}" width="{a*23}" height="23" fill="#287e78"/>',
                f'<rect x="{190+a*23}" y="{y}" width="{b*23}" height="23" fill="#d28b38"/>',
                f'<text x="{200+(a+b)*23}" y="{y+18}" font-family="sans-serif" font-size="14">{a+b} ({a} joined / {b} missing)</text>']
    out += ['<rect x="190" y="428" width="17" height="17" fill="#287e78"/><text x="216" y="442" font-family="sans-serif" font-size="14">Existing inscription</text>',
            '<rect x="405" y="428" width="17" height="17" fill="#d28b38"/><text x="431" y="442" font-family="sans-serif" font-size="14">Missing transcription</text></svg>']
    (OUT / 'category_coverage.svg').write_text(''.join(out))


def die_chart(objects, members):
    by_ref = {o['cisi']: o for o in objects}
    counts = collections.Counter((r['published_die_group'], by_ref[r['cisi']]['container']) for r in members)
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 490" role="img" aria-labelledby="t d"><title id="t">Published repeated seals and their support categories</title><desc id="d">Numbers count sealings in Frenez2020 published die groups. Multiple impressions can put an object in several groups. These are not independent validation trials.</desc><rect width="1000" height="490" fill="#faf8f2"/>']
    for i, c in enumerate(CATEGORIES):
        x = 170 + 72*i
        out.append(f'<text transform="translate({x+23},170) rotate(-55)" font-family="sans-serif" font-size="13">{label(c)}</text>')
    for j, g in enumerate(GROUPS):
        y = 195 + 36*j
        out.append(f'<text x="8" y="{y+23}" font-family="sans-serif" font-size="15">{label(g)}</text>')
        for i, c in enumerate(CATEGORIES):
            n = counts[g, c]
            fill = '#d5e8e4' if n else '#eeede7'
            out.append(f'<rect x="{170+72*i}" y="{y}" width="63" height="29" fill="{fill}"/>')
            out.append(f'<text x="{201+72*i}" y="{y+21}" text-anchor="middle" font-family="sans-serif" font-size="15">{n or "–"}</text>')
    out.append('<text x="8" y="480" font-family="sans-serif" font-size="13">Source: Frenez2020 table1 + table2. Published identifications; container type is not contents.</text></svg>')
    (OUT / 'published_die_uses.svg').write_text(''.join(out))


def report(summary, categories, dies, predictions, objects, faces):
    import csv
    with (OUT / 'repeated_die_memberships.csv').open() as f:
        members = list(csv.DictReader(f))
    reviews = {r['cisi']: r['photo_review'] for r in csv.DictReader((INPUT / 'photo_review.csv').open())}
    source_photos = OUT / 'recovered_photos'
    source_photos.mkdir(exist_ok=True)
    for p in (INPUT / 'recovered_photos').glob('*.jpg'):
        shutil.copy2(p, source_photos / p.name)
    photo_sources = [dict(file=p.name, source_path='evidence/tmp/002390x_3335_yajnadevam_repo_trace_20260531/repo/public/seal_images/'+p.name,
                          original_upstream_commit='727dfd411a4faa44d193d204757540d45c7b139b',
                          reproduced_as='Unchanged catalogue reproduction; modern collection annotations are not ancient signs.')
                     for p in sorted(source_photos.glob('*.jpg'))]
    write('recovered_photo_sources.csv', photo_sources)
    shutil.copy2(BASE / 'LOTHAL_EXPANSION.md', OUT / 'protocol.md')
    coverage_chart(categories)
    die_chart(objects, members)
    corrections = [
        dict(cisi='L-125', old_inference='TAG:L interpreted as soft cloth/reed/cord bale', source_category='Wooden box'),
        dict(cisi='L-138', old_inference='TAG:L interpreted as soft cloth/reed/cord bale', source_category='Structure'),
        dict(cisi='L-142', old_inference='TAG:P interpreted as smooth token without packaging', source_category='Wooden box'),
    ]
    write('old_subtype_inference_differences.csv', corrections)
    missing = [dict(cisi=o['cisi'], container=o['container'], context=o['context'],
                    photo_available=bool(o['recovered_photos']), photo_files=o['recovered_photos'],
                    review=reviews[o['cisi']]) for o in objects if not o['corpus_joined']]
    write('missing_object_photo_review.csv', missing)
    # Only three of the source categories are distinctly architectural/locker;
    # ambiguous and undiagnostic categories must stay visible in the master table.
    useful = [o for o in objects if o['container'] not in {'undiagnostic', 'other_types'}]
    summary['specific_support_classifications'] = len(useful)
    summary['specific_support_classifications_with_text'] = sum(o['corpus_joined'] for o in useful)
    summary['new_specific_labels_with_text'] = sum(o['corpus_joined'] and o['newly_supplied_backing_label'] for o in useful)
    summary['missing_objects_with_recovered_photos'] = sum(r['photo_available'] for r in missing)
    summary['subtype_inference_differences_reviewed'] = len(corrections)
    summary['source_context_and_category_cells_verified'] = 93
    (OUT / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    rows = []
    for o in objects:
        flags = ('Existing backing evidence' if o['prior_specific_backing_evidence'] else 'New backing label')
        if o['same_published_die_as_prior_evidence']:
            flags += '; same published die as prior evidence'
        photos = o['recovered_photos'].split('; ') if o['recovered_photos'] else []
        photo_links = ' '.join(f'<a href="recovered_photos/{html.escape(p)}">Photo</a>' for p in photos)
        if o['cisi'] in reviews:
            photo_links += '<p class="note">' + html.escape(reviews[o['cisi']]) + '</p>'
        cells = [f'<b>{o["cisi"]}</b>', label(o['container']), label(o['context']),
                 str(o['published_impressions']), html.escape(o['sign_sequences']) or 'No transcription joined',
                 html.escape(o['proposed_translations']) or 'No proposed reading joined',
                 html.escape(o['published_die_groups']) or 'No repeated die assigned in table1',
                 html.escape(flags), photo_links]
        rows.append('<tr data-ref="'+o['cisi']+'" data-category="'+o['container']+'" data-context="'+o['context']+'" data-joined="'+str(o['corpus_joined']).lower()+'" data-new="'+str(o['newly_supplied_backing_label']).lower()+'">'+''.join('<td>'+c+'</td>' for c in cells)+'</tr>')
    options = ''.join(f'<option value="{c}">{label(c)}</option>' for c in CATEGORIES)
    source_table = table(dies, [('published_die_group','Published die'),('source_sealings','Sealings'),('diagnostic_use_categories','Specific support categories'),('prior_evidence_in_group','Already represented in old backing evidence')])
    prediction_table = table(predictions, [('sign','Sign'),('proposed_meaning','Fixed proposed meaning'),('sign_bearing_joined_objects','Joined objects carrying sign'),('reason','Result')])
    corrections_table = table(corrections, [('cisi','Object'),('old_inference','Earlier subtype inference'),('source_category','Published physical category')])
    page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Full Lothal physical-context expansion</title>
<style>body{font:17px/1.55 system-ui,sans-serif;color:#253647;background:#faf8f2;max-width:1240px;margin:42px auto;padding:0 24px}h1{font-size:38px;line-height:1.15}h2{margin-top:42px}a{color:#0d687c}.callout{background:#e4efeb;padding:20px;border-left:5px solid #287e78}.stats{display:flex;gap:12px;flex-wrap:wrap;margin:25px 0}.stats div{background:white;border:1px solid #d6ded9;padding:16px;flex:1;min-width:125px}.stats b{display:block;font-size:30px;color:#226f68}.scroll{overflow-x:auto}table{border-collapse:collapse;width:100%;background:white;font-size:14px}th,td{border:1px solid #d5dcd6;padding:10px;text-align:left;vertical-align:top}th{background:#edf0e9}.wide{min-width:1600px}.note{font-size:13px;color:#5b6872}.controls{display:flex;gap:10px;flex-wrap:wrap;margin:20px 0}select,input{font:inherit;padding:9px;border:1px solid #a9b9b3;border-radius:4px;max-width:100%;box-sizing:border-box}input{min-width:220px;flex:1}img.chart{display:block;width:100%;height:auto}#count{font-weight:600}button{font:inherit;padding:9px;background:white;border:1px solid #9aaea4;cursor:pointer}@media(max-width:600px){body{padding:0 16px}h1{font-size:29px}.stats div{min-width:110px}.controls>*{width:100%}}[hidden]{display:none!important}</style>
<h1>93 Lothal sealings: physical use joined to inscriptions</h1><p>23 November 2026 · full extraction of Frenez2020 tables1–2</p>
<div class="callout"><b>The expansion adds 44 new backing/use labels to already encoded objects;34 identify a specific support category.</b> The other10 are “Other types” or undiagnostic. It also adds25 archaeological records with missing transcriptions. These are additional physical data, not93 newly deciphered inscriptions.</div>
<div class="stats"><div><b>93</b>source sealings</div><div><b>133</b>recorded impressions</div><div><b>68</b>objects with existing texts</div><div><b>44</b>new use labels joined to texts</div><div><b>25</b>missing transcriptions</div></div>
<h2>What the physical categories say</h2><p>These identify what the clay was attached to: a jar, a box, a bag, a locker, a structure or another support. They do not identify the stored commodity. Question marks in the source mean <b>unknown find context</b>, not an uncertain support classification. All93 category/context cells were checked against the source images.</p><img class="chart" src="category_coverage.svg" alt="Container categories split by whether a transcription is available">
<h2>Three earlier subtype assumptions need correction</h2>''' + corrections_table + '''<p>The original subtype codes are preserved. The source categories replace those generic assumptions for this comparison; this is not a silent edit of Cúper's corpus. Other old labels are corroborated or remain undiagnostic.</p>
<h2>The same physical seal can occur on different supports</h2><p>The full source matrix contains seven published repeated-die groups,56 memberships across43 sealings. Six groups span more than one specific support category. These identifications and the general cross-container observation were already published by Parpola/Frenez. Our addition is the full machine-readable join. Multiple impressions mean one sealing can belong to several groups; memberships cannot be counted as independent trials. The source matrix identifies the object carrying a die impression. It does not assign each encoded face to that die; the face export preserves that distinction.</p><img class="chart" src="published_die_uses.svg" alt="Published die groups across physical support categories">''' + source_table + '''
<p>For example, the source's <b>Unicorn1</b> seal occurs on wooden boxes, a leather sack, pottery jars, architectural pegs and structures. That weakens a claim that this seal exclusively labels one container type. It does not distinguish an issuer from a commodity that could be stored in different containers. The elephant group is confined to wooden boxes in this table.</p>
<h2>The proposed 440 and690 tests have no exposed sample</h2>''' + prediction_table + '''<p>Neither sign occurs in the68 objects with joined texts. The other25 remain unknown; no zero is imputed to them. Thus neither fixed prediction was tested, and no p-value is reported. The source key labels are goblet/corner for440 and bundle/store for690, which are wider than the earlier vessel/storehouse examples. No other word was substituted after inspecting the outcomes.</p>
<h2>How much of this could become additional validation?</h2><p>Of93 source objects,24 already have specific subtype/backing evidence or were inspected in the previous follow-up. The remaining69 acquire a label here;44 have existing texts. After excluding known repeated dies and exact complete texts connected to prior evidence,30 text-bearing rows remain provisionally unlinked. They are <b>not30 proven independent test cases</b>: damaged text and unknown dies can hide further copies. Support categories also include undiagnostic records. The full table preserves these distinctions.</p>
<h2>All93 source objects</h2><p>Existing proposed readings are quoted from the repository, not endorsed translations. Older volume estimates in those readings are preserved as historical source text. “Missing transcription” is separate from an unknown sign inside an encoded text.</p>
<div class="controls"><input id="search" aria-label="Search references, signs or proposed meanings" placeholder="Search L-142, a sign, or a proposed meaning"><select id="category" aria-label="Support category"><option value="">All support categories</option>''' + options + '''</select><select id="coverage" aria-label="Transcription coverage"><option value="">All transcription states</option><option value="true">Existing transcription</option><option value="false">Missing transcription</option></select><select id="novelty" aria-label="Label novelty"><option value="">All label histories</option><option value="true">Newly supplied label</option><option value="false">Prior backing evidence</option></select><button id="reset">Reset filters</button></div><p id="count"></p><div class="scroll"><table class="wide" id="objects"><thead><tr><th>Object</th><th>Physical support</th><th>Find context</th><th>Impressions</th><th>Existing sign sequences</th><th>Existing proposed reading</th><th>Published repeated die</th><th>Prior evidence</th><th>Recovered photo / review</th></tr></thead><tbody>''' + ''.join(rows) + '''</tbody></table></div>
<h2>Files and source</h2><p><a href="all_93_sealings.csv">Full93-object dataset</a> · <a href="all_existing_face_readings.csv">All86 existing face readings and recorded findspots</a> · <a href="repeated_seal_matrix.csv">Complete source matrix</a> · <a href="repeated_die_memberships.csv">Die memberships</a> · <a href="missing_object_photo_review.csv">Missing-object photo review</a> · <a href="recovered_photo_sources.csv">Photo provenance</a> · <a href="source_cell_checks.csv">Source-cell verification</a> · <a href="fixed_prediction_eligibility.csv">Fixed predictions</a> · <a href="protocol.md">Protocol and prior-work distinctions</a></p><p>Primary source: <a href="''' + SOURCE + '''">Frenez2020, table1 p29 and table2 pp31–32</a>. The seven groups are author identifications rather than physical die matches newly verified here. All container/use labels derive from that source. Contents remain unidentified. Colab units:0.</p>
<script>const rows=[...document.querySelectorAll('#objects tbody tr')];const search=document.querySelector('#search'),category=document.querySelector('#category'),coverage=document.querySelector('#coverage'),novelty=document.querySelector('#novelty');function apply(){let n=0;for(const r of rows){const keep=(!search.value||r.textContent.toLowerCase().includes(search.value.toLowerCase()))&&(!category.value||r.dataset.category===category.value)&&(!coverage.value||r.dataset.joined===coverage.value)&&(!novelty.value||r.dataset.new===novelty.value);r.hidden=!keep;n+=keep;}document.querySelector('#count').textContent=n+' of93 objects shown';}for(const e of[search,category,coverage,novelty])e.addEventListener('input',apply);document.querySelector('#reset').addEventListener('click',()=>{for(const e of[search,category,coverage,novelty])e.value='';apply();});apply();</script></html>'''
    for old, new in {'Frenez2020':'Frenez 2020', 'tables1–2':'tables 1–2',
                     'objects;34':'objects; 34', 'other10':'other 10', 'adds25':'adds 25', 'not93':'not 93',
                     'All93':'All 93', 'all93':'all 93', 'groups,56':'groups, 56', 'across43':'across 43',
                     'table1':'table 1', 'and690':'and 690', 'the68':'the 68', 'other25':'other 25',
                     'for440':'for 440', 'for690':'for 690', 'Of93':'Of 93', 'objects,24':'objects, 24',
                     'remaining69':'remaining 69', 'here;44':'here; 44', 'evidence,30':'evidence, 30',
                     'not30':'not 30', 'All86':'All 86', 'Full93':'Full 93', 'table2':'table 2',
                     'p29':'p 29', 'pp31–32':'pp 31–32', 'units:0':'units: 0',
                     "n+' of93":"n+' of 93"}.items():
        page = page.replace(old, new)
    (OUT / 'lothal.html').write_text(page)
    (BASE / 'LOTHAL_RESULTS.md').write_text(f'''# Full Lothal source expansion

The [interactive report](results/lothal_tables/lothal.html) joins all93 source sealings and133 recorded impressions to the existing corpus. There are68 objects with86 existing encoded faces;25 have no exact transcription join. Forty-four existing objects acquire a previously unrecorded physical-use label. Of the69 newly supplied labels across all objects, some are undiagnostic or lack transcriptions; they are not69 new tests.

The repeated-seal matrix is fully extracted: seven published groups,56 memberships across43 objects. Six groups span several diagnostic support types. This reproduces a published physical observation with a complete source join; it is not a newly discovered same-die match or issuer-versus-contents experiment.

Three generic subtype inferences differ from the source categories: L-125 soft-bale inference → wooden box; L-138 soft-bale inference → structure; L-142 token/no-packing inference → wooden box. Original catalogue fields are retained. All93 category/context markers agree with image-cell measurements. In the source, question marks mean unknown discovery context, not uncertain container classification.

The two fixed target signs440/690 are absent from joined inscriptions. The missing25 are unknown, not negative examples. Neither prediction was scored. Thirty newly labelled text-bearing rows remain provisionally unlinked after known repeated-die and exact complete-text exclusions; this is not a guarantee of independent designs. Future near-variant and damaged-copy review is required before any new predictive validation.

Photos were recovered for20 of the25 missing objects. Their review and original files are released, including L-178 as a candidate for dedicated epigraphic transcription. No new sign encoding was guessed; white/dark modern collection annotations were not mistaken for ancient signs. Table2 records five impressions for L-215, while its recovered photo filename mentions1–4; the discrepancy remains visible.

Source: [Frenez2020](https://doi.org/10.5281/zenodo.5513821), table1 p29 and table2 pp31–32. [Protocol](LOTHAL_EXPANSION.md). Run `python3 research/independent_validation_20261120/context_associations/lothal_tables.py` with numpy/Pillow. No statistical fit or hypothesis test ran; Colab units:0.
''')
