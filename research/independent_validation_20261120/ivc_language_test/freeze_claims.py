"""Freeze the existing IVC hypotheses; no new sign meanings are supplied here."""
import csv
import hashlib
import json
from pathlib import Path

BASE=Path(__file__).resolve().parent
REPO=BASE.parents[2]
claims=[]


def add(sign,title,a,b,ae,be,kind='bridge',note=''):
    claims.append(dict(id='S'+sign,sign=sign,title=title,a=a.split('|'),b=b.split('|'),
        a_entries=ae.split(),b_entries=be.split(),kind=kind,note=note))


# Each meaning and entry follows the frozen master or its cited Key reports.
# Two different etyma can support a rebus; single-entry polysemy is separate.
add('740','jar → house','jar|pot|vessel','house|home|abode|family|lineage','1651','1655')
add('700','bowl / hollow → measure','bowl|earthen pot|hollow','measure|capacity','9 308','9 295')
add('400','comb → small / junior','comb|disentangle','small|little|young','2497','2495')
add('220','fish → star','fish','star|constellation|asterism','4885','4876')
add('520','spear → chief','spear|lance|dart|javelin','chief|ruler|king|hero','5536','5545')
add('390','tree → sew / weave','tree|plant|shrub','sew|stitch|weave|plait','3474','3473')
add('861','eye / sight → weight / property','eye|sight|see','weight|fraction|property|possession','1159 1443','1444')
add('820','wheel → quarter / leg','wheel|cart','quarter|leg|foot','1483','1479')
add('320','step / ladder → ration / measure','step|stair|ladder','ration|measure|allowance|capacity|weight','3850','3849')
add('590','basket / plait → bale / load','basket|plait|braid','sack|load|bale|bundle','4927','5037')
add('615','loom frame → field plot','weaver|loom|reed','field|ridge|land|beds','48','49')
add('705','threshing floor → vessel / ship','threshing|field|floor','ship|vessel|boat','1376','1305')
add('176','sit / remain → tribute','sit|remain|abide','tax|tribute|duty|payment','480','521')
add('090','man → manager / ruler','man|male|husband|servant','rule|manage|control','399','5157')
add('233','split → dawn / light','crack|split|burst','dawn|daybreak|dawning|day','5473','5475')
add('415','fork / branch → seize','fork|prong|branch','seize|grasp|catch|control','1325','1326')
add('920','moon ↔ month','moon','month','3213','3213',kind='polysemy')
add('407','branch → cloth','branch','cloth|weaver','2200','2198')
add('806','stalk → millet','stalk|stem','millet|grain','1454','1242')
add('798','shell → bind / build house','shell','bind|tie|build|house','3544','3536',note='The separately cited claw/grasp entry 444 is recorded as an alternative lexical anchor, not silently combined with shell.')
add('255','crocodile → first / principal','crocodile','first|beginning|principal|capital','4952','4950')
add('840','pair ↔ join','pair|couple','join|unite|union|agree','457','457',kind='polysemy')
add('760','sprout ↔ young / child','sprout|shoot|tendril','young|child|infant','1791 2149','1791 2149',kind='polysemy')
add('368','flag → give / grant','flag|banner','give|grant','2049','2053')
add('690','tie ↔ bundle / building','tie|bind|fasten','bundle|packet|building|store','1147','1147',kind='polysemy')
add('550','waist / middle → district','waist|middle|centre|center','district|country|province|locality','3584','3638')
add('892','bow → sell','bow','sell|sale|price','5422','5421')
add('140','mother / lady ↔ goddess','mother|lady|matron','goddess','183','183',kind='polysemy')
add('154','carrying pole → guard','carrying pole|pole|yoke','guard|watch|preserve|protect|shelter','1417','1416')
add('142','staff → smith','staff|stick|rod','smith|iron','2237','2133')
add('503','mountain → garland','mountain|hill','garland|necklace','4742','4827')
add('440','corner → vessel','corner|nook|lane','vessel|pot|pan|cup','4898','4899')
add('435','hook → attendant','hook|goad','servant|watchman|attendant|messenger','3547','3546')
add('845','line → tax','line|stripe|streak|draw|write','tax|impost|duty|toll|levy','5263','5266')
add('850','eye → copper','eye|sight','copper|bronze|brazier','1159','1402',note='The proposal used ASCII equivalence; strict normalization retains ṇ versus ṉ.')
add('717','foot ↔ servant','foot|footprint','servant|slave|servitude','72','72',kind='polysemy')
add('413','grain → tax / cut','grain|paddy|rice|ear','tax|duty|cut|reap','215','216 212')
add('350','fence → watchman','fence|yard|pound|enclosure','watchman|servant|messenger','3485','3546')
add('460','shoot → garland','shoot|branch','garland|wreath|neckrope','1353','1184')
add('482','mountain → king','mountain|hill','king|emperor|chief|leadership','2178','2177')
add('480','point → vessel','point|sharp|tip','vessel|capacity|measure','3314','3385')
add('335','frame → pot','frame','pot|vessel|pan','2304','2306',note='The source also offers double-basket koḍame, entry 2047, as a literal alternative.')
add('540','drum ↔ capacity measure','drum','measure|capacity','4032','4032',kind='polysemy')
add('630','cage → assemble / store','cage|coop|nest|pen|hive','assemble|join|store|stored|together','1883','1882')
add('171','hang ↔ weigh','hang|suspend|suspended','weigh|weight|balance|scales','3376','3376',kind='polysemy')
add('831','blade → grain','blade|weapon|arrow|weaver','grain|paddy','237','255')
add('165','bend / snail → cauldron','bend|curve|hump|snail','cauldron','1927','1928')
add('104','leap → collect / levy','leap|skip|jump|stride|dance','collect|levy|recover','3158','3054')
# Literal roots distinguish lexical inheritance from complete rebus survival.
add('923','horn / tusk','horn|tusk','', '4720','',kind='literal')
add('500','sail','sail','', '4088','',kind='literal')
add('790','circle / bangle','circle|bangle|bracelet','', '5313','',kind='literal')
add('215','rice','rice','', '215','',kind='literal')
add('854','sesame','sesamum|sesame','', '854','',kind='literal')
add('711','vessel / capacity measure','measure|capacity|dish|boat','', '5315','',kind='literal')
add('575','capacity measure kōṭṭai','measure|capacity','', '2208','',kind='literal')
add('235','light component of roofed fish','light|bright|brightness','', '1016','',kind='literal')
add('060','inside component / locative','inside|interior|within','', '698','',kind='literal',note='Lexical inside is tested; -iṉ genitive and an actual locative suffix require a grammatical test and are not inferred from this word.')
for sign,number,eid in [('001','one','990'),('002','two','474'),('003','three','5052'),('004','four','3655'),
                         ('005','five','2826'),('006','six','2485'),('007','seven','910'),
                         ('025','nine','1025'),('028','ten','3918'),('055','twelve','3918')]:
    add(sign,'numeral '+number,number,'',eid,'',kind='numeral',note='Eight uses the ordinary numeral family eṭṭu; proposed *eṇ is separately documented as an unresolved stem interpretation.' if number=='eight' else '')


