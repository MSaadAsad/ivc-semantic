"""Semantic traps, source units, all-language coverage and interpretation guards."""
import json

import open_rebus as O
import portability_contact as P


def main():
    assert not P.matched(P.heads('mouth of a pot'),['pot'])
    assert not P.matched(P.heads('ear of corn'),['ear'])
    assert not P.matched(P.heads('potter'),['pot'])
    assert not P.heads('see DEDR5354')
    assert P.matched(P.heads('doorway, entrance, gate, place, king\'s court'),['gate'])==['gate']
    assert P.matched(P.heads('doorway, entrance, gate, place, king\'s court'),["king's court"])==["king's court"]
    # A synthetic real two-sense word is recovered inside one language.
    row=dict(language='synthetic',headword='kāta',gloss='gate; royal court',source='synthetic',row=1,entry='1',flag='unmarked',citation='',notes='')
    assert set(P.form_rows([row],['gate']))&set(P.form_rows([row],['royal court']))=={'kata'}
    assert set(P.form_rows([row],['gate']))&set(P.form_rows([dict(row,headword='pāta')],['royal court']))==set()
    summary=json.loads((O.OUT/'contact_portability_summary.json').read_text())
    assert summary['source_rows']==88249 and summary['lexical_records']==88250
    assert summary['languages']==22 and summary['case_language_cells']==176
    assert sum(summary['language_counts'].values())==summary['lexical_records']
    detail=O.R.read(O.OUT/'contact_portability_by_language.csv')
    assert len(detail)==176 and {r['language'] for r in detail}==set(P.D.LANGS)
    assert len({(r['case'],r['language']) for r in detail})==176
    assert {r['case'] for r in detail}=={r[0] for r in P.CASES}
    assert O.R.read(O.OUT/'contact_same_meaning_form_witnesses.csv')==[]
    reviewed=O.R.read(O.OUT/'contact_portability_review.csv')
    accepted=[r for r in reviewed if r['review_decision']=='accepted_shared_metonymy']
    assert len(accepted)==3 and {r['picture_entry'] for r in accepted}=={'5354'}
    assert any(r['review_decision']=='rejected_part_of_speech_error' for r in reviewed)
    ledger=O.R.read(O.OUT/'nonoverlap_loan_research_ledger.csv')
    assert len(ledger)==8 and all(r['borrowing_demonstrated']=='False' for r in ledger)
    assert {r['case'] for r in ledger if r['Dravidian_reviewed_exact_languages']}=={'gate_court'}
    print('PASS: lexical-head traps and recovery,88,249 source rows/88,250 corrected records,22 languages/176 cells, original witnesses and verb-stick rejection, one shared metonymy family, zero same-meaning form contacts or claimed loans. Colab0.')


if __name__=='__main__':main()
