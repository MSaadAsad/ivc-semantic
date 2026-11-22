"""Readable inventory of every existing pair and all current sign values."""
import csv, html, json
from pathlib import Path
BASE=Path(__file__).resolve().parent; OUT=BASE/'results'
def rows(name):
    with (OUT/name).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))
def esc(s):return str(s).replace('|','/').replace('\n',' ')
pairs=rows('pair_summary.csv'); signs=rows('all_163_sign_results.csv')
lines=['# Every tested existing word-pair recipe','',
       'All 178 recorded recipes across 93 candidate sign IDs. Panels overlap. The automatic panel tests artifact-context domains rather than established word meanings. These are lexical screen outcomes, not translated inscriptions.','',
       '| Panel | Sign | Proposed connection | Equal older-source Proto-Dravidian form after specified exclusions? | Equal subgroup forms recorded | Table outcome |',
       '|---|---|---|---|---|---|']
for r in pairs:
    lines.append('| '+' | '.join(esc(x) for x in [r['panel'],r['sign'],r['title'],r['qualified_published_PD_equal'],r['equal_subgroups'],r['assessment']])+ ' |')
lines+=['','## Every current sign value','',
        'Every one of the 163 current proposed sign values is retained, including compounds, variants, numbers and values without a scorable two-sided pun. Component links are vocabulary links, not proof of a compound reading.','',
        '| Sign | English meaning | Proposed root | Explicit components | Components with a lexical link / components searched | Assessment |',
        '|---|---|---|---|---|---|']
for r in signs:
    lines.append('| '+' | '.join(esc(x) for x in [r['sign'],r['proposed_meaning'],r['proposed_root'],r['explicit_components'],r['components_with_lexical_links']+'/'+r['explicit_components_count'],r['assessment']])+' |')
(OUT/'ALL_PAIRS_AND_SIGNS.md').write_text('\n'.join(lines)+'\n')
parts=['<!doctype html><meta charset="utf-8"><title>Reconstructed word pairs</title><style>body{font:16px Arial,sans-serif;margin:32px;color:#1b2e40;background:#f6f8fa}p{max-width:1050px;line-height:1.5}table{border-collapse:collapse;background:white;width:100%;font-size:14px}th,td{padding:12px;border-bottom:1px solid #dde3e9;vertical-align:top;text-align:left}th{background:#243d53;color:white}details{margin:12px 0;background:white;padding:14px;max-width:1250px}summary{cursor:pointer;font-weight:bold}input{padding:12px;font:inherit;width:450px}.entry{line-height:1.5}</style>',
       '<h1>Reconstructed vocabulary and proposed Indus readings</h1>',
       '<p>All 178 existing pair recipes were searched against the full 15,629-record table. Different sources and ancestral levels remain separate. Exact reconstruction equality supports a lexical possibility; it does not establish a sign meaning or date the word to the Indus period. Missing coverage and unequal forms remain unresolved.</p>',
       '<input id="q" placeholder="Search a meaning, root or sign"><p id="count"></p>']
for r in pairs:
    note='Same recorded older-source Proto-Dravidian form survives the specified exclusions.' if r['qualified_published_PD_equal']=='True' else r['assessment']
    if r['published_PD_equal']=='True' and r['qualified_published_PD_equal']=='False':note='Apparent equality excluded: relevant human sense or fully specified pronunciation is missing.'
    parts.append('<details class="entry"><summary>'+html.escape(f"{r['title']} — sign {r['sign']} ({r['panel']})")+'</summary><p>'+html.escape(note)+'</p><p>'+html.escape(r['PD_evidence'])+'</p><p>Equal forms recorded at subgroup levels: '+html.escape(r['equal_subgroups'] or 'None in this screen')+'</p></details>')
parts.append('''<script>const entries=[...document.querySelectorAll('.entry')];const q=document.getElementById('q');function draw(){let n=0;for(const e of entries){e.hidden=!e.textContent.toLowerCase().includes(q.value.toLowerCase());if(!e.hidden)n++}document.getElementById('count').textContent=n+' of 178 existing recipes'}q.oninput=draw;draw();</script>''')
(OUT/'word_pairs.html').write_text('\n'.join(parts))
print('Readable inventory: 178 recipes and 163 sign values; searchable evidence for every pair.')
