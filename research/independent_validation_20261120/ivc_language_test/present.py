"""Corrected subgroup displays with every proposed meaning written in English."""
import argparse
import collections
import csv
import hashlib
import itertools
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, PathPatch
from matplotlib.font_manager import FontProperties
from matplotlib.textpath import TextPath
from matplotlib.transforms import Affine2D
from analyze import BASE, LANGS

BG='#f7f5ef';INK='#142e39';MUTED='#586a70'
NONE='#d8dedb';FIRST='#90bbdb';SECOND='#bba6d4';BOTH='#e3b55f';SAME='#247d69'
HEADERS=['#6296c5','#d39c46','#9a84b2','#54a18d','#497f83']

def writecsv(name,rows):
    with (BASE/'results'/name).open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)

def draw_glyph(ax,sign,x,y,fp,cmap,width=.55,height=.72):
    """Fit each original outline inside its row, preserving its physical aspect ratio."""
    cp=0xe000+int(sign)
    if cp not in cmap:return
    path=TextPath((0,0),chr(cp),size=1,prop=fp)
    box=path.get_extents()
    if box.width<=0 or box.height<=0:return
    pixels_x=ax.get_window_extent().width/abs(ax.get_xlim()[1]-ax.get_xlim()[0])
    pixels_y=ax.get_window_extent().height/abs(ax.get_ylim()[1]-ax.get_ylim()[0])
    scale=min(width*pixels_x/box.width,height*pixels_y/box.height)
    transform=(Affine2D().translate(-box.x0-box.width/2,-box.y0-box.height/2)
               .scale(scale/pixels_x,-scale/pixels_y).translate(x,y))
    ax.add_patch(PathPatch(path.transformed(transform),facecolor=INK,edgecolor='none'))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--font',type=Path,required=True);a=ap.parse_args()
    fp=FontProperties(fname=a.font)
    from fontTools.ttLib import TTFont
    cmap=TTFont(a.font).getBestCmap()
    plt.rcParams.update({'font.family':'DejaVu Sans','text.color':INK,'font.size':11,'svg.fonttype':'path'})
    classification=json.loads((BASE/'classification.json').read_text());groups=classification['groups']
    displayed=[l for g in groups for l in g['languages']]
    assert len(displayed)==len(set(displayed))==22 and set(displayed)==set(LANGS)
    claims=json.loads((BASE/'claims.json').read_text())['claims']
    pairs=[c for c in claims if c['kind'] in ('bridge','polysemy')]
    matrix=list(csv.DictReader((BASE/'results/language_by_claim.csv').open()))
    idx={(r['claim'],r['language']):r for r in matrix}
    out=BASE/'figures';out.mkdir(exist_ok=True)
    by_group={};group_rows=[];summary=[];regions=[]
    for g in groups:
        for c in claims:
            rr=[idx[c['id'],l] for l in g['languages']]
            rec=dict(claim=c['id'],sign=c['sign'],title=c['title'],group=g['id'],label=g['label'])
            for field in ['target_meaning','both_meanings','strict_complete','one_edit_complete']:
                ls=[r['language'] for r in rr if r[field]=='True']
                rec[field]=bool(ls);rec[field+'_languages']='; '.join(ls)
            by_group[c['id'],g['id']]=rec;group_rows.append(rec)
        summary.append(dict(group=g['id'],label=g['label'],languages='; '.join(g['languages']),n_languages=len(g['languages']),
            target_meanings_67=sum(by_group[c['id'],g['id']]['target_meaning'] for c in claims),
            both_meanings_48=sum(by_group[c['id'],g['id']]['both_meanings'] for c in pairs),
            same_form_48=sum(by_group[c['id'],g['id']]['strict_complete'] for c in pairs),
            one_edit_48=sum(by_group[c['id'],g['id']]['one_edit_complete'] for c in pairs)))
    for field,eligible in [('target_meaning',claims),('both_meanings',pairs),('strict_complete',pairs)]:
        bins=collections.defaultdict(list)
        for c in eligible:
            key=''.join('1' if by_group[c['id'],g['id']][field] else '0' for g in groups)
            bins[key].append(c)
        for bits in itertools.product('01',repeat=len(groups)):
            key=''.join(bits);cc=bins[key]
            regions.append(dict(measure=field,region=key,count=len(cc),
                groups='; '.join(g['label'] for bit,g in zip(bits,groups) if bit=='1'),
                claims='; '.join(c['id'] for c in cc),semantics='; '.join(c['title'] for c in cc)))
    writecsv('branch_by_claim.csv',group_rows);writecsv('branch_summary.csv',summary)
    writecsv('branch_overlap_regions.csv',regions)
    old=[]
    for label,ls in [('Tamil / Malayalam',['Tamil','Malayalam']),('Kannada / Telugu',['Kannada','Telugu']),
                     ('Brahui / Kurukh / Malto',['Brahui','Kurukh','Malto'])]:
        old.append(dict(superseded_display_group=label,
            both_meanings_48=sum(any(idx[c['id'],l]['both_meanings']=='True' for l in ls) for c in pairs),
            same_form_48=sum(any(idx[c['id'],l]['strict_complete']=='True' for l in ls) for c in pairs),
            status='Historical display grouping withdrawn; these counts were semantic attestations, not ancestral reconstructions.'))
    writecsv('superseded_group_audit.csv',old)
    semantics=[]
    for c in claims:
        rec=dict(sign=c['sign'],kind=c['kind'],proposed_picture_or_first_meaning=' / '.join(c['a']),
            proposed_intended_meaning=' / '.join(c['b']) if c['kind'] in ('bridge','polysemy') else 'Single-meaning/numeral claim; no second meaning tested',
            proposal_root=c['proposal_root'],cited_first_entries='; '.join(c['a_entries']),
            cited_second_entries='; '.join(c['b_entries']),
            languages_with_first_meaning='; '.join(l for l in displayed if idx[c['id'],l]['meaning_a']=='True'),
            languages_with_intended_meaning='; '.join(l for l in displayed if idx[c['id'],l]['meaning_b']=='True'),
            languages_with_both_meanings='; '.join(l for l in displayed if idx[c['id'],l]['both_meanings']=='True'),
            languages_with_same_form='; '.join(l for l in displayed if idx[c['id'],l]['strict_complete']=='True'))
        semantics.append(rec)
    writecsv('semantics_catalogue.csv',semantics)
    # All 48 connections, with English semantics and defensible historical display sets.
    fig=plt.figure(figsize=(16,19),facecolor=BG)
    fig.text(.045,.963,'What do the proposed signs mean?',size=25,weight='bold')
    fig.text(.045,.938,'48 proposed picture → intended-meaning connections • all 22 studied varieties • corrected subgroup display',size=11.5,color=MUTED)
    fig.text(.045,.914,'Gold or green means both meanings are documented within ONE language. English labels are hypotheses, not translations.',size=10.5,color=MUTED)
    ax=fig.add_axes([.035,.205,.93,.675]);ax.set_xlim(0,21);ax.set_ylim(49,-2.7);ax.axis('off')
    xs=[11.4,13.4,15.4,17.4,19.4]
    ax.text(2,-2.1,'PICTURE / FIRST MEANING → PROPOSED INTENDED MEANING',size=10,weight='bold')
    for j,(g,x,s) in enumerate(zip(groups,xs,summary)):
        ax.text(x,-2.2,g['column_label'],ha='center',size=10.5,weight='bold',color=HEADERS[j])
        ax.text(x,-1.3,f"{s['both_meanings_48']}/48",ha='center',size=12,weight='bold')
        ax.text(x,-.6,'both meanings',ha='center',size=8,color=MUTED)
    for k,c in enumerate(pairs):
        if k%2==0:ax.add_patch(Rectangle((0,k-.44),20.8,.9,facecolor='#eeeee7',edgecolor='none'))
        draw_glyph(ax,c['sign'],.43,k,fp,cmap)
        ax.text(1.0,k,c['sign'],size=8.5,weight='bold',va='center')
        ax.text(2,k,c['title'],size=10,va='center')
        for g,x in zip(groups,xs):
            rec=by_group[c['id'],g['id']]
            co=SAME if rec['strict_complete'] else BOTH if rec['both_meanings'] else NONE
            ax.scatter([x],[k],s=45,color=co,linewidths=0)
    for x,co,label in [(.05,NONE,'Both meanings not established'),(.38,BOTH,'Both meanings; forms differ'),(.69,SAME,'Both meanings; same written form')]:
        fig.add_artist(Circle((x,.175),.005,transform=fig.transFigure,color=co));fig.text(x+.012,.171,label,size=10)
    fig.text(.045,.142,'South I: Tamil, Malayalam, Kannada, Tulu, Kota, Toda, Kodagu.  South II: Telugu, Gondi, Konda, Pengo, Manda, Kui, Kuwi.',size=9,color=MUTED)
    fig.text(.045,.121,'Central: Kolami, Naikri, Naiki, Parji, Gadaba.  Kurukh–Malto and Brahui are shown separately: their common northern subgroup is disputed.',size=9,color=MUTED)
    fig.text(.045,.093,'Northern two-meaning cases are Malto fish → star and sprout → infant. Their modern forms differ.',size=10,weight='bold')
    fig.text(.045,.073,'Brahui still records horn/tusk, one, two, three and a questioned inside comparison. These single meanings appear in the full atlas.',size=9.3)
    fig.text(.045,.047,'Same spelling is not a historical sound law. Unrecorded is not absent. A group credit means at least one studied language, not every member.',size=9,color=MUTED)
    fig.text(.045,.027,'Classification: Krishnamurti 2003 pp.19–20; northern caveat: Kobayashi 2020 pp.467–468. Existing lexical matrix unchanged. 20 November 2026.',size=8,color=MUTED)
    for ext in ['png','svg']:fig.savefig(out/f'indus_language_overlap.{ext}',dpi=160,facecolor=BG)
    plt.close(fig)
    # Every semantic claim by all 22 languages; no clipped titles or seven-language selection.
    fig=plt.figure(figsize=(24,26),facecolor=BG)
    fig.text(.035,.974,'Every proposed meaning, in every studied language',size=27,weight='bold')
    fig.text(.035,.954,'67 claims = 48 two-meaning connections + 19 single meanings/numerals • existing dictionary-family and language-specific sense checks',size=12,color=MUTED)
    ax=fig.add_axes([.025,.14,.95,.765]);ax.set_xlim(0,33);ax.set_ylim(67.8,-5.2);ax.axis('off')
    start=11.8;step=.92;cols={l:start+i*step for i,l in enumerate(displayed)}
    for gi,g in enumerate(groups):
        xx=[cols[l] for l in g['languages']]
        ax.add_patch(Rectangle((xx[0]-.43,-4.8),xx[-1]-xx[0]+.86,1.05,color=HEADERS[gi],alpha=.18,lw=0))
        ax.text((xx[0]+xx[-1])/2,-4.1,g['column_label'],ha='center',va='center',size=9 if len(xx)<3 else 11,weight='bold')
        for l in g['languages']:ax.text(cols[l],-1.3,l,rotation=60,ha='left',va='bottom',size=9)
    for k,c in enumerate(claims):
        if k%2==0:ax.add_patch(Rectangle((0,k-.44),32.8,.9,facecolor='#eeeee7',edgecolor='none'))
        draw_glyph(ax,c['sign'],.4,k,fp,cmap)
        ax.text(1.0,k,c['sign'],size=9,weight='bold',va='center')
        label=c['title']
        if c['id']=='S060':label='inside / within [suffix not established]'
        elif c['kind'] not in ('bridge','polysemy'):label+=' [single meaning]'
        ax.text(2,k,label,size=10,va='center')
        for l in displayed:
            r=idx[c['id'],l];a_yes=r['meaning_a']=='True';b_yes=r['meaning_b']=='True'
            co=SAME if r['strict_complete']=='True' else BOTH if r['both_meanings']=='True' else FIRST if a_yes else SECOND if b_yes else NONE
            ax.scatter([cols[l]],[k],s=35,color=co,linewidths=0)
    legends=[(NONE,'Neither checked meaning\nrecorded in this family'),(FIRST,'Picture / first\nmeaning only'),
             (SECOND,'Intended second\nmeaning only'),(BOTH,'Both meanings;\nforms differ'),(SAME,'Both meanings;\nsame written form')]
    for j,(co,label) in enumerate(legends):
        x=.04+j*.19;fig.add_artist(Circle((x,.11),.004,transform=fig.transFigure,color=co));fig.text(x+.01,.104,label,size=11,linespacing=1.5)
    fig.text(.035,.067,'Single-meaning and numeral rows test only the first meaning. Blank source evidence never establishes that a language lacks a word.',size=11,color=MUTED)
    fig.text(.035,.047,'Kannada is grouped with Tamil and Malayalam in South I. Telugu, Gondi, Kui and Kuwi are in South II. Kolami and Parji are Central.',size=11)
    fig.text(.035,.028,'These are existing modern dictionary attestations, not inferred ancestral forms. Regular historical sound correspondences and independent Indus meanings remain to be tested.',size=10,color=MUTED)
    fig.text(.035,.012,'Conventional classification: Krishnamurti 2003; Kurukh–Malto/Brahui caveat: Kobayashi 2020. Glyph outlines are from the repository font. All labels are proposed English meanings.',size=9,color=MUTED)
    for ext in ['png','svg']:fig.savefig(out/f'indus_all_signs.{ext}',dpi=145,facecolor=BG)
    plt.close(fig)
    for p in out.glob('*.svg'):p.write_text('\n'.join(line.rstrip() for line in p.read_text().splitlines())+'\n')
    text=['# What the proposed signs are claimed to mean','',
          'These are hypotheses from the source key. A picture word and an intended word are not established translations. Group credits require both meanings within one individual language.','',
          '| Sign ID | Picture / first proposed meaning | Intended proposed meaning | Languages documenting both |',
          '| --- | --- | --- | --- |']
    for c,rec in zip(claims,semantics):
        if c['kind'] not in ('bridge','polysemy'):continue
        text.append('| '+' | '.join([c['sign'],rec['proposed_picture_or_first_meaning'],rec['proposed_intended_meaning'],rec['languages_with_both_meanings'] or 'Not established in the checked records'])+' |')
    text+=['','## Single meanings and numerals','',
           '| Sign ID | Proposed meaning | Languages with the checked family and sense |','| --- | --- | --- |']
    for c in claims:
        if c['kind'] in ('bridge','polysemy'):continue
        ls='; '.join(l for l in displayed if idx[c['id'],l]['target_meaning']=='True')
        text.append('| '+' | '.join([c['sign'],c['title'],ls or 'Not established in the checked records'])+' |')
    text+=['','Full sense alternatives, cited etymological entries and same-form results: [semantics_catalogue.csv](results/semantics_catalogue.csv).','',
           'An unrecorded pair is not proof of word loss. Matching modern spelling is not a reconstruction of a Harappan pronunciation.']
    (BASE/'semantics.md').write_text('\n'.join(text)+'\n')
    metadata=dict(matrix_sha256=hashlib.sha256((BASE/'results/language_by_claim.csv').read_bytes()).hexdigest(),
        classification_sha256=hashlib.sha256((BASE/'classification.json').read_bytes()).hexdigest(),
        font_sha256=hashlib.sha256(a.font.read_bytes()).hexdigest(),languages=displayed,
        primary_connections=48,all_claims=67,old_display_withdrawn=True)
    (BASE/'results/graphic_revision.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print('Rendered corrected 48-connection subgroup chart and 67-by-22 atlas with full English semantics.')

if __name__=='__main__':main()
