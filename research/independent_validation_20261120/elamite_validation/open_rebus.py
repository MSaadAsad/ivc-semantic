"""Discover picture -> Elamite word -> unrestricted alternative lexical senses.

No existing reading, Dravidian form or target semantic class selects candidates.
"""
import argparse
import ast
import collections
import csv
import hashlib
import json
from pathlib import Path
import re
import time
import unicodedata

import run as R

BASE=Path(__file__).resolve().parent;REPO=BASE.parents[2];OUT=BASE/'results'
VOCAB={'N','V','ADJ','Other','Uncalss'}
PICTURE_ALIASES={
    'jar':{'jar','jug','pot','pitcher','waterpot'},
    'cup':{'cup','bowl','goblet'},'door':{'door','gate'},'gate':{'door','gate'},
    'teeth':{'teeth','tooth'},'staff':{'staff','stave','stick','rod','sceptre','scepter'},
    'box':{'box','chest','coffer','casket','trunk'},
}


def write(name,rows,fields=None):
    with (OUT/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields or list(rows[0]),lineterminator='\n')
        w.writeheader();w.writerows(rows)


def fold(s):
    s=unicodedata.normalize('NFD',s.lower())
    return ''.join(c for c in s if not unicodedata.combining(c)).replace('ß','ss')


def permissive(s):
    s=R.norm(s).translate(str.maketrans({'b':'p','d':'t','g':'k'}))
    return re.sub(r'(.)\1+',r'\1',s)


def onset(s):
    cons=re.sub('[aeiou]','',s)
    return (s[:1] in 'aeiou',cons[:1])


def nominal_stem(word,raw):
    key=R.norm(word)
    if re.search(r'-SG$',raw) and key.endswith('r') and len(key)>2:
        return key[:-1],'source SG analysis; final nominal -r removed'
    if re.search(r'-PL$',raw) and key.endswith('p') and len(key)>2:
        return key[:-1],'source PL analysis; final nominal -p removed'
    return key,''


def source_constants():
    tree=ast.parse((REPO/'work_scripts/lang_m2_common.py').read_text())
    result={}
    for node in tree.body:
        if isinstance(node,ast.Assign):
            for t in node.targets:
                if isinstance(t,ast.Name) and t.id in {'PIC_EN_SYN','DE'}:
                    result[t.id]=ast.literal_eval(node.value)
    assert set(result)=={'PIC_EN_SYN','DE'}
    return result


def german_senses(raw):
    text=fold(raw)
    text=re.sub(r'\([^()]*\)',' ',text)
    text=re.sub(r'\b(?:vgl|siehe|s\.v\.|konig\s*\().*','',text)
    result=[]
    for part in re.split('[;,]',text):
        part=re.sub(r'^(?:(?:ae|ne|me|ache|der|die|das|ein|eine|sein|seine|ihr|ihre|wohl|vielleicht|wahrscheinlich|anscheinend)\s+)+','',part.strip())
        # Keep the lexical head, not the objects of a prepositional explanation.
        part=re.split(r'\s+(?:mit|aus|von|fur|im|auf|bei|laut)\b',part)[0]
        part=part.strip(' .:?!')
        if len(part)>1 and part not in {'s','vgl','ne','ae','me','ache'}:
            result.append(part)
    return tuple(sorted(set(result)))


def target_flags(raw,word,language,heads,english_words):
    flags=[]
    if '?' in raw:flags.append('uncertain_gloss')
    if re.search(r'\b(?:unknown|unclear|unbekannt|unlesbar|irrtum|bedeutungslos)\b',raw,re.I):flags.append('meaning_unknown_or_error')
    if language=='en':
        tokens=[fold(w) for h in heads for w in re.findall(r'[^\W\d_]+',h)]
        if not tokens or not all(t in english_words for t in tokens):flags.append('English_head_requires_translation_review')
        if any(permissive(h)==permissive(word) for h in heads):flags.append('possible_untranslated_self_gloss')
        if re.search(r'\b(?:PN|GN|DN|name|Elamite|Susa|Anshan)\b',raw):flags.append('name_or_label_risk')
    else:
        flags.append('German_OCR_gloss_requires_review')
        if re.search(r'\b(?:endung|suffix|lesung|schreibung|statt|irrtum|vgl|siehe|wohl|vielleicht)\b',fold(raw)):
            flags.append('grammatical_or_editorial_context')
    return flags


