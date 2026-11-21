"""Publication graphics with the repository's actual Indus-font outlines."""
import argparse, csv, json, math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch
from matplotlib.font_manager import FontProperties
from analyze import BASE

BG='#f7f5ef';INK='#142e39';MUTED='#586a70'
GROUPS=[['Tamil','Malayalam'],['Kannada','Telugu'],['Brahui','Kurukh','Malto']]
COLORS=['#679bd4','#efbc63','#60bca7']

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--font',type=Path,required=True);a=ap.parse_args()
    fp=FontProperties(fname=a.font)
    from fontTools.ttLib import TTFont
    cmap=TTFont(a.font).getBestCmap()
    plt.rcParams.update({'font.family':'DejaVu Sans','text.color':INK,'font.size':11,'svg.fonttype':'path'})
    claims=json.loads((BASE/'claims.json').read_text())['claims'];by={c['id']:c for c in claims}
    matrix=list(csv.DictReader((BASE/'results/language_by_claim.csv').open()))
    out=BASE/'figures';out.mkdir(exist_ok=True)
    fig=plt.figure(figsize=(18,11),facecolor=BG)
    fig.text(.045,.95,'How the proposed Indus readings overlap',size=28,weight='bold')
    fig.text(.045,.911,'67 representative sign claims • seven languages shown • full vocabulary study: 22 Dravidian varieties',size=13,color=MUTED)
    example={
        'target_meaning':{'100':['S390','S575'],'010':['S440'],'110':['S740','S845'],'101':['S923','S520'],'111':['S220','S060']},
        'both_meanings':{'100':['S615','S390'],'010':['S460'],'110':['S740','S892'],'101':['S760'],'111':['S220']}}
    positions={'100':(-1.65,.9),'010':(1.65,.9),'110':(0,1.58),'101':(-.85,-.45),'011':(.85,-.45),'111':(0,.3),'001':(0,-1.65)}
    bins_out=[]
    for panel,(field,title,desc) in enumerate([
        ('target_meaning','1  Target word family + meaning','67 claims: target sense of rebus, literal word or numeral'),
        ('both_meanings','2  Both meanings within one language','48 proposed connections; sound similarity assessed separately')]):
        ax=fig.add_axes([.035+panel*.49,.275,.465,.55]);ax.set_facecolor(BG)
        ax.set_xlim(-2.8,2.8);ax.set_ylim(-2.7,2.85);ax.set_aspect('equal');ax.axis('off')
        fig.text(.045+panel*.49,.857,title,size=18,weight='bold')
        fig.text(.045+panel*.49,.831,desc,size=9.7,color=MUTED)
        for (x,y),co in zip([(-.83,.53),(.83,.53),(0,-.87)],COLORS):
            ax.add_patch(Circle((x,y),1.64,color=co,alpha=.23,lw=0))
            ax.add_patch(Circle((x,y),1.64,fill=False,edgecolor=co,lw=1.7,alpha=.9))
        ax.text(-1.5,2.43,'Tamil / Malayalam',ha='center',size=11,weight='bold',color='#326593')
        ax.text(1.5,2.43,'Kannada / Telugu',ha='center',size=11,weight='bold',color='#946416')
        ax.text(0,-2.56,'Brahui / Kurukh / Malto',ha='center',size=11,weight='bold',color='#2c7e6b')
        eligible=[c for c in claims if field=='target_meaning' or c['kind'] in ('bridge','polysemy')]
        sets=[{r['claim'] for r in matrix if r['language'] in g and r[field]=='True' and r['claim'] in {c['id'] for c in eligible}} for g in GROUPS]
        bins={key:[] for key in ['100','010','110','101','011','111','001','000']}
        for c in eligible:bins[''.join('1' if c['id'] in s else '0' for s in sets)].append(c['id'])
        for key,(x,y) in positions.items():
            ids=example[field].get(key,[])
            ax.text(x,y+.25,str(len(bins[key])),ha='center',va='center',size=22,weight='bold',color=INK if bins[key] else '#81908b')
            for j,cid in enumerate(ids):
                xx=x+(j-(len(ids)-1)/2)*.52
                ax.text(xx,y-.15,chr(0xe000+int(by[cid]['sign'])),fontproperties=fp,size=31,ha='center',va='center')
                ax.text(xx,y-.48,by[cid]['sign'],size=8,ha='center',color=MUTED)
        ax.text(-2.65,-2.43,f'Outside these sets: {len(bins["000"])}',size=9,color=MUTED)
        for key,ids in bins.items():bins_out.append(dict(measure=field,region=key,count=len(ids),claims='; '.join(ids)))
    fig.text(.045,.247,'Set membership means at least one language in that set; it does not mean every language.',size=11,weight='bold')
    fig.text(.045,.222,'Counts cover all eligible claims. Glyphs illustrate selected cases. Circles are schematic, not proportional to counts.',size=10,color=MUTED)
    cards=[(.045,'BROAD INHERITANCE','“One” and “two” families\nare recorded in all 22 varieties.'),
           (.365,'A NORTHERN-HEAVY RETENTION','Horn: Tamil + Brahui + Kurukh + Malto.\nA useful lead; not northern-exclusive.'),
           (.685,'SOUND CHECK','No strict same-form pair among the 48\nin Brahui, Kurukh or Malto. See caveat below.')]
    for x,head,body in cards:
        fig.add_artist(FancyBboxPatch((x,.101),.29,.091,transform=fig.transFigure,boxstyle='round,pad=0.012,rounding_size=0.01',facecolor='white',edgecolor='#e0e2da',lw=1))
        fig.text(x+.005,.165,head,size=10,weight='bold',color='#2c7468')
        fig.text(x+.005,.122,body,size=10,linespacing=1.5)
    fig.text(.045,.059,'Meaning-pair overlap is not homophony. The northern two-sided cases are Malto fish/star and sprout/infant.',size=10,color=MUTED)
    fig.text(.045,.037,'Modern exact-form matching is conservative; it does not reconstruct Harappan speech. Unattested ≠ absent. These sign meanings remain proposals.',size=9.3,color=MUTED)
    fig.text(.045,.018,'Sources: pinned Jambu/DEDR + northern glossaries • source key 727dfd4 • glyph outlines: repository Indus font • 20 November 2026',size=8,color=MUTED)
    for ext in ['png','svg']:fig.savefig(out/f'indus_language_overlap.{ext}',dpi=170,facecolor=BG)
    plt.close(fig)
    with (BASE/'results/venn_regions.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(bins_out[0]),lineterminator='\n');w.writeheader();w.writerows(bins_out)
    # Full atlas: every selected claim, with individual-language evidence levels.
    ls=['Tamil','Malayalam','Kannada','Telugu','Kurukh','Malto','Brahui'];abbr=['Ta','Ma','Ka','Te','Kur','Mal','Br']
    idx={(r['claim'],r['language']):r for r in matrix}
    fig=plt.figure(figsize=(18,20),facecolor=BG)
    fig.text(.035,.969,'Every tested sign claim',size=27,weight='bold')
    fig.text(.035,.945,'67 representatives • individual languages • fixed word families and language-specific meanings',size=12,color=MUTED)
    for panel in range(2):
        ax=fig.add_axes([.025+panel*.49,.075,.465,.84]);ax.set_xlim(0,14);ax.set_ylim(34.8,-1.5);ax.axis('off')
        for j,lab in enumerate(abbr):ax.text(8.1+j*.8,-.8,lab,ha='center',weight='bold',size=9)
        for k,c in enumerate(claims[panel*34:(panel+1)*34]):
            if k%2==0:ax.add_patch(FancyBboxPatch((0,k-.42),13.9,.92,boxstyle='round,pad=0',facecolor='#eeeee7',edgecolor='none'))
            cp=0xe000+int(c['sign'])
            if cp in cmap:ax.text(.55,k,chr(cp),fontproperties=fp,size=29,ha='center',va='center')
            else:ax.text(.55,k,'—',size=14,ha='center',va='center',color=MUTED)
            ax.text(1.25,k-.05,c['sign'],size=9,weight='bold',va='center')
            label=c['title'].replace(' / ','/').replace('numeral ','')
            if len(label)>35:label=label[:33]+'…'
            ax.text(2.25,k-.05,label,size=8.8,va='center')
            for j,l in enumerate(ls):
                r=idx[c['id'],l]
                color='#d9dfdd'
                if r['target_meaning']=='True':color='#91bad8'
                if c['kind'] in ('bridge','polysemy') and r['both_meanings']=='True':color='#e4bc67'
                if r['strict_complete']=='True':color='#287f6c'
                ax.add_patch(Circle((8.1+j*.8,k-.02),.19,color=color,lw=0))
    legend=[('#d9dfdd','Target sense unrecorded'),('#91bad8','Target family + sense'),('#e4bc67','Both senses; forms differ'),('#287f6c','Both senses + same form')]
    for j,(co,lab) in enumerate(legend):
        x=.04+j*.24;fig.add_artist(Circle((x,.05),.0045,transform=fig.transFigure,color=co));fig.text(x+.01,.0465,lab,size=10)
    fig.text(.035,.023,'Unrecorded is not absent. Exact spelling is not a historical sound law. The key’s zero-token 008 / eṇ extension is excluded; its stem remains unresolved.',size=9,color=MUTED)
    fig.text(.035,.011,'Ta Tamil · Ma Malayalam · Ka Kannada · Te Telugu · Kur Kurukh · Mal Malto · Br Brahui. All other studied varieties appear in the downloadable matrix.',size=8,color=MUTED)
    for ext in ['png','svg']:fig.savefig(out/f'indus_all_signs.{ext}',dpi=150,facecolor=BG)
    plt.close(fig)
    for p in out.glob('*.svg'):p.write_text('\n'.join(line.rstrip() for line in p.read_text().splitlines())+'\n')

if __name__=='__main__':main()
