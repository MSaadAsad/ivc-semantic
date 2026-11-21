import csv,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
BASE=Path(__file__).resolve().parent
def main():
    bg='#f7f5ef';ink='#163640';plt.rcParams.update({'font.family':'DejaVu Sans','text.color':ink,'axes.labelcolor':ink,'xtick.color':ink,'ytick.color':ink})
    fig=plt.figure(figsize=(15,7.5),facecolor=bg)
    fig.text(.05,.93,'A known-answer test exposed a scoring asymmetry',fontsize=23,weight='bold')
    fig.text(.05,.88,'Three Sumerian rebus groups • the repo’s existing seven-family dictionary engine',fontsize=12,color='#586a70')
    ax=fig.add_axes([.08,.27,.33,.49],facecolor=bg)
    vals=[1,2,3];labels=['Original phonetic\nrule','Original rule +\npolysemy','Cluster filter\nremoved*']
    ax.bar(range(3),vals,color=['#6199ba','#e3b562','#3e9984'],width=.6)
    for i,v in enumerate(vals):ax.text(i,v+.08,f'{v}/3',ha='center',weight='bold',size=14)
    ax.set_xticks(range(3),labels);ax.set_ylim(0,3.6);ax.set_yticks([0,1,2,3]);ax.set_ylabel('Known rebus cases detected');ax.set_title('Reading recovery',loc='left',weight='bold',pad=16)
    ax.spines[['top','right']].set_visible(False)
    rows=[r for r in csv.DictReader((BASE/'results/edge_eligibility.csv').open()) if r['mode']=='phon_exact']
    ax=fig.add_axes([.58,.27,.35,.49],facecolor=bg)
    ys=list(range(len(rows)));pct=[100*int(r['eligible_distinct_cluster_edges'])/int(r['total_homophone_edges']) for r in rows]
    ax.barh(ys,pct,color=['#6199ba' if r['language']=='Dravidian' else '#69ad9d' for r in rows],height=.6)
    ax.set_yticks(ys,[r['language'] for r in rows]);ax.invert_yaxis();ax.set_xlim(0,112);ax.set_xlabel('Homophone pairs allowed by the cluster filter (%)');ax.set_title('Same rule, unequal opportunity to score',loc='left',weight='bold',pad=16)
    for y,p,r in zip(ys,pct,rows):ax.text(p+1.5,y,f'{p:.1f}%',va='center',size=10)
    ax.spines[['top','right']].set_visible(False)
    fig.text(.05,.15,'Order check: reversing identical Sumerian input records changes the original strict score from 1/3 to 0/3.',fontsize=12,weight='bold')
    fig.text(.05,.105,'*Removing the filter is a diagnostic, not a validated etymological repair. Sumerian ranks first in the original-order pilot; Dravidian does not win.',fontsize=10,color='#586a70')
    fig.text(.05,.068,'The exact phonetic channel has zero eligible homophone pairs for Akkadian and Burushaski. Polysemy is a separate channel.',fontsize=10,color='#586a70')
    fig.text(.05,.03,'Small illustrative pilot, not an Indus decipherment. Sources: existing lexica and Key2A engine; Woods, Visible Language p.43; Parpola 2010 p.13.',fontsize=9,color='#586a70')
    (BASE/'figures').mkdir(exist_ok=True);fig.savefig(BASE/'figures/benchmark_diagnostics.png',dpi=150,facecolor=bg);plt.close(fig)
if __name__=='__main__':main()
