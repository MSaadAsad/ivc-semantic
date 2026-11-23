"""Render released Elamite results with coverage and the meaning-shuffle baseline."""
import html
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import run as R


def main():
    s = json.loads((R.OUT/'summary.json').read_text())
    d = s['primary_direct']; b = s['primary_rebus']
    null = np.array([float(r['similarity']) for r in R.read(R.OUT/'direct_primary_null.csv')])
    plt.rcParams.update({'font.family':'DejaVu Sans','svg.fonttype':'none','svg.hashsalt':'ivc-elamite-check'})
    fig, axes = plt.subplots(1,2,figsize=(13,4.7),gridspec_kw={'width_ratios':[1,1.5]})
    fig.patch.set_facecolor('#f6f4ef')
    a = axes[0]
    covered = [d['covered'],b['both_covered']]
    missing = [d['claims']-d['covered'],b['claims']-b['both_covered']]
    a.barh([1,0],covered,color='#397b75',label='Meanings covered')
    a.barh([1,0],missing,left=covered,color='#deded7',label='Missing coverage')
    for y,c,m in zip([1,0],covered,missing):
        a.text(c/2,y,f'{c}',va='center',ha='center',color='white',weight='bold')
        a.text(c+m/2,y,f'{m}',va='center',ha='center',color='#394d50')
    a.set_yticks([1,0],['Word / meaning\nclaims','Picture / meaning\npairs'])
    a.set_xlabel('Number of fixed claims')
    a.set_xlim(0,70)
    a.set_title('How much can we actually check?',loc='left',pad=18)
    a.legend(loc='upper left',bbox_to_anchor=(0,-.22),frameon=False,ncol=1)
    ax = axes[1]
    ax.hist(null,bins=30,color='#a9bbb8',edgecolor='white')
    ax.axvline(d['mean_similarity'],color='#b76530',lw=2.5,label=f'Actual: {d["mean_similarity"]:.3f}')
    ax.axvline(d['similarity_null_mean'],color='#374f55',lw=1.7,ls='--',label=f'Reassigned meanings, mean: {d["similarity_null_mean"]:.3f}')
    ax.set_title('Are the spellings closer than chance?',loc='left',pad=18)
    ax.set_xlabel('Mean spelling similarity on the 34 covered claims')
    ax.set_ylabel('Number of reassignment trials')
    ax.legend(frameon=False,fontsize=9)
    ax.text(.02,.04,f'p = {d["similarity_p"]:.4f} before correction\nA score this high is common in the control trials.',transform=ax.transAxes,fontsize=10,
            bbox=dict(facecolor='#f6f4ef',edgecolor='none',alpha=.9,pad=3))
    for ax in axes:
        ax.set_facecolor('#f6f4ef')
        ax.spines[['top','right']].set_visible(False)
    fig.suptitle('Archived form-affinity comparison: not an Elamite–Indus language test',x=.04,ha='left',fontsize=15,weight='bold')
    fig.subplots_adjust(left=.16,right=.98,top=.81,bottom=.25,wspace=.40)
    svg = R.OUT/'elamite_check.svg'
    fig.savefig(svg,metadata={'Date':None},facecolor=fig.get_facecolor())
    svg.write_text(('\n'.join(x.rstrip() for x in svg.read_text().splitlines())+'\n').replace("'DejaVu Sans'", "'DejaVu Sans', Arial, sans-serif"))
    fig.savefig(R.OUT/'elamite_check.png',dpi=160,facecolor=fig.get_facecolor())
    plt.close(fig)
    e = lambda x:html.escape(str(x))
    direct = [r for r in R.read(R.OUT/'all_direct_results.csv') if r['pool']=='unflagged' and r['mode']=='phon']
    pairs = [r for r in R.read(R.OUT/'all_pair_results.csv') if r['pool']=='unflagged' and r['mode']=='phon' and r['panel']=='fixed48']
    dr = ''.join(f'<tr><td>{e(r["sign"])}</td><td>{e(r["title"])}</td><td>{e(r["proposed_root"])}</td><td>{e(r["best_word"]) or "Missing coverage"}</td><td>{e(r["best_head"])}</td><td>{e(r["best_periods"])}</td><td>{float(r["best_similarity"]):.3f}</td></tr>' for r in direct)
    pr = ''.join(f'<tr><td>{e(r["sign"])}</td><td>{e(r["title"])}</td><td>{r["picture_entries"]}</td><td>{r["target_entries"]}</td><td>{"Both meanings covered; no equal-form pair" if r["both_covered"]=="True" else "Missing one or both meanings"}</td></tr>' for r in pairs)
    pool = ''.join(f'<tr><td>{e(r["pool"])}</td><td>{r["unique_form_head_pairs"]}</td><td>{r["unique_heads"]}</td></tr>' for r in s['pool_sizes'])
    rival = ''.join(f'<tr><td>{e(r["language"])}</td><td>{r["covered"]}</td><td>{float(r["mean_similarity"]):.3f}</td><td>{r["exact_hits"]}</td><td>{r["dictionary_form_head_pairs"]}</td></tr>' for r in R.read(R.OUT/'rival_dictionary_summary.csv') if r['scope']=='common_coverage')
    page = f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Structured Elamite vocabulary check</title><style>body{{margin:0;background:#f6f4ef;color:#243c40;font:16px/1.6 system-ui,sans-serif}}main{{max-width:1200px;margin:auto;padding:28px}}h1{{font-size:35px;line-height:1.2}}h2{{margin-top:32px}}.finding{{background:#e3eae5;border-left:5px solid #397b75;padding:18px}}.limit{{background:#fff0dc;border-left:5px solid #af7737;padding:18px}}.scroll{{overflow:auto}}table{{border-collapse:collapse;background:white;width:100%}}th,td{{border:1px solid #d4dcd6;padding:10px;text-align:left;vertical-align:top}}th{{background:#2d484b;color:white}}img{{width:100%;height:auto}}a{{color:#176474}}</style><main>
<h1>Could Elamite explain the Indus inscriptions?</h1><p>22 November 2026 · Dataset coverage and a restricted rebus check. Scope corrected after the user's clarification.</p>
<p><b>New direct sequence experiment:</b> <a href="concordance.html">Elamite-style written-agreement prediction</a> uses raw Indus sequences without proposed words or meanings. This page preserves the earlier dictionary work and its scope correction.</p>
<div class="finding"><b>This extension does not supply a full Elamite–Indus test.</b> An Elamite reading must be allowed to use Elamite words and sounds, without resembling Cúper’s proposed Dravidian pronunciations. His individual meanings are also hypotheses, not independently established translations.</div>
<p><b>The relevant completed component:</b> test whether Elamite can reproduce the particular picture/meaning wordplay proposed in the existing work. Only12/48 principal pairs have both meanings covered; none supplies the specified equal-form bridge. This limited result does not exclude an Elamite reading of Indus.</p>
<p><b>Correction to the earlier framing:</b> comparing Cúper’s Dravidian forms with Elamite spellings answers a different question. The34-claim comparison and its p-value are archived below, not presented as an Elamite–IVC language test. Elamite–Dravidian historical sound correspondences are not a prerequisite for testing Elamite as the inscription language.</p>
<div class="limit"><b>Missing meanings are not failed translations.</b> Only {b['both_covered']} of the 48 main picture/meaning pairs have both concepts represented under the specified whole-head rule. None supplies the proposed equal-form wordplay; the target-reassignment baseline is also zero. This part has little discriminating power. Old-Elamite period labels are not exact Indus-period dates.</div>
<h2>The usable dataset</h2><p>Ten pinned source files supply 10,438 rows; the admitted common-vocabulary categories supply 8,184. Readable-form/head filtering retains 4,158 rows. Source cognate flags are excluded from the main pool; “unflagged” does not certify an indigenous etymology. English hints are mostly in the source’s morphology column. Personal/place/divine names, damaged forms and logograms are excluded from this lexical screen.</p>
<div class="scroll"><table><thead><tr><th>Pool</th><th>Distinct form/head pairs</th><th>Distinct lexical-head sets</th></tr></thead><tbody>{pool}</tbody></table></div>
<p>These are spellings and lexical heads, not thousands of independent roots. The October 2025 public snapshot is cited by the 2026 dictionary abstract; publication of every promised 2026 annotation was not assumed.</p>
<h2>Elamite vocabulary is allowed to differ</h2><p>The release lists <b>a-a-in “house”</b> (N:4, nE), <b>da-la “tax”</b> (N:1093, nE), and <b>su-un-ki-ir “king-SG”</b> (V:1505, mE). If an Indus sign had one of these meanings in Elamite, the Elamite form could be entirely different from a proposed Dravidian reading. These dictionary entries do not themselves assign that meaning to an Indus sign.</p>
<p>Period key: oE = Old Elamite, mE = Middle Elamite, nE = Neo-Elamite, achE = Achaemenid Elamite. Other source codes remain as recorded. SG means singular.</p>
<h2>Archived off-target comparison: 67 proposed forms</h2><p>This spelling comparison is not evidence about whether Indus encodes Elamite. Its score is normalized character-edit similarity; it is not translation accuracy. Of67 claims,34 have covered target meanings; mean similarity0.210 versus0.205 under meaning reassignment (unadjusted p={d['similarity_p']:.4f}). <a href="elamite_check.svg">Archived affinity figure</a>. All rows are retained for inspection.</p><div class="scroll"><table><thead><tr><th>Sign</th><th>Fixed claim</th><th>Proposed Dravidian form</th><th>Closest eligible Elamite spelling(s)</th><th>Source lexical head</th><th>Recorded periods</th><th>Similarity</th></tr></thead><tbody>{dr}</tbody></table></div>
<h2>All 48 principal picture/meaning pairs</h2><p>The full release also scores the other five overlapping panels, for 178 formulations in total. These are not 178 independent words. Counts below are form/head entries covering a meaning, not independent etyma.</p><div class="scroll"><table><thead><tr><th>Sign</th><th>Proposed wordplay</th><th>Picture entries</th><th>Target entries</th><th>Result</th></tr></thead><tbody>{pr}</tbody></table></div>
<h2>Archived controls for the off-target form comparison</h2><div class="scroll"><table><thead><tr><th>Language</th><th>Common covered claims</th><th>Mean similarity</th><th>Exact hits</th><th>Dictionary form/head pairs</th></tr></thead><tbody>{rival}</tbody></table></div><p>This table compares proposed Dravidian forms with dictionary forms and is not an Elamite–IVC test. The pools differ in size and source quality. Neither the raw ranking nor the within-dictionary permutation p-value identifies the Indus language.</p>
<h2>What this adds</h2><p>Earlier repository tests already used Elamite dictionaries and tested proposed Linear-Elamite sound transfer. This extension adds the structured DigitalPasts input, period/borrowing-flag splits and fixed-form/same-meaning affinity controls. The source derives from Hinz–Koch; it is not an independent ancient corpus. No source-verified historical Elamo-Dravidian sound-correspondence test or independent Indus semantic assignment is claimed. All 163 signs are retained in the scope inventory, with untested compounds/allographs distinguished.</p>
<p><a href="../README.md">Interpretation, sources and reproduction</a> · <a href="all_direct_results.csv">Every direct candidate</a> · <a href="all_pair_results.csv">All 178 formulations</a> · <a href="rebus_summary.csv">All rebus sensitivities</a> · <a href="direct_summary.csv">All direct sensitivities</a> · <a href="entry_eligibility.csv">Every source-row exclusion</a> · <a href="all_163_sign_scope.csv">All 163 signs: tested scope</a> · <a href="summary.json">Summary</a> · <a href="rival_dictionary_details.csv">Rival candidate details</a></p>
<p><a href="https://github.com/DigitalPasts/ALP-MEGA2024/tree/3160b20f5cd84b387343d071749bb90419148743/Elamite_materials/EWB-EJSmithFiles">Pinned primary CSV source</a> · <a href="https://dh-daejeon.vercel.app/abs/358?full=1&amp;q=XML">DH2026 dictionary abstract</a></p></main></html>'''
    (R.OUT/'elamite.html').write_text(page)
    print('Rendered Elamite report and scientific figure.')


if __name__ == '__main__':
    main()
