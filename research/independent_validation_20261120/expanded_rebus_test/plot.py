"""Standalone scientific figure: observed counts beside both null distributions."""
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

BASE=Path(__file__).resolve().parent

def main():
    rows=list(csv.DictReader((BASE/'results/summary.csv').open()))
    names=['Dravidian','Sumerian','Munda','Indo-Aryan','Elamite','Akkadian','Burushaski']
    data=np.load(BASE/'results/nulls_and_matrices.npz')
    panels=['fixed48','auto51','legacy12','key4b30','key5a13','key6a24']
    bg='#faf8f2';ink='#183a45'
    plt.rcParams.update({'font.family':'DejaVu Sans','text.color':ink,'axes.labelcolor':ink,
                         'xtick.color':ink,'ytick.color':ink,'font.size':11})
    fig,axes=plt.subplots(1,2,figsize=(15,7),facecolor=bg)
    fig.subplots_adjust(left=.10,right=.97,top=.73,bottom=.25,wspace=.38)
    for ax,panel,title in zip(axes,['fixed48','auto51'],
          ['48 proposed reading pairs','51 automatically assembled picture/domain pairs']):
        ax.set_facecolor(bg)
        rr=[next(r for r in rows if r['panel']==panel and r['language']==l and r['mode']=='phon_exact'
                 and r['gate']=='distinct_entry' and r['channel']=='phonetic_plus_polysemy') for l in names]
        y=np.arange(len(names));obs=[int(r['hits']) for r in rr]
        ax.barh(y,obs,height=.60,color=['#287f7b' if l=='Dravidian' else '#5e8fad' for l in names],alpha=.75)
        pi=panels.index(panel)
        for kind,offset,marker,color in [('domain',-.13,'o','#7d4f21'),('entry_sound',.13,'D','#512d6d')]:
            for j,l in enumerate(names):
                a=data[l+'_'+kind][:,pi,0,1,1];mu=a.mean();lo,hi=np.quantile(a,[.025,.975])
                ax.plot([lo,hi],[j+offset,j+offset],color=color,lw=1.7)
                ax.plot(mu,j+offset,marker=marker,color=color,ms=4)
        for j,v in enumerate(obs):ax.text(v+.55,j+.03,str(v),va='center',weight='bold',
                                       bbox=dict(facecolor=bg,edgecolor='none',pad=.3))
        ax.set_yticks(y,names);ax.invert_yaxis();ax.set_xlim(0,43 if panel=='fixed48' else 33)
        ax.set_xlabel('Meaning pairs matched by the program')
        ax.set_title(title,loc='left',size=13,weight='bold',pad=16)
        ax.spines[['top','right']].set_visible(False)
    fig.text(.05,.94,'Dravidian’s fit survives on selected readings; it does not transfer to the automatic panel',
             size=17,weight='bold')
    fig.text(.05,.875,'Seven dictionary pools • exact normalized sounds + distinct-sense polysemy • cluster filter removed',size=11)
    fig.text(.05,.825,'Bars: observed matches. Circles: target-permutation null. Diamonds: entry-stratified sound null. Lines: central 95% of null counts.',size=10)
    fig.text(.05,.16,'Selected 48: Dravidian 38, Sumerian 11. Dravidian exceeds both nulls (seven-language adjusted p = 0.0007).',size=11,weight='bold')
    fig.text(.05,.105,'Automatic 51: Dravidian 13, Sumerian 14. Neither exceeds both nulls. The original repo already reported a null result here.',size=10)
    fig.text(.05,.065,'9,999 controls per null. Panels overlap and are not independent. Selected meanings remain hypotheses; these are machine matches, not verified readings.',size=9)
    fig.text(.05,.025,'The seven-language primary correction is shown above. Across all 504 sensitivity cells, the smallest Holm-adjusted p is 0.0504 (Monte Carlo resolution floor).',size=9)
    (BASE/'figures').mkdir(exist_ok=True)
    fig.savefig(BASE/'figures/expanded_comparison.png',dpi=160,facecolor=bg)
    fig.savefig(BASE/'figures/expanded_comparison.pdf',facecolor=bg)
    plt.close(fig)

if __name__=='__main__':main()