def load_entries(source_dir,wordlist=Path('/usr/share/dict/words')):
    meta=json.loads((BASE/'inputs/source_files.json').read_text())
    english_words={fold(w.strip()) for w in wordlist.read_text().splitlines()} if wordlist.exists() else set()
    entries=[];audit=[];counts=[]
    def add(identifier,source,word,raw,language,category,period='',cognate='',variant=''):
        original_word=word
        removed=[]
        while '.' in word and word.split('.',1)[0] in {'v','h','hh','hhh','d'}:
            prefix,word=word.split('.',1);removed.append(prefix)
        reason=('empty_gloss' if not raw.strip() else 'damaged_form' if re.search(r'[?\[\]<>]',word) else
                'determinative_or_compound_dot' if '.' in word else 'capital_logogram' if any(c.isupper() for c in word) else
                'unexplained_form_punctuation' if any(not(c.isalpha() or c.isdigit() or c=='-') for c in word) else
                'short_form' if len(R.norm(word))<2 else 'eligible')
        heads=R.senses(raw) if language=='en' else german_senses(raw)
        if reason=='eligible' and not heads:reason='no_lexical_head'
        audit.append(dict(id=identifier,source=source,reason=reason))
        if reason!='eligible':return
        for head in heads:
            flags=target_flags(raw,word,language,(head,),english_words)
            if removed:flags.append('putative_determinative_prefix_removed:'+','.join(removed))
            stem,basis=nominal_stem(word,raw) if language=='en' else (R.norm(word),'')
            entries.append(dict(id=identifier,source=source,word=word,raw_gloss=raw,heads=(head,),language=language,
                                category=category,period=period,cognate=cognate,variant=variant,strict=R.norm(word),
                                permissive=permissive(word),flags=flags,original_word=original_word,
                                stem=stem,stem_basis=basis))
    for spec in meta['files']:
        name=Path(spec['path']).name;category=name.split('-')[0]
        if category not in VOCAB:continue
        path=source_dir/name;blob=path.read_bytes()
        assert hashlib.sha1(f'blob {len(blob)}\0'.encode()+blob).hexdigest()==spec['blob_sha']
        rows=R.read(path);counts.append(dict(source='DigitalPasts',file=name,rows=len(rows)))
        for n,r in enumerate(rows,2):
            add(f'{category}:{n}','DigitalPasts',r['transliteration'],r['morphology'],'en',category,
                r['period'],r['cognate'],r['variant'])
    path=REPO/'work_data/lang_m/lex/elamite_hinzkoch.tsv'
    old_rows=list(csv.reader(path.open(),delimiter='\t'))
    counts.append(dict(source='HinzKoch_existing',file=str(path.relative_to(REPO)),rows=len(old_rows)))
    for r in old_rows:
        if len(r)>=5:add('HK:'+r[0],'HinzKoch_existing',r[1],r[4],'de','unknown')
    # Duplicate source records are retained as witnesses, not independent roots.
    write('open_rebus_source_inventory.csv',counts)
    write('open_rebus_source_exclusions.csv',audit)
    return entries,counts,dict(english_wordlist_sha256=hashlib.sha256(wordlist.read_bytes()).hexdigest() if wordlist.exists() else None,
                               english_wordlist_role='Review flag only; no candidate is excluded for a failed spelling check.')


def picture_match(entry,noun,constants):
    terms={noun}|PICTURE_ALIASES.get(noun,set())
    for group in constants['PIC_EN_SYN'].values():
        if noun in group.split():terms.update(group.split())
    if entry['language']=='de':
        terms={t for n in terms for t in constants['DE'].get(n,'').split()}
    terms={fold(t) for t in terms}
    return bool(terms & {fold(h) for h in entry['heads']})


def build_neighbors(entries):
    strict=collections.defaultdict(set);soft=collections.defaultdict(set);deleted=collections.defaultdict(set)
    for i,e in enumerate(entries):
        strict[e['strict']].add(i);soft[e['permissive']].add(i)
        s=e['permissive']
        if len(s)>=4:
            for j in range(len(s)):deleted[s[:j]+s[j+1:]].add(s)
    neighbors={}
    for q in soft:
        if len(q)<4 or len(re.sub('[aeiou]','',q))<2:
            neighbors[q]=set();continue
        words=set(deleted.get(q,set()))
        for j in range(len(q)):
            short=q[:j]+q[j+1:]
            if short in soft:words.add(short)
            words.update(deleted.get(short,set()))
        words={x for x in words if len(x)>=4 and len(re.sub('[aeiou]','',x))>=2 and onset(x)==onset(q) and R.distance(q,x)==1}
        neighbors[q]={i for word in words for i in soft[word]}
    stems=collections.defaultdict(set)
    for i,e in enumerate(entries):stems[e['stem']].add(i)
    return strict,soft,neighbors,stems


