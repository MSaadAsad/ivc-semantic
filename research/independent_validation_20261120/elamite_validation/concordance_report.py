"""Present the direct Indus sequence/marker experiment; no refitting."""
import csv
import html
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BASE=Path(__file__).resolve().parent;OUT=BASE/'results'


def main():
    summary=json.loads((OUT/'concordance_summary.json').read_text())
    with (OUT/'concordance_as_stored_coefficient_curve.csv').open() as f:curve=list(csv.DictReader(f))
    plt.rcParams.update({'svg.fonttype':'none','svg.hashsalt':'ivc-elamite-concordance'})
    fig,ax=plt.subplots(figsize=(10,4.5))
    x=[100*float(r['coefficient']) for r in curve]
    ax.plot(x,[float(r['validation_mean_gain_bits']) for r in curve],label='Internal validation (selects the rule)',color='#a76b32',lw=2)
    ax.plot(x,[float(r['test_mean_gain_bits']) for r in curve],label='New-formula evaluation (diagnostic curve)',color='#347b82',lw=2)
    ax.axhline(0,color='#47595b',lw=1)
    ax.scatter([0],[0],s=60,color='#263e42',zorder=3,label='Selected copying weight: 0%')
    ax.set(xlabel='Prediction weight assigned to copying an earlier marker (%)',ylabel='Gain over baseline (bits/sign)',
           title='The repeated-marker rule was not selected during validation')
    ax.legend(frameon=False,fontsize=9);ax.spines[['top','right']].set_visible(False)
    fig.tight_layout()
    path=OUT/'concordance_curve.svg'
    fig.savefig(path,metadata={'Date':None})
    path.write_text(('\n'.join(l.rstrip() for l in path.read_text().splitlines())+'\n').replace("'DejaVu Sans'","'DejaVu Sans', Arial, sans-serif"))
    plt.close(fig)
    e=lambda v:html.escape(str(v))
    result_rows=''.join(f'<tr><td>{e(r["direction"])}</td><td>{100*r["fitted_copy_coefficient"]:.1f}%</td><td>{r["test"]["formulas"]}</td><td>{r["test"]["predicted_positions"]}</td><td>{r["test"]["copy_opportunities"]}</td><td>{r["test"]["actual_copy_repeats"]}</td><td>{r["test"]["mean_gain_bits_per_predicted_sign"]:.4f}</td></tr>' for r in summary['linear_models'])
    graphics=''.join(f'<tr><td>{e(r["corpus"])}</td><td>{r["plain_plain"]}</td><td>{r["plain_caged"]}</td><td>{r["caged_plain"]}</td><td>{r["caged_caged"]}</td></tr>' for r in summary['graphic_representation']['corpora'])
    with (OUT/'concordance_as_stored_predictions.csv').open() as f:repeats=[r for r in csv.DictReader(f) if float(r['copy_probability'])>0]
    examples=''.join(f'<tr><td>{e(r["sequence"])}</td><td>{int(r["position"])+1}</td><td>{e(r["target"])}</td></tr>' for r in repeats)
    page=f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Direct Elamite-style agreement check on Indus sequences</title><style>body{{margin:0;background:#f6f4ef;color:#263d40;font:16px/1.6 system-ui,sans-serif}}main{{max-width:1150px;margin:auto;padding:28px}}h1{{font-size:34px;line-height:1.25}}h2{{margin-top:32px}}.result{{padding:18px;background:#e3eae5;border-left:5px solid #397b75}}.limit{{padding:18px;background:#fff0dc;border-left:5px solid #b17c38}}.diagram{{padding:20px;text-align:center;background:white;font-size:24px}}.scroll{{overflow:auto}}table{{border-collapse:collapse;width:100%;background:white}}td,th{{border:1px solid #d3dcd6;padding:11px;text-align:left;vertical-align:top}}th{{background:#2d484b;color:white}}img{{width:100%;height:auto}}a{{color:#176474}}code{{overflow-wrap:anywhere}}</style><main>
<h1>Does Elamite-style agreement help predict Indus writing?</h1><p>22 November2026 · Raw sign sequences; no Dravidian words, proposed translations or dictionary-affinity scores.</p>
<div class="result"><b>This particular written-agreement model gained no selected predictive rule.</b> It was fitted on1,373 distinct Lipi formulas and evaluated on183 New formulas absent from Lipi. Internal validation chose zero weight for copying an earlier grammatical marker, so the final predictor is identical to its no-copy baseline.</div>
<h2>The actual linguistic prediction</h2><p>Elamite noun phrases can repeat a grammatical class ending on linked words. A published example is <i>nap-(i)r u-r</i>, “my god.” If an Indus writing system sometimes represented such agreement with an independent recurring marker, an earlier marker should help predict the later one.</p>
<div class="diagram">stem A – <b>marker s</b> – stem B – <b>marker s</b></div><p>The letters are placeholders, not translations of Indus signs. The algorithm searches for repeatable marker positions without assuming any noun means house, king, tax or star. No marker is assigned the Elamite sound r/p/k.</p>
<div class="limit"><b>This is a conditional writing model, not a complete Elamite decipherment.</b> Elamite agreement can be omitted or written with different spellings. Other languages also have agreement. A negative result cannot eliminate every Elamite model, and a positive one would not uniquely identify Elamite.</div>
<h2>Training and evaluation</h2><p>The1,373 Lipi formulas split into1,109 inner-training and264 validation formulas. Fifty-five candidate suffix signs are selected by frequency in inner training. The baseline predicts signs using length, interior/final position, object type and the immediately preceding sign. One extra coefficient controls copying an earlier marker. It is fixed before evaluating New formulas.</p>
<p>Only sequences with at least four numeric-ID signs and no000/ALT/X damage codes are admitted. That is a transcription filter, not proof of physical completeness. Duplicate formulas count once; six New formulas also seen in Lipi are excluded. These data existed in the repo:183 means distinct test patterns, not183 newly excavated objects or independently blind archaeological observations.</p>
<h2>Results</h2><div class="scroll"><table><thead><tr><th>Direction</th><th>Chosen copying weight</th><th>Test formulas</th><th>Predicted positions</th><th>Copy opportunities</th><th>Actual repeats</th><th>Gain, bits/sign</th></tr></thead><tbody>{result_rows}</tbody></table></div>
<p>The primary direction is as stored; reversed order is a diagnostic. <b>Zero gain follows mathematically from choosing zero copying weight.</b> It is not183 separate rejections. The narrow finding is that the additional rule failed to improve validation enough to be selected.</p>
<img src="concordance_curve.svg" alt="Both validation and test prediction gains decline as substantial copying weight is imposed; validation selects0%">
<p>These full-grid curves were added after seeing the zero coefficient and are diagnostic only. At0.5% the primary test curve has a tiny positive0.00287-bit gain while validation is negative. That test-set optimum was not promoted. At5%, validation and test gains are−0.0402 and−0.0268 bits/sign. Every grid point is downloadable.</p>
<h2>Could a smaller set of marker signs work?</h2><p>An exploratory refinement lets Lipi validation choose at most six marker signs and their copying weight, then freezes them before evaluating New. It selects only sign407 from <b>one validation opportunity</b>. The test set contains <b>zero eligible opportunities</b> for that chosen rule. This is an unsupported single-case lead, not a successful Elamite reading. Selection steps and every prediction are retained. This refinement was designed after viewing the first model's results and is not an independently preregistered confirmation.</p>
<h2>Every admissible repeated marker in the primary test</h2><div class="scroll"><table><thead><tr><th>Indus sequence</th><th>Predicted sign position, counting from1</th><th>Earlier marker repeated</th></tr></thead><tbody>{examples}</tbody></table></div><p>For example,095–740–176–740–090 repeats740 after different preceding signs. That alone does not establish that740 is a grammatical suffix or give the inscription an Elamite translation.</p>
<h2>Could agreement be written inside a modified sign?</h2><p>A separate check uses nine published-in-repo graphical decompositions explicitly describing four-small-stroke/line cages, compared across different graphic base families. It admits neither generic brackets nor four-pair enclosures.</p><div class="scroll"><table><thead><tr><th>Corpus</th><th>Plain/plain</th><th>Plain/caged</th><th>Caged/plain</th><th>Caged/caged</th></tr></thead><tbody>{graphics}</tbody></table></div><p>There are no marked test pairs, so this representation cannot be evaluated as a confirmation or refutation. No significance claim is made.</p>
<h2>What this changes</h2><p>We now have a direct test of one Elamite-compatible written mechanism against the actual Indus sequences. It gives no positive support for that representation. It has not produced a reading or decided the Indus language. Existing dictionary, grammar-order, QAP and Linear-Elamite transfer experiments are credited rather than repeated as new results.</p>
<p><a href="../CONCORDANCE.md">Interpretation, sources and reproduction</a> · <a href="concordance_summary.json">Summary</a> · <a href="concordance_formula_membership.csv">Every formula and object key</a> · <a href="concordance_as_stored_predictions.csv">Every primary prediction</a> · <a href="concordance_reversed_predictions.csv">Reversed predictions</a> · <a href="concordance_as_stored_coefficient_curve.csv">Every coefficient</a> · <a href="concordance_graphic_inventory.csv">Admitted graphical rows</a></p>
<p><a href="https://unora.unior.it/bitstream/11574/217200/1/basello2023introduction-elamite.pdf">Basello: primary Elamite grammar source, printed28</a> · <a href="https://www.elamit.net/depot/resources/stolper2004original.pdf">Stolper: grammar source, pp.73–74</a></p></main></html>'''
    for a,b in [('November2026','November 2026'),('on1,373','on 1,373'),('on183','on 183'),('The1,373','The 1,373'),('into1,109','into 1,109'),('and264','and 264'),('no000','no 000'),('repo:183','repo: 183'),('not183','not 183'),('At0.5','At 0.5'),('positive0.00287','positive 0.00287'),('At5%','At 5%'),('are−0.0402','are −0.0402'),('and−0.0268','and −0.0268'),('from1','from 1'),('example,095','example, 095'),('repeats740','repeats 740'),('that740','that 740')]:page=page.replace(a,b)
    (OUT/'concordance.html').write_text(page)
    print('Rendered direct concordance report.')


if __name__=='__main__':main()