def main():
    master=list(csv.DictReader((REPO/'work_data/key6a/master_lexicon_after_key6a.csv').open()))
    by_sign={r['sign']:r for r in master}
    for c in claims:
        c['proposal_root']=by_sign[c['sign']]['root_or_gloss']
        c['source_note']=by_sign[c['sign']]['evidence_note']
        c['source_intact_tokens']=int(by_sign[c['sign']]['intact_4163_tokens'])
        c['scope']='fixed original concept/etymon claim, not independently established sign meaning'
    inputs=['work_data/key6a/master_lexicon_after_key6a.csv','jobs/out/key2a_rebus_lock.md',
            'work_data/key4b/test4b1_top30_sign_table.csv','work_data/key5a/trackA_per_sign_bridges.csv',
            'work_data/key6a/trackA_per_sign_bridges.csv']
    obj=dict(source_commit='727dfd411a4faa44d193d204757540d45c7b139b',
        input_sha256={p:hashlib.sha256((REPO/p).read_bytes()).hexdigest() for p in inputs},
        design='Retrospective IVC-specific portability analysis. Primary inventory fixes the source meaning pairs and etyma. No language is credited for a generic same-meaning replacement from a different family.',
        excluded=[dict(sign='008',proposal_root='*eṇ',reason='Zero intact tokens and no glyph in the source font. Ordinary eight eṭṭu (784) does not verify the proposed eṇ stem; excluded rather than credited through a replacement.')],
        claims=claims)
    (BASE/'claims.json').write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
    print('Froze',len(claims),'IVC cases;',sum(c['kind'] in ('bridge','polysemy') for c in claims),'complete connections.')


if __name__=='__main__':main()