def search_targets(picture,entries,index):
    strict,soft,near,stems=index
    for channel,indices in [('equal_conservative_form',strict[picture['strict']]),
                            ('equal_permissive_key',soft[picture['permissive']]),
                            ('equal_nominal_class_stem',stems[picture['stem']]),
                            ('one_edit_whole_form',near[picture['permissive']])]:
        for b in sorted(indices):
            target=entries[b]
            if channel=='equal_permissive_key' and picture['strict']==target['strict']:continue
            if channel=='one_edit_whole_form' and picture['permissive']==target['permissive']:continue
            if channel=='equal_nominal_class_stem' and (not(picture['stem_basis'] or target['stem_basis']) or picture['permissive']==target['permissive']):continue
            yield channel,target


def main(source_dir,wordlist=Path('/usr/share/dict/words')):
    started=time.monotonic();OUT.mkdir(exist_ok=True)
    constants=source_constants();entries,source_counts,meta=load_entries(source_dir,wordlist)
    pictures=R.read(REPO/'work_data/pictures/pictures_blind.csv')
    assert len(pictures)==417
    noun_pictures=collections.defaultdict(list)
    for p in pictures:
        if p['level'] not in {'3of3','2of3'}:continue
        for noun in p['agreed_things'].split(';'):
            if noun:noun_pictures[noun].append(p)
    crosswalk=collections.defaultdict(set)
    for r in R.read(REPO/'work_data/lipi_mahadevan_crosswalk.csv'):
        if r['rank_for_lipi_sign']=='1':crosswalk[r['mahadevan']].add(r['lipi'])
    old=set()
    for r in R.read(REPO/'work_data/lang_m2/evidence.csv'):
        if r['dict']=='elamite_hinzkoch':old.add((r['noun'],permissive(r['picture_word']),permissive(r['soundalike'])))
    anchors={n:[i for i,e in enumerate(entries) if picture_match(e,n,constants)] for n in noun_pictures}
    index=build_neighbors(entries);strict,soft,near,stems=index
    fields=['candidate_id','picture_noun','channel','mahadevan_glyphs','lipi_signs','picture_levels','picture_word','picture_heads',
            'target_word','target_heads','picture_source','target_source','picture_source_id','target_source_id','picture_raw_gloss','target_raw_gloss',
            'picture_period','target_period','picture_cognate_flag','target_cognate_flag','picture_flags','target_flags','same_source_entry',
            'old_candidate_word_pair','short_form','classification','picture_original_word','target_original_word',
            'picture_stem_key','target_stem_key','picture_stem_basis','target_stem_basis']
    candidates=[];coverage=[]
    for noun,pp in sorted(noun_pictures.items()):
        start=len(candidates);glyphs=sorted({p['glyph'] for p in pp},key=int)
        signs=sorted({s for g in glyphs for s in crosswalk[g]})
        for a in anchors[noun]:
            picture=entries[a]
            for channel,target in search_targets(picture,entries,index):
                if picture_match(target,noun,constants):continue
                if set(picture['heads'])==set(target['heads']) and picture['language']==target['language']:continue
                same=picture['source']==target['source'] and picture['id']==target['id']
                flags=set(picture['flags'])|set(target['flags'])
                classification=('uninterpreted_or_error_gloss' if flags & {'possible_untranslated_self_gloss','meaning_unknown_or_error'} else
                                'needs_English_translation_review' if target['language']=='en' and 'English_head_requires_translation_review' in target['flags'] else
                                'German_source_review' if target['language']=='de' else 'English_gloss_candidate')
                literal_aliases={noun}|PICTURE_ALIASES.get(noun,set())
                if target['language']=='en' and any(h.startswith(t+'-') or h.startswith(t+'.') for h in target['heads'] for t in literal_aliases):
                    classification='same_picture_lexeme_grammar'
                if re.search(r'\(\s*=\s*dynasty\s*\)',picture['raw_gloss'],re.I):
                    classification='nonliteral_picture_sense_requires_review'
                identifier='ER'+str(len(candidates)+1).zfill(5)
                candidates.append(dict(zip(fields,[identifier,noun,channel,';'.join(glyphs),';'.join(signs),';'.join(sorted({p['level'] for p in pp})),
                    picture['word'],'; '.join(picture['heads']),target['word'],'; '.join(target['heads']),picture['source'],target['source'],
                    picture['id'],target['id'],picture['raw_gloss'],target['raw_gloss'],picture['period'],target['period'],picture['cognate'],target['cognate'],
                    ';'.join(picture['flags']),';'.join(target['flags']),same,(noun,picture['permissive'],target['permissive']) in old,
                    len(picture['permissive'])<4 or len(target['permissive'])<4,classification,picture['original_word'],target['original_word'],
                    picture['stem'],target['stem'],picture['stem_basis'],target['stem_basis']])))
        rr=candidates[start:]
        coverage.append(dict(picture_noun=noun,mahadevan_drawings=len(glyphs),lipi_signs=';'.join(signs),
                             lexical_picture_rows=len(anchors[noun]),conservative_pairs=sum(r['channel']=='equal_conservative_form' for r in rr),
                             permissive_pairs=sum(r['channel']=='equal_permissive_key' for r in rr),
                             nominal_stem_pairs=sum(r['channel']=='equal_nominal_class_stem' for r in rr),one_edit_pairs=sum(r['channel']=='one_edit_whole_form' for r in rr)))
    write('open_rebus_all_candidates.csv',candidates,fields)
    write('open_rebus_picture_coverage.csv',coverage)
    # Include every drawing, even those without identifiable pictured nouns.
    picture_inventory=[dict(mahadevan_glyph=p['glyph'],picture_level=p['level'],picture_nouns=p['agreed_things'],
                            lipi_signs=';'.join(sorted(crosswalk[p['glyph']])),
                            any_lexical_coverage=any(anchors.get(n) for n in p['agreed_things'].split(';'))) for p in pictures]
    write('open_rebus_all_417_pictures.csv',picture_inventory)
    # Unrestricted lexical collision rates expose how easily chance alternatives occur.
    collision=[]
    for mode,index in [('conservative',strict),('permissive',soft)]:
        covered=0
        for i,e in enumerate(entries):
            group=index[e['strict' if mode=='conservative' else 'permissive']]
            if any(entries[j]['language']==e['language'] and set(entries[j]['heads'])!=set(e['heads']) for j in group):covered+=1
        collision.append(dict(mode=mode,dictionary_records=len(entries),records_with_different_head_same_key=covered,
                              fraction=covered/len(entries),interpretation='Lexical collision diagnostic, not evidence for an Indus language.'))
    write('open_rebus_dictionary_collisions.csv',collision)
    provenance=['work_scripts/lang_m2_common.py','work_data/lang_m/lex/elamite_hinzkoch.tsv',
                'work_data/pictures/pictures_blind.csv','work_data/lipi_mahadevan_crosswalk.csv','work_data/lang_m2/evidence.csv',
                'research/independent_validation_20261120/proto_reconstruction/results/all_existing_pair_recipes.csv']
    write('open_rebus_input_hashes.csv',[dict(path=p,sha256=hashlib.sha256((REPO/p).read_bytes()).hexdigest(),
                                            bytes=(REPO/p).stat().st_size) for p in provenance])
    terms={n:sorted({n}|PICTURE_ALIASES.get(n,set())|{t for v in constants['PIC_EN_SYN'].values() if n in v.split() for t in v.split()}) for n in noun_pictures}
    (OUT/'open_rebus_picture_terms.json').write_text(json.dumps({n:dict(English=v,German=sorted({t for x in v for t in constants['DE'].get(x,'').split()})) for n,v in terms.items()},indent=2)+'\n')
    summary=dict(picture_drawings=417,pictured_drawings=sum(p['level'] in {'3of3','2of3'} for p in pictures),
                 picture_noun_types=len(noun_pictures),covered_picture_nouns=sum(bool(v) for v in anchors.values()),
                 source_counts=source_counts,eligible_lexical_records=len(entries),
                 eligible_source_rows=len({(e['source'],e['id']) for e in entries}),
                 eligible_conservative_forms=len(strict),eligible_records_unit='sense records; not independent roots',
                 candidates=len(candidates),candidate_channels=dict(collections.Counter(c['channel'] for c in candidates)),
                 candidate_classification=dict(collections.Counter(c['classification'] for c in candidates)),
                 old_candidate_pairs_flagged=sum(c['old_candidate_word_pair'] for c in candidates),
                 destination_meanings_restricted=False,uses_dravidian_forms=False,uses_Cuper_target_meanings_to_select=False,
                 source_review='Word forms and glosses are candidates; no new translation assigned.',
                 **meta,runtime_seconds=round(time.monotonic()-started,2),colab_units=0)
    (OUT/'open_rebus_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--source-dir',type=Path,default=REPO.parent/'elamite-sources')
    ap.add_argument('--english-wordlist',type=Path,default=Path('/usr/share/dict/words'))
    args=ap.parse_args();main(args.source_dir,args.english_wordlist)
